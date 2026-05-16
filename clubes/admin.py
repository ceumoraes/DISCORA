from django.contrib import admin
from .models import Clube, MembroGrupo

class MembroGrupoInline(admin.StackedInline):
    model = MembroGrupo
    extra = 1

@admin.register(Clube)
class ClubeAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_clube', 'data_criacao')
    search_fields = ('nome_clube', 'descricao')
    inlines = [MembroGrupoInline]

@admin.register(MembroGrupo)
class MembroGrupoAdmin(admin.ModelAdmin):
    list_display = ('id', 'perfil', 'clube', 'admin', 'data_entrada')
    list_filter = ('admin', 'data_entrada', 'clube')
    search_fields = ('perfil__usuario__username', 'clube__nome__clube')
