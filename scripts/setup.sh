#!/bin/bash
set -e

echo "=================================="
echo "🚀 SGPI API - Setup Script"
echo "=================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado. Por favor, instale Python 3.11 ou superior."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "Python $PYTHON_VERSION encontrado"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    print_warning "Docker não encontrado. Você precisará do Docker para executar o ambiente completo."
else
    print_success "Docker encontrado"
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_warning "Docker Compose não encontrado. Você precisará do Docker Compose para executar o ambiente completo."
else
    print_success "Docker Compose encontrado"
fi

echo ""
echo "=================================="
echo "📦 Instalação de Dependências"
echo "=================================="

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    print_info "Criando ambiente virtual..."
    python3 -m venv venv
    print_success "Ambiente virtual criado"
else
    print_info "Ambiente virtual já existe"
fi

# Ativar ambiente virtual
print_info "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
print_info "Atualizando pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip atualizado"

# Instalar dependências
print_info "Instalando dependências..."
pip install -r requirements.txt > /dev/null 2>&1
print_success "Dependências instaladas"

# Instalar Playwright browsers
print_info "Instalando browsers do Playwright..."
playwright install > /dev/null 2>&1
print_success "Playwright configurado"

echo ""
echo "=================================="
echo "🔧 Configuração"
echo "=================================="

# Verificar se .env existe
if [ ! -f ".env" ]; then
    print_warning ".env não encontrado"
    echo ""
    read -p "Deseja criar um arquivo .env agora? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Criando .env..."
        cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sgpi

# Security
SECRET_KEY=development-secret-key-change-in-production

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_SECURE=false
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=sgpi-files
MINIO_PUBLIC_ENDPOINT=localhost:9000
MINIO_PUBLIC_SECURE=false

# API
ENVIRONMENT=development
API_PORT=8009
EOF
        print_success ".env criado com configurações padrão"
        print_warning "IMPORTANTE: Ajuste as configurações no arquivo .env antes de usar em produção!"
    fi
else
    print_success ".env já existe"
fi

echo ""
echo "=================================="
echo "🐳 Docker Setup"
echo "=================================="

# Verificar se as redes Docker existem
if command -v docker &> /dev/null; then
    if ! docker network ls | grep -q nginx_proxy; then
        print_info "Criando rede Docker nginx_proxy..."
        docker network create nginx_proxy
        print_success "Rede nginx_proxy criada"
    else
        print_success "Rede nginx_proxy já existe"
    fi
fi

echo ""
echo "=================================="
echo "✅ Setup Completo!"
echo "=================================="
echo ""
echo "Próximos passos:"
echo ""
echo "1. Ajuste as configurações no arquivo .env (se necessário)"
echo ""
echo "2. Inicie os serviços com Docker Compose:"
echo "   $ docker-compose up -d"
echo ""
echo "   Ou apenas o banco e MinIO:"
echo "   $ docker-compose up -d postgres minio"
echo ""
echo "3. Execute as migrations:"
echo "   $ source venv/bin/activate"
echo "   $ alembic upgrade head"
echo ""
echo "4. Inicie a aplicação:"
echo "   $ uvicorn app.main:app --reload --port 8009"
echo ""
echo "5. Acesse a documentação da API:"
echo "   http://localhost:8009/docs"
echo ""
echo "=================================="
print_success "Ambiente pronto para desenvolvimento! 🎉"
echo "=================================="

