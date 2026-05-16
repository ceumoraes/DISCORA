from django.contrib import admin
from .models import Album, Historico

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'artista', 'titulo', 'ano_lancamento', 'data_cadastro')
    list_display_links = ('id', 'titulo')
    search_fields = ('titulo', 'artista', 'id_spotify', 'id_lastfm')
    list_filter = ('ano_lancamento', 'data_cadastro')

@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil', 'album', 'data_escutado')
    search_fields = ('perfil__usuario__username', 'album__titulo')
    list_filter = ['data_escutado']