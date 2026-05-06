# RetroApp4L

Plataforma de retrospectivas ágeis em tempo real construída com Django, Django Channels e Celery.

## Tech Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Realtime**: Django Channels + Daphne (WebSocket)
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL 16
- **Auth**: JWT (djangorestframework-simplejwt) + django-allauth

## Arquitetura

O projeto é dividido nos seguintes serviços Docker:

| Serviço | Descrição | Porta |
|---------|-----------|-------|
| `backend` | API Django + WebSocket | 8000 |
| `worker` | Celery worker + beat | - |
| `db` | PostgreSQL 16 | 5432 |
| `redis` | Redis (cache e broker) | 6379 |

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)


## Deploy em Produção (Hostinger VPS KVM2)

O deploy oficial do RetroApp4L é realizado em um VPS KVM2 da Hostinger, utilizando Docker e Docker Compose. O ambiente foi configurado para produção seguindo um passo a passo detalhado no arquivo [deploy.md](deploy.md).

**Resumo do processo:**

1. Instalação do Docker no VPS (Ubuntu)
2. Instalação do Nginx e emissão de certificado SSL com Certbot
3. Clonagem do repositório em `/opt/retroapp4l`
4. Criação do arquivo `backend/.env.prod` com variáveis reais (DJANGO_SECRET_KEY, POSTGRES_PASSWORD, etc)
5. Instalação do hook de renovação SSL
6. Build e start dos containers com `docker compose -f docker-compose.prod.yml up -d --build`
7. Verificação dos serviços e acesso via domínio configurado

Veja o passo a passo completo e comandos em [deploy.md](deploy.md).

> **Nota:** O projeto deixou de focar em custo zero/MVP em cloud gratuita e agora recomenda VPS dedicada para produção, devido a requisitos de estabilidade e controle. O código segue open source (MIT), mas o deploy oficial não é mais em tiers gratuitos.

---

## Rodando localmente com Docker (desenvolvimento)

Se quiser rodar em ambiente local para desenvolvimento, siga os passos abaixo:

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd retroapp4l
```

### 2. Configure o ambiente

Copie o arquivo de exemplo de variáveis de ambiente:

```bash
cp backend/.env.example backend/.env
```

Edite o arquivo `backend/.env` conforme necessário.

### 3. Suba os serviços

```bash
docker-compose up -d
```

Isso irá:
- Construir as imagens do backend e worker
- Iniciar o PostgreSQL e Redis
- Rodar as migrações do Django automaticamente
- Iniciar a API na porta `8000`

### 4. Acesse a API

- **API**: `http://localhost:8000`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

## Comandos úteis

### Verificar logs

```bash
# Logs do backend
docker-compose logs -f backend

# Logs do worker
docker-compose logs -f worker
```

### Rodar testes

```bash
docker-compose exec backend python manage.py test
```

### Criar superusuário

```bash
docker-compose exec backend python manage.py createsuperuser
```

### Rodar migrações manualmente

```bash
docker-compose exec backend python manage.py migrate
```

### Parar os serviços

```bash
docker-compose down
```

### Parar e remover volumes (limpa o banco)

```bash
docker-compose down -v
```

## Endpoints da API

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/register/` | Registro de usuário |
| POST | `/api/auth/login/` | Login com JWT |
| POST | `/api/auth/logout/` | Logout (blacklist do token) |

### Retrospectivas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/retrospectives/` | Criar retrospectiva |
| GET | `/api/retrospectives/` | Listar retrospectivas |
| GET | `/api/retrospectives/<id>/` | Detalhe da retrospectiva |
| GET | `/api/retrospectives/suggestions/` | Sugestões de team_key |

## Estrutura do Projeto

```
retroapp4l/
├── backend/
│   ├── apps/                 # Apps Django (users, retrospectives, cards, actions, realtime)
│   ├── config/               # Configurações Django (settings, urls, asgi, celery)
│   ├── tests/                # Testes automatizados
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── Dockerfile.worker
├── docker-compose.yml
└── docs/
```

## Desenvolvimento Local (sem Docker)

Se preferir rodar localmente:

```bash
# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
cd backend
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env

# Rodar migrações
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

## Licença

Este projeto está sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
