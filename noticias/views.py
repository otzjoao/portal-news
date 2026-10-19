from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Noticia, Categoria

class Home(ListView):
    model = Noticia
    template_name = 'noticias/home.html'
    context_object_name = 'noticias'
    paginate_by = 10

    def get_queryset(self):
        qs = Noticia.objects.filter(publicada=True).select_related('categoria', 'autor')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(titulo__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['destaques'] = Noticia.objects.filter(publicada=True, destaque=True)[:3]
        ctx['categorias'] = Categoria.objects.all()
        return ctx

class PorCategoria(Home):
    def get_queryset(self):
        return super().get_queryset().filter(categoria__slug=self.kwargs['slug'])

class Detalhe(DetailView):
    model = Noticia
    template_name = 'noticias/detalhe.html'