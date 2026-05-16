from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil', 'album', 'nota', 'data_criacao')
    list_editable = ('nota',)
    list_filter = ('nota', 'data_criacao')
    search_fields = ('perfil__usuario__username', 'album__titulo', 'comentario')


