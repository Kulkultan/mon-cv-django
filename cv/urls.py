from django.urls import path

from .views import download_cv_pdf, home

urlpatterns = [
    path("", home, name="home"),
    path("download/pdf/", download_cv_pdf, name="download_cv_pdf"),
]
