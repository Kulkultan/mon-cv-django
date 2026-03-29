from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import override

from .models import Experience, Profile


class CvPrintRegressionTests(TestCase):
    def setUp(self):
        Profile.objects.create(
            full_name="Test User",
            headline_fr="Headline",
            bio_fr="Bio",
            email="test@example.com",
            phone="+22500000000",
            address_fr="Abidjan",
        )
        Experience.objects.create(
            title_fr="Consultant",
            company_fr="ACME",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 1),
        )

    def test_contact_cards_remain_printable(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'class="contact-card card elevated-card print-keep"', count=3)
        self.assertNotContains(response, 'contact-card card elevated-card no-print')

    def test_home_links_to_server_side_pdf_download(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, reverse("download_cv_pdf"))

    def test_download_cv_pdf_returns_a_pdf_file(self):
        response = self.client.get(reverse("download_cv_pdf"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_english_page_links_back_to_root_french_url(self):
        response = self.client.get("/en/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/" class="chip-action">FR</a>', html=False)

    def test_french_page_links_to_prefixed_english_url(self):
        with override("fr"):
            response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/en/" class="chip-action">EN</a>', html=False)
