from __future__ import annotations
from django.db import models
from django.utils import timezone, translation

MONTHS_FR = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
MONTHS_EN = ['January','February','March','April','May','June','July','August','September','October','November','December']


def month_diff(start, end):
    if not start or not end:
        return 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    return max(months + 1, 1)


def split_years_months(total_months):
    return total_months // 12, total_months % 12


def format_duration(total_months, lang='fr'):
    years, months = split_years_months(total_months)
    parts = []
    if lang == 'en':
        if years:
            parts.append(f"{years} year" + ("s" if years > 1 else ""))
        if months:
            parts.append(f"{months} month" + ("s" if months > 1 else ""))
        return ' '.join(parts) if parts else '0 month'
    if years:
        parts.append(f"{years} an" + ("s" if years > 1 else ""))
    if months:
        parts.append(f"{months} mois")
    return ' '.join(parts) if parts else '0 mois'


def format_month_label(date_value, lang='fr'):
    if not date_value:
        return ''
    if lang == 'en':
        return f"{MONTHS_EN[date_value.month - 1]} {date_value.year}"
    return f"{MONTHS_FR[date_value.month - 1].capitalize()} {date_value.year}"


class BaseTranslatedModel(models.Model):
    class Meta:
        abstract = True

    def lang(self):
        return (translation.get_language() or 'fr')[:2]


class DatedDurationMixin(models.Model):
    start_date = models.DateField('Date de début')
    end_date = models.DateField('Date de fin', blank=True, null=True)
    is_current = models.BooleanField('En cours', default=False)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            from django.core.exceptions import ValidationError
            raise ValidationError({'end_date': 'La date de fin doit être postérieure ou égale à la date de début.'})

    @property
    def effective_end_date(self):
        if self.is_current or not self.end_date:
            today = timezone.localdate()
            return today.replace(day=1)
        return self.end_date

    def duration_months(self):
        return month_diff(self.start_date, self.effective_end_date)

    def get_duration_display(self, lang=None):
        lang = lang or (translation.get_language() or 'fr')[:2]
        return format_duration(self.duration_months(), lang)

    @property
    def duration_display(self):
        return self.get_duration_display()

    def get_period_display(self, lang=None):
        lang = lang or (translation.get_language() or 'fr')[:2]
        start = format_month_label(self.start_date, lang)
        end = 'Present' if lang == 'en' else 'Présent'
        if not self.is_current and self.end_date:
            end = format_month_label(self.end_date, lang)
        return f"{start} — {end}"

    @property
    def period_display(self):
        return self.get_period_display()


class UiText(BaseTranslatedModel):
    key = models.CharField(max_length=100, unique=True)
    text_fr = models.CharField(max_length=255, blank=True, default='')
    text_en = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        verbose_name = 'Texte interface'
        verbose_name_plural = 'Textes interface'
        ordering = ['key']

    def __str__(self):
        return self.key

    @property
    def text(self):
        return self.text_en if self.lang() == 'en' and self.text_en else self.text_fr


class Profile(BaseTranslatedModel):
    full_name = models.CharField(max_length=150, default='LEGRE Zaddy Wilfried Ghislain')
    headline_fr = models.CharField(max_length=255, blank=True, default='')
    headline_en = models.CharField(max_length=255, blank=True, default='')
    bio_fr = models.TextField(blank=True, default='')
    bio_en = models.TextField(blank=True, default='')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    address_fr = models.CharField(max_length=255, blank=True, default='')
    address_en = models.CharField(max_length=255, blank=True, default='')
    footer_fr = models.CharField(max_length=255, blank=True, default='')
    footer_en = models.CharField(max_length=255, blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    portfolio_url = models.URLField(blank=True, default='')
    keywords_fr = models.TextField(blank=True, default='', help_text='Mots-clés ATS séparés par des virgules ou des retours à la ligne')
    keywords_en = models.TextField(blank=True, default='', help_text='ATS keywords separated by commas or line breaks')

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profil'

    def __str__(self):
        return self.full_name

    @property
    def headline(self):
        return self.headline_en if self.lang() == 'en' and self.headline_en else self.headline_fr

    @property
    def bio(self):
        return self.bio_en if self.lang() == 'en' and self.bio_en else self.bio_fr

    @property
    def address(self):
        return self.address_en if self.lang() == 'en' and self.address_en else self.address_fr

    @property
    def footer(self):
        return self.footer_en if self.lang() == 'en' and self.footer_en else self.footer_fr

    @property
    def keywords(self):
        raw = self.keywords_en if self.lang() == 'en' and self.keywords_en else self.keywords_fr
        if not raw:
            return []
        values = []
        normalized = ','.join(raw.splitlines())
        for chunk in normalized.split(','):
            item = chunk.strip()
            if item and item not in values:
                values.append(item)
        return values


class Experience(BaseTranslatedModel, DatedDurationMixin):
    order = models.PositiveIntegerField(default=0)
    title_fr = models.CharField(max_length=255, blank=True, default='')
    title_en = models.CharField(max_length=255, blank=True, default='')
    company_fr = models.CharField(max_length=255, blank=True, default='')
    company_en = models.CharField(max_length=255, blank=True, default='')
    location_fr = models.CharField(max_length=255, blank=True, default='')
    location_en = models.CharField(max_length=255, blank=True, default='')
    description_fr = models.TextField(blank=True, default='', help_text='Une ligne = une puce')
    description_en = models.TextField(blank=True, default='', help_text='One line = one bullet')
    highlights_fr = models.TextField(blank=True, default='', help_text='Une ligne = un KPI / impact / résultat')
    highlights_en = models.TextField(blank=True, default='', help_text='One line = one KPI / impact / result')

    class Meta:
        ordering = ['order', '-start_date', '-id']
        verbose_name = 'Expérience'
        verbose_name_plural = 'Expériences'

    def __str__(self):
        return self.title_fr or self.company_fr or 'Expérience'

    @property
    def title(self):
        return self.title_en if self.lang() == 'en' and self.title_en else self.title_fr

    @property
    def company(self):
        return self.company_en if self.lang() == 'en' and self.company_en else self.company_fr

    @property
    def location(self):
        return self.location_en if self.lang() == 'en' and self.location_en else self.location_fr

    @property
    def description(self):
        return self.description_en if self.lang() == 'en' and self.description_en else self.description_fr

    @property
    def description_points(self):
        return [line.strip() for line in self.description.splitlines() if line.strip()]

    @property
    def highlights(self):
        return self.highlights_en if self.lang() == 'en' and self.highlights_en else self.highlights_fr

    @property
    def highlight_items(self):
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]


class Education(BaseTranslatedModel, DatedDurationMixin):
    order = models.PositiveIntegerField(default=0)
    degree_fr = models.CharField(max_length=255, blank=True, default='')
    degree_en = models.CharField(max_length=255, blank=True, default='')
    school_fr = models.CharField(max_length=255, blank=True, default='')
    school_en = models.CharField(max_length=255, blank=True, default='')
    location_fr = models.CharField(max_length=255, blank=True, default='')
    location_en = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['order', '-start_date', '-id']
        verbose_name = 'Formation'
        verbose_name_plural = 'Formations'

    def __str__(self):
        return self.degree_fr or self.school_fr or 'Formation'

    @property
    def degree(self):
        return self.degree_en if self.lang() == 'en' and self.degree_en else self.degree_fr

    @property
    def school(self):
        return self.school_en if self.lang() == 'en' and self.school_en else self.school_fr

    @property
    def location(self):
        return self.location_en if self.lang() == 'en' and self.location_en else self.location_fr


class Certification(BaseTranslatedModel):
    order = models.PositiveIntegerField(default=0)
    name_fr = models.CharField(max_length=255, blank=True, default='')
    name_en = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'

    def __str__(self):
        return self.name_fr or 'Certification'

    @property
    def name(self):
        return self.name_en if self.lang() == 'en' and self.name_en else self.name_fr


class Skill(BaseTranslatedModel):
    order = models.PositiveIntegerField(default=0)
    name_fr = models.CharField(max_length=150, blank=True, default='')
    name_en = models.CharField(max_length=150, blank=True, default='')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Compétence'
        verbose_name_plural = 'Compétences'

    def __str__(self):
        return self.name_fr or 'Compétence'

    @property
    def name(self):
        return self.name_en if self.lang() == 'en' and self.name_en else self.name_fr


class Language(BaseTranslatedModel):
    order = models.PositiveIntegerField(default=0)
    name_fr = models.CharField(max_length=100, blank=True, default='')
    name_en = models.CharField(max_length=100, blank=True, default='')
    level_fr = models.CharField(max_length=100, blank=True, default='')
    level_en = models.CharField(max_length=100, blank=True, default='')
    progress = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Langue'
        verbose_name_plural = 'Langues'

    def __str__(self):
        return self.name_fr or 'Langue'

    @property
    def name(self):
        return self.name_en if self.lang() == 'en' and self.name_en else self.name_fr

    @property
    def level(self):
        return self.level_en if self.lang() == 'en' and self.level_en else self.level_fr
