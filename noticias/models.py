from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class Categoria(models.Model):
    nome = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    resumo = models.CharField(max_length=300)
    conteudo = models.TextField()
    imagem = models.ImageField(upload_to='noticias/', blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='noticias')
    autor = models.ForeignKey(User, on_delete=models.PROTECT)
    destaque = models.BooleanField(default=False)
    publicada = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    divulgada = models.BooleanField(default=False)

    class Meta:
        ordering = ['-criada_em']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detalhe', args=[self.slug])

    def __str__(self):
        return self.titulo