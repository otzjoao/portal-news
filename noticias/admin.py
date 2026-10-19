from django.contrib import admin
from .models import Categoria, Noticia

@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'autor', 'publicada', 'criada_em')
    list_filter = ('categoria', 'publicada', 'destaque')
    search_fields = ('titulo', 'conteudo')

admin.site.register(Categoria)