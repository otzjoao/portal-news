# Portal de Notícias

Portal de notícias feito em **Django**, com painel de redação no admin e **automação de redes sociais via n8n**: quando uma notícia é publicada, o portal avisa o n8n por webhook e o n8n publica nas redes.

```
Admin salva notícia (publicada) → Django envia POST ao webhook do n8n → n8n publica nas redes
```

## Funcionalidades

- Home com notícias em destaque, grade de cards e paginação
- Páginas por categoria, busca por título e página de detalhe
- Painel de redação no `/admin/` (categorias, notícias, destaque, publicada/rascunho)
- Tema claro/escuro (preferência salva no navegador)
- Tags Open Graph na página da notícia (preview bonito ao compartilhar o link)
- Webhook automático para o n8n ao publicar, com controle de envio duplicado (`divulgada`)

## Stack

| Camada      | Tecnologia                           |
| ----------- | ------------------------------------ |
| Backend     | Python 3 + Django                    |
| Banco (dev) | SQLite                               |
| Frontend    | Templates Django + HTML/CSS/JS puro  |
| Automação   | n8n (local ou Docker)                |
| Redes       | Telegram primeiro; demais em seguida |

## Estrutura do projeto

```
noticias/                  # raiz do repositório
├── manage.py
├── requirements.txt
├── secrets.example.yaml   # modelo de configuração (copie para secrets.yaml)
├── portal/                # configuração do projeto (settings, urls)
└── noticias/              # app principal
    ├── models.py          # Categoria e Noticia
    ├── views.py           # Home, PorCategoria, Detalhe
    ├── urls.py
    ├── admin.py
    ├── signals.py         # dispara o webhook para o n8n
    ├── apps.py            # registra o signal no ready()
    ├── context_processors.py  # categorias no menu de todas as páginas
    └── templates/noticias/    # base.html, home.html, detalhe.html
```

## Como rodar localmente

### Pré-requisitos

- Python 3.12 ou superior
- Git
- (Para a automação) n8n: Docker **ou** Node 24+

### 1. Clonar e criar o ambiente virtual

```bash
git clone https://github.com/otzjoao/portal-news.git
cd portal-news
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python3 -m pip install -r requirements.txt
```

### 2. Configurar os segredos

O arquivo `secrets.yaml` **não vai para o Git** (está no `.gitignore`). Crie o seu a partir do modelo:

```bash
cp secrets.example.yaml secrets.yaml
```

Edite o `secrets.yaml`:

```yaml
django_secret_key: "gere-uma-chave-propria"
site_url: "http://127.0.0.1:8000"
n8n_webhook_url: "" # preencha quando tiver o n8n rodando
n8n_webhook_token: ""
```

Gere uma `django_secret_key` própria (cada dev usa a sua):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Com `n8n_webhook_url` vazio, o portal funciona normalmente e simplesmente não envia nada ao n8n.

> Variáveis de ambiente em maiúsculas (`N8N_WEBHOOK_URL`, `DJANGO_SECRET_KEY`...) têm prioridade sobre o YAML. Isso será usado no deploy.

### 3. Banco de dados e usuário admin

```bash
python3 manage.py migrate
python3 manage.py createsuperuser
```

### 4. Subir o servidor

```bash
python3 manage.py runserver
```

- Portal: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

No admin, crie 2 ou 3 **categorias** e algumas **notícias** (marque `destaque` em até 3 para aparecerem no topo da home).

## Integração com o n8n

### Subir o n8n

Opção Docker (recomendada):

```bash
docker run -it --rm --name n8n -p 5678:5678 \
  -e GENERIC_TIMEZONE="America/Campo_Grande" \
  -e TZ="America/Campo_Grande" \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

Opção Node (precisa do Node 24 ou superior):

```bash
npx n8n
```

Acesse http://localhost:5678 e crie a conta local.

### Montar o workflow

1. Crie um workflow e adicione o nó **Webhook**:
   - Método `POST`, Path `noticias`
   - Authentication: **Header Auth**, com a credencial:
     - Name: `X-Webhook-Token`
     - Value: o mesmo valor de `n8n_webhook_token` do seu `secrets.yaml`
   - Respond: `Immediately`
2. Adicione um nó **Edit Fields (Set)** com os campos `legenda` e `imagem` (modo Expression):

```
legenda:
📰 {{ $json.body.titulo }}

{{ $json.body.resumo }}

🔗 {{ $json.body.url }}

#{{ $json.body.categoria.replace(/\s+/g, '') }}

imagem: {{ $json.body.imagem }}
```

3. Adicione o nó da rede social (comece pelo **Telegram**, ação _Send a text message_, texto `{{ $json.legenda }}`).

### Testar o webhook

URLs do n8n:

| Modo     | URL                                           | Quando usar                                                  |
| -------- | --------------------------------------------- | ------------------------------------------------------------ |
| Teste    | `http://localhost:5678/webhook-test/noticias` | Só funciona enquanto você clica em **Listen for test event** |
| Produção | `http://localhost:5678/webhook/noticias`      | Funciona com o workflow **publicado** (botão Publish)        |

Teste isolado com `curl` (n8n escutando):

```bash
curl -X POST http://localhost:5678/webhook-test/noticias \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Token: SEU_TOKEN" \
  -d '{"titulo":"Teste","resumo":"Resumo","categoria":"Tecnologia","url":"http://127.0.0.1:8000/","imagem":null}'
```

Depois coloque a URL e o token no `secrets.yaml`, **reinicie o `runserver`** (ele só lê o arquivo ao subir) e publique uma notícia nova no admin.

### Payload enviado pelo Django

| Campo       | Descrição                                       |
| ----------- | ----------------------------------------------- |
| `id`        | ID da notícia                                   |
| `titulo`    | Título                                          |
| `resumo`    | Resumo (até 300 caracteres)                     |
| `categoria` | Nome da categoria                               |
| `autor`     | Nome completo ou username                       |
| `url`       | Link completo da notícia (`site_url` + caminho) |
| `imagem`    | URL completa da imagem ou `null`                |
| `criada_em` | Data/hora em ISO 8601                           |

### Regras do envio

O signal (`noticias/signals.py`) só envia quando a notícia está **publicada** e ainda **não foi divulgada**. Se o n8n responder com sucesso, o campo `divulgada` vira `True` e a notícia não é enviada de novo. Para reenviar, desmarque `divulgada` no admin e salve.

O envio roda em uma thread, então um n8n lento não trava o admin. Falhas aparecem no terminal do Django com o prefixo `[n8n]`.

### Limitação em desenvolvimento

As redes sociais precisam abrir o link e baixar a imagem, e `127.0.0.1` só existe no seu computador. Para testar posts com imagem de verdade, é preciso expor o portal (túnel como `cloudflared` ou `ngrok`, ajustando `site_url`) ou fazer o deploy.

## Fluxo de trabalho no Git

- A branch `main` deve estar sempre funcionando.
- Trabalhe em branches curtas, uma por tarefa:

```bash
git checkout main
git pull
git checkout -b feature/nome-da-tarefa
```

- Commits pequenos e com mensagem clara (`Adiciona busca por categoria`, `Corrige paginação`).
- Antes de abrir um Pull Request: `python3 manage.py check` sem erros e o portal rodando.
- Se mudar os models: `python3 manage.py makemigrations noticias` e commite o arquivo da migration.
- Sempre `git pull` antes de começar e antes de enviar, para evitar conflitos.

### O que nunca vai para o Git

`secrets.yaml`, `.env*`, `db.sqlite3`, `media/` e `.venv/`. Se um token vazar para um commit, **troque o token**, porque apagar o arquivo não remove do histórico.

## Problemas comuns

| Sintoma                               | Causa provável                                                           |
| ------------------------------------- | ------------------------------------------------------------------------ |
| `TemplateDoesNotExist`                | Templates fora de `noticias/templates/noticias/`                         |
| `Incorrect timezone setting`          | Use um fuso válido, como `America/Sao_Paulo`                             |
| `403` ao enviar ao n8n                | Token do `secrets.yaml` diferente da credencial do n8n                   |
| `404` ao enviar ao n8n                | n8n não está escutando (modo teste) ou workflow não publicado (produção) |
| Notícia criada e nada chegou          | Confira `publicada`, `divulgada` e as linhas `[n8n]` no terminal         |
| Mudou o `secrets.yaml` e nada mudou   | Reinicie o `runserver`                                                   |
| `'str' object has no attribute 'get'` | `secrets.yaml` fora do formato `chave: "valor"`                          |

## Roadmap

- [x] Portal com home, categorias, busca e detalhe
- [x] Webhook do Django para o n8n
- [ ] Workflow do n8n publicando no Telegram
- [ ] Demais redes sociais (Instagram, Facebook, X, LinkedIn)
- [ ] Imagem nos posts (depende de URL pública)
- [ ] Editor rico no conteúdo (CKEditor ou TinyMCE)
- [ ] Comentários e "mais lidas"
- [ ] SEO (sitemap) e deploy (Render, Railway ou PythonAnywhere, com PostgreSQL)
- [ ] Settings de produção (`DEBUG`, `ALLOWED_HOSTS` e segredos via variáveis de ambiente)
