import os
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent


def _carregar_secrets():
    caminho = BASE_DIR / 'secrets.yaml'
    if not caminho.exists():
        return {}
    with open(caminho, encoding='utf-8') as f:
        dados = yaml.safe_load(f)
    if dados is None:
        return {}
    if not isinstance(dados, dict):
        raise ValueError(
            'secrets.yaml inválido: use linhas no formato chave: "valor" '
            '(ex.: django_secret_key: "abc")'
        )
    return dados


_SECRETS = _carregar_secrets()


def secret(nome, padrao=''):
    # variável de ambiente (em maiúsculas) tem prioridade sobre o YAML
    return os.getenv(nome.upper(), _SECRETS.get(nome, padrao))


SECRET_KEY = secret('django_secret_key', 'chave-insegura-so-para-dev')
SITE_URL = secret('site_url', 'http://127.0.0.1:8000')
N8N_WEBHOOK_URL = secret('n8n_webhook_url')
N8N_WEBHOOK_TOKEN = secret('n8n_webhook_token')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'noticias',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'noticias.context_processors.categorias',
            ],
        },
    },
]

WSGI_APPLICATION = 'portal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}