from django.contrib import admin
from .models import Profile, Experience, Certification, Education, Skill, Language, UiText

admin.site.site_header = 'MonCV Premium'
admin.site.site_title = 'MonCV Premium'
admin.site.index_title = 'Administration du CV'

@admin.register(UiText)
class UiTextAdmin(admin.ModelAdmin):
    list_display = ('key', 'text_fr', 'text_en')
    search_fields = ('key', 'text_fr', 'text_en')
    ordering = ('key',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informations générales', {'fields': ('full_name', 'email', 'phone', 'linkedin_url', 'portfolio_url')}),
        ('Français', {'fields': ('headline_fr', 'bio_fr', 'address_fr', 'footer_fr', 'keywords_fr')}),
        ('English', {'fields': ('headline_en', 'bio_en', 'address_en', 'footer_en', 'keywords_en')}),
    )

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title_label', 'company_fr', 'start_date', 'end_date', 'is_current', 'duration_admin', 'order')
    list_display_links = ('title_label', 'company_fr')
    list_editable = ('order', 'is_current')
    ordering = ('order', '-start_date', '-id')
    search_fields = ('title_fr', 'title_en', 'company_fr', 'company_en', 'location_fr', 'location_en')
    fieldsets = (
        ('Ordre et période', {'fields': ('order', 'start_date', 'end_date', 'is_current')}),
        ('Français', {'fields': ('title_fr', 'company_fr', 'location_fr', 'description_fr', 'highlights_fr')}),
        ('English', {'fields': ('title_en', 'company_en', 'location_en', 'description_en', 'highlights_en')}),
    )

    @admin.display(description='Titre affiché')
    def title_label(self, obj):
        return obj.title_fr or '— à renseigner —'

    @admin.display(description='Durée')
    def duration_admin(self, obj):
        return obj.get_duration_display('fr')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name_fr', 'name_en', 'order')
    list_editable = ('order',)
    ordering = ('order', 'id')
    search_fields = ('name_fr', 'name_en')
    fieldsets = (('Ordre', {'fields': ('order',)}), ('Français', {'fields': ('name_fr',)}), ('English', {'fields': ('name_en',)}))

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree_fr', 'school_fr', 'start_date', 'end_date', 'is_current', 'duration_admin', 'order')
    list_display_links = ('degree_fr', 'school_fr')
    list_editable = ('order', 'is_current')
    ordering = ('order', '-start_date', '-id')
    search_fields = ('degree_fr', 'degree_en', 'school_fr', 'school_en', 'location_fr', 'location_en')
    fieldsets = (
        ('Ordre et période', {'fields': ('order', 'start_date', 'end_date', 'is_current')}),
        ('Français', {'fields': ('degree_fr', 'school_fr', 'location_fr')}),
        ('English', {'fields': ('degree_en', 'school_en', 'location_en')}),
    )

    @admin.display(description='Durée')
    def duration_admin(self, obj):
        return obj.get_duration_display('fr')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name_fr', 'name_en', 'order')
    list_editable = ('order',)
    ordering = ('order', 'id')
    search_fields = ('name_fr', 'name_en')
    fieldsets = (('Ordre', {'fields': ('order',)}), ('Français', {'fields': ('name_fr',)}), ('English', {'fields': ('name_en',)}))

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name_fr', 'level_fr', 'progress', 'order')
    list_editable = ('progress', 'order')
    ordering = ('order', 'id')
    search_fields = ('name_fr', 'name_en', 'level_fr', 'level_en')
    fieldsets = (('Ordre', {'fields': ('order', 'progress')}), ('Français', {'fields': ('name_fr', 'level_fr')}), ('English', {'fields': ('name_en', 'level_en')}))
