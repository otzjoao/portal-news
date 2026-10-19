import threading
import requests
from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Noticia


def _enviar(pk, payload):
    try:
        r = requests.post(
            settings.N8N_WEBHOOK_URL,
            json=payload,
            headers={'X-Webhook-Token': settings.N8N_WEBHOOK_TOKEN},
            timeout=10,
        )
        r.raise_for_status()
        # update() não dispara o signal de novo
        Noticia.objects.filter(pk=pk).update(divulgada=True)
        print(f'[n8n] notícia {pk} enviada ({r.status_code})')
    except requests.RequestException as e:
        print(f'[n8n] falha ao enviar notícia {pk}: {e}')


@receiver(post_save, sender=Noticia)
def notificar_n8n(sender, instance, **kwargs):
    print(f'[n8n] signal disparou: {instance.pk} url={settings.N8N_WEBHOOK_URL!r} '
          f'publicada={instance.publicada} divulgada={instance.divulgada}')

    if not settings.N8N_WEBHOOK_URL:
        return
    if not instance.publicada or instance.divulgada:
        return

    payload = {
        'id': instance.pk,
        'titulo': instance.titulo,
        'resumo': instance.resumo,
        'categoria': instance.categoria.nome,
        'autor': instance.autor.get_full_name() or instance.autor.username,
        'url': settings.SITE_URL + instance.get_absolute_url(),
        'imagem': settings.SITE_URL + instance.imagem.url if instance.imagem else None,
        'criada_em': instance.criada_em.isoformat(),
    }

    transaction.on_commit(
        lambda: threading.Thread(target=_enviar, args=(instance.pk, payload), daemon=True).start()
    )