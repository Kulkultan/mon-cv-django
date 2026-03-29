from io import BytesIO
from xml.sax.saxutils import escape

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import get_language, override

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer

from .models import (
    Certification,
    Education,
    Experience,
    Language,
    Profile,
    Skill,
    UiText,
    format_duration,
)

DEFAULT_UI = {
    'nav_profile': 'Profil',
    'nav_contact': 'Contacts',
    'nav_experiences': 'Expériences',
    'nav_certifications': 'Certifications',
    'nav_education': 'Formation',
    'nav_skills': 'Compétences',
    'nav_languages': 'Langues',
    'section_profile': 'Profil exécutif',
    'section_contact': 'Coordonnées',
    'section_experiences': 'Expériences professionnelles',
    'section_certifications': 'Certifications',
    'section_education': 'Cursus académique',
    'section_skills': 'Compétences clés',
    'section_languages': 'Langues',
    'download_cv': 'Télécharger le CV (PDF)',
    'footer_text': 'Zaddy Wilfried Ghislain LEGRE — Qualiticien QHSE — Abidjan, Côte d’Ivoire',
    'address_label': 'Adresse',
    'total_experience_label': 'Expérience totale',
    'current_label': 'Poste actuel',
    'linkedin_label': 'Profil LinkedIn',
}
DEFAULT_UI_EN = {
    'nav_profile': 'Profile',
    'nav_contact': 'Contact',
    'nav_experiences': 'Experience',
    'nav_certifications': 'Certifications',
    'nav_education': 'Education',
    'nav_skills': 'Skills',
    'nav_languages': 'Languages',
    'section_profile': 'Executive profile',
    'section_contact': 'Contact',
    'section_experiences': 'Professional experience',
    'section_certifications': 'Certifications',
    'section_education': 'Education',
    'section_skills': 'Core skills',
    'section_languages': 'Languages',
    'download_cv': 'Download CV (PDF)',
    'footer_text': 'Zaddy Wilfried Ghislain LEGRE — QHSE Specialist — Abidjan, Côte d’Ivoire',
    'address_label': 'Address',
    'total_experience_label': 'Total experience',
    'current_label': 'Current role',
    'linkedin_label': 'LinkedIn profile',
}

def _get_ui(lang):
    ui = DEFAULT_UI_EN.copy() if lang == "en" else DEFAULT_UI.copy()
    with override(lang):
        for item in UiText.objects.all():
            ui[item.key] = item.text
    return ui


def _get_cv_context(lang):
    with override(lang):
        profile = Profile.objects.first()
        experiences = list(Experience.objects.all())
        certifications = list(Certification.objects.all())
        educations = list(Education.objects.all())
        skills = list(Skill.objects.all())
        languages = list(Language.objects.all())

        total_experience_months = sum(exp.duration_months() for exp in experiences)
        total_experience_display = format_duration(total_experience_months, lang)

        return {
            "profile": profile,
            "experiences": experiences,
            "certifications": certifications,
            "educations": educations,
            "skills": skills,
            "languages": languages,
            "ui": _get_ui(lang),
            "lang": lang,
            "ats_keywords": profile.keywords if profile else [],
            "total_experience_display": total_experience_display,
        }


def _build_pdf_response(context):
    profile = context["profile"]
    experiences = context["experiences"]
    certifications = context["certifications"]
    educations = context["educations"]
    skills = context["skills"]
    languages = context["languages"]
    ui = context["ui"]
    lang = context["lang"]
    ats_keywords = context["ats_keywords"]
    total_experience_display = context["total_experience_display"]

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=f"CV - {profile.full_name if profile else 'Profile'}",
    )

    stylesheet = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "CvTitle",
            parent=stylesheet["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#183A61"),
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "CvSubtitle",
            parent=stylesheet["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#274E7D"),
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "CvBody",
            parent=stylesheet["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=13,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=5,
        ),
        "section": ParagraphStyle(
            "CvSection",
            parent=stylesheet["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=15,
            textColor=colors.HexColor("#183A61"),
            spaceBefore=8,
            spaceAfter=6,
        ),
        "item_title": ParagraphStyle(
            "CvItemTitle",
            parent=stylesheet["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#111827"),
            spaceAfter=2,
        ),
        "meta": ParagraphStyle(
            "CvMeta",
            parent=stylesheet["BodyText"],
            fontName="Helvetica",
            fontSize=8.6,
            leading=11,
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "CvBullet",
            parent=stylesheet["BodyText"],
            fontName="Helvetica",
            fontSize=8.9,
            leading=12,
            textColor=colors.HexColor("#1F2937"),
            leftIndent=9,
            firstLineIndent=-6,
            spaceAfter=2,
        ),
        "footer": ParagraphStyle(
            "CvFooter",
            parent=stylesheet["BodyText"],
            alignment=TA_CENTER,
            fontName="Helvetica",
            fontSize=8,
            textColor=colors.HexColor("#6B7280"),
        ),
    }

    def text_or_empty(value):
        return escape(str(value)) if value else ""

    def add_section(story, title):
        story.append(Spacer(1, 4))
        story.append(Paragraph(text_or_empty(title), styles["section"]))
        story.append(HRFlowable(color=colors.HexColor("#D7DEE8"), thickness=0.6, spaceAfter=6))

    story = []

    if profile:
        story.append(Paragraph(text_or_empty(profile.full_name), styles["title"]))
        if profile.headline:
            story.append(Paragraph(text_or_empty(profile.headline), styles["subtitle"]))
        if profile.bio:
            story.append(Paragraph(text_or_empty(profile.bio), styles["body"]))

        phone_label = "Phone" if lang == "en" else "Téléphone"
        contact_parts = []
        if profile.email:
            contact_parts.append(f"Email: {text_or_empty(profile.email)}")
        if profile.phone:
            contact_parts.append(f"{text_or_empty(phone_label)}: {text_or_empty(profile.phone)}")
        if profile.address:
            contact_parts.append(f"{text_or_empty(ui['address_label'])}: {text_or_empty(profile.address)}")
        if profile.linkedin_url:
            contact_parts.append(f"LinkedIn: {text_or_empty(profile.linkedin_url)}")
        if contact_parts:
            story.append(Paragraph(" | ".join(contact_parts), styles["meta"]))

        summary_parts = [f"{text_or_empty(ui['total_experience_label'])}: {text_or_empty(total_experience_display)}"]
        if experiences:
            summary_parts.append(f"{text_or_empty(ui['section_experiences'])}: {len(experiences)}")
        if educations:
            summary_parts.append(f"{text_or_empty(ui['section_education'])}: {len(educations)}")
        story.append(Paragraph(" | ".join(summary_parts), styles["meta"]))

        if ats_keywords:
            story.append(
                Paragraph(
                    f"<b>ATS / LinkedIn / Recruiters:</b> {text_or_empty(', '.join(ats_keywords))}",
                    styles["body"],
                )
            )

    add_section(story, ui["section_experiences"])
    for exp in experiences:
        meta_parts = [text_or_empty(exp.company)]
        if exp.period_display:
            meta_parts.append(text_or_empty(exp.period_display))
        if exp.location:
            meta_parts.append(text_or_empty(exp.location))
        if exp.duration_display:
            meta_parts.append(text_or_empty(exp.duration_display))
        if exp.is_current:
            meta_parts.append(text_or_empty(ui["current_label"]))

        exp_block = [
            Paragraph(text_or_empty(exp.title), styles["item_title"]),
            Paragraph(" | ".join(part for part in meta_parts if part), styles["meta"]),
        ]
        for item in exp.highlight_items:
            exp_block.append(Paragraph(f"<b>{text_or_empty(item)}</b>", styles["body"]))
        for point in exp.description_points:
            exp_block.append(Paragraph(f"- {text_or_empty(point)}", styles["bullet"]))
        exp_block.append(Spacer(1, 4))
        story.append(KeepTogether(exp_block))

    if certifications:
        add_section(story, ui["section_certifications"])
        story.append(Paragraph(text_or_empty(", ".join(cert.name for cert in certifications if cert.name)), styles["body"]))

    if educations:
        add_section(story, ui["section_education"])
        for edu in educations:
            edu_parts = [text_or_empty(edu.school)]
            if edu.period_display:
                edu_parts.append(text_or_empty(edu.period_display))
            if edu.location:
                edu_parts.append(text_or_empty(edu.location))
            story.append(
                KeepTogether(
                    [
                        Paragraph(text_or_empty(edu.degree), styles["item_title"]),
                        Paragraph(" | ".join(part for part in edu_parts if part), styles["meta"]),
                        Spacer(1, 2),
                    ]
                )
            )

    if skills:
        add_section(story, ui["section_skills"])
        story.append(Paragraph(text_or_empty(", ".join(skill.name for skill in skills if skill.name)), styles["body"]))

    if languages:
        add_section(story, ui["section_languages"])
        language_lines = []
        for language in languages:
            name = language.name
            level = language.level
            progress = f" ({language.progress}%)" if language.progress else ""
            if name and level:
                language_lines.append(f"{name}: {level}{progress}")
            elif name:
                language_lines.append(f"{name}{progress}")
        story.append(Paragraph(text_or_empty(" | ".join(language_lines)), styles["body"]))

    footer_text = profile.footer if profile and profile.footer else ui["footer_text"]

    def draw_page(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawString(doc.leftMargin, 8 * mm, footer_text[:95])
        canvas.drawRightString(A4[0] - doc.rightMargin, 8 * mm, str(canvas.getPageNumber()))
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)

    filename = f'CV - {profile.full_name if profile else "Profile"}.pdf'
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def home(request):
    lang = (get_language() or "fr")[:2]
    context = _get_cv_context(lang)
    return render(request, "cv/index.html", context)


def download_cv_pdf(request):
    lang = (get_language() or "fr")[:2]
    context = _get_cv_context(lang)
    return _build_pdf_response(context)
