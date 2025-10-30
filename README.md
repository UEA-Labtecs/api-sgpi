# API SGPI - Sistema de Gestão de Propriedade Intelectual

API para gerenciamento de patentes com crawler integrado do INPI Brasil.

## 🏗️ Tecnologias

- **Python 3.11+**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **Alembic** - Migrations de banco de dados
- **PostgreSQL** - Banco de dados relacional
- **MinIO** - Storage de arquivos (S3-compatible)
- **Playwright** - Crawler para o site do INPI
- **Docker** - Containerização

## 📋 Pré-requisitos

- Python 3.11 ou superior
- PostgreSQL 16
- MinIO (ou S3-compatible storage)
- Docker e Docker Compose (para ambiente de desenvolvimento)

## 🚀 Como Executar

### Desenvolvimento Local

1. **Clone o repositório**
```bash
git clone <repo-url>
cd api-sgpi
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
playwright install
```

4. **Configure as variáveis de ambiente**

Crie um arquivo `.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sgpi
SECRET_KEY=your-secret-key-here
MINIO_ENDPOINT=localhost:9000
MINIO_SECURE=false
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=sgpi-files
MINIO_PUBLIC_ENDPOINT=localhost:9000
MINIO_PUBLIC_SECURE=false
```

5. **Execute as migrations**
```bash
alembic upgrade head
```

6. **Inicie a aplicação**
```bash
uvicorn app.main:app --reload --port 8009
```

A API estará disponível em: http://localhost:8009

Documentação Swagger: http://localhost:8009/docs

### Usando Docker Compose

1. **Inicie os serviços**
```bash
docker-compose up -d
```

Isso iniciará:
- API na porta 8009
- PostgreSQL na porta 5445
- MinIO na porta 9000 (API) e 9001 (Console)

2. **Verifique os logs**
```bash
docker-compose logs -f api
```

3. **Parar os serviços**
```bash
docker-compose down
```

## 📁 Estrutura do Projeto

```
api-sgpi/
├── app/
│   ├── core/              # Configurações e utilitários
│   │   ├── config.py      # Configurações da aplicação
│   │   ├── database.py    # Configuração do banco de dados
│   │   ├── security.py    # Autenticação e segurança
│   │   └── minioClient.py # Cliente MinIO
│   ├── models/            # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── patent.py
│   │   ├── userPatents.py
│   │   └── userPatentStage.py
│   ├── schemas/           # Schemas Pydantic
│   ├── routes/            # Rotas da API
│   │   ├── auth.py
│   │   ├── patent.py
│   │   ├── dashboard.py
│   │   └── userPatentStage.py
│   ├── services/          # Lógica de negócio
│   │   ├── auth_service.py
│   │   ├── crawler_service.py
│   │   └── storage_service.py
│   ├── crawler/           # Crawler do INPI
│   │   └── crawler.py
│   └── main.py           # Ponto de entrada
├── alembic/              # Migrations do banco de dados
├── tests/                # Testes (a implementar)
├── .github/
│   └── workflows/
│       └── ci-cd.yaml    # Pipeline de CI/CD
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🔌 Endpoints Principais

### Autenticação
- `POST /auth/login` - Login de usuário
- `POST /auth/register` - Registro de novo usuário

### Patentes
- `GET /patents` - Lista patentes
- `GET /patents/{id}` - Detalhes de uma patente
- `POST /patents` - Criar nova patente
- `PUT /patents/{id}` - Atualizar patente
- `DELETE /patents/{id}` - Deletar patente

### Dashboard
- `GET /dashboard/stats` - Estatísticas do sistema
- `GET /dashboard/user-patents` - Patentes do usuário

### User Patent Stages
- `GET /user-patent-stages` - Lista estágios de patentes do usuário
- `POST /user-patent-stages` - Criar novo estágio
- `PUT /user-patent-stages/{id}` - Atualizar estágio
- `DELETE /user-patent-stages/{id}` - Deletar estágio

Acesse `/docs` para documentação completa da API.

## 🗃️ Banco de Dados

### Criar nova migration

```bash
alembic revision --autogenerate -m "descrição da mudança"
```

### Aplicar migrations

```bash
alembic upgrade head
```

### Reverter migration

```bash
alembic downgrade -1
```

## 🧪 Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio

# Rodar testes
pytest tests/ -v

# Rodar com cobertura
pytest tests/ --cov=app --cov-report=html
```

## 🔐 Autenticação

A API usa JWT (JSON Web Tokens) para autenticação. 

1. Faça login em `/auth/login` com suas credenciais
2. Receba um token JWT na resposta
3. Inclua o token no header `Authorization: Bearer <token>` em requisições autenticadas

## 📦 MinIO Storage

O sistema usa MinIO para armazenar arquivos de patentes. Os arquivos são organizados por:

```
sgpi-files/
└── patents/
    └── {patent_id}/
        └── stage-{stage_number}/
            └── {filename}
```

## 🚀 CI/CD

O projeto usa GitHub Actions para CI/CD automatizado.

### Pipeline Stages:

1. **Test & Lint** - Executa em todos os PRs e pushes
   - Linting com flake8
   - Formatação com black
   - Testes automatizados

2. **Build & Push** - Executa em push para `main` e `develop`
   - Constrói imagem Docker
   - Push para GitHub Container Registry

3. **Deploy** - Executa apenas em push para `main`
   - Deploy automático no servidor de produção
   - Usa self-hosted runner

### Configuração:

Para configurar o CI/CD, consulte:
- [SETUP-GITHUB-SECRETS.md](./SETUP-GITHUB-SECRETS.md) - Como configurar secrets
- [SETUP-SELF-HOSTED-RUNNER.md](./SETUP-SELF-HOSTED-RUNNER.md) - Como configurar o runner

### Status do Pipeline:

![CI Pipeline](https://github.com/SEU-USUARIO/SEU-REPO/actions/workflows/ci-cd.yaml/badge.svg)

## 🐳 Docker

### Build manual

```bash
docker build -t api-sgpi .
```

### Run manual

```bash
docker run -d \
  --name api-sgpi \
  -p 8009:8009 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/sgpi" \
  -e SECRET_KEY="your-secret" \
  -e MINIO_ENDPOINT="minio:9000" \
  -e MINIO_ACCESS_KEY="minioadmin" \
  -e MINIO_SECRET_KEY="minioadmin" \
  api-sgpi
```

## 🔧 Variáveis de Ambiente

| Variável | Descrição | Obrigatória | Padrão |
|----------|-----------|-------------|--------|
| `DATABASE_URL` | URL de conexão PostgreSQL | ✅ | - |
| `SECRET_KEY` | Chave secreta para JWT | ✅ | - |
| `MINIO_ENDPOINT` | Endpoint do MinIO | ✅ | - |
| `MINIO_SECURE` | Usar HTTPS no MinIO | ❌ | `false` |
| `MINIO_ACCESS_KEY` | Access Key do MinIO | ✅ | - |
| `MINIO_SECRET_KEY` | Secret Key do MinIO | ✅ | - |
| `MINIO_BUCKET` | Nome do bucket MinIO | ❌ | `sgpi-files` |
| `MINIO_PUBLIC_ENDPOINT` | Endpoint público do MinIO | ❌ | - |
| `MINIO_PUBLIC_SECURE` | Usar HTTPS no endpoint público | ❌ | `false` |

## 📝 Desenvolvimento

### Code Style

O projeto segue PEP 8. Use ferramentas de linting:

```bash
# Lint
flake8 app

# Format
black app

# Type checking
mypy app
```

### Commit Messages

Siga o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: adiciona novo endpoint de relatórios
fix: corrige bug no crawler do INPI
docs: atualiza documentação da API
chore: atualiza dependências
```

## 🤝 Contribuindo

1. Crie um branch para sua feature (`git checkout -b feature/AmazingFeature`)
2. Commit suas mudanças (`git commit -m 'feat: Add some AmazingFeature'`)
3. Push para o branch (`git push origin feature/AmazingFeature`)
4. Abra um Pull Request

## 📄 Licença

Este projeto é proprietário da Universidade do Estado do Amazonas (UEA).

## 👥 Autores

- Time LabTECS - UEA

## 📞 Suporte

Para suporte, entre em contato com a equipe LabTECS.

## 🔗 Links Úteis

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [MinIO Documentation](https://docs.min.io/)
- [Playwright Documentation](https://playwright.dev/python/)
