#!/bin/bash
set -e

# Script de deploy manual para SGPI API
# Use este script quando não estiver usando GitHub Actions

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================="
echo "🚀 SGPI API - Deploy Script"
echo -e "==================================${NC}"
echo ""

# Configurações padrão
CONTAINER_NAME="api-sgpi"
IMAGE_NAME="api-sgpi"
HOST_PORT="${PORT:-8009}"
CONTAINER_PORT=8009
NETWORK="nginx_proxy"

# Função para imprimir mensagens
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
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado!"
    exit 1
fi

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    print_error "Arquivo .env não encontrado!"
    print_info "Crie um arquivo .env com as variáveis de ambiente necessárias."
    exit 1
fi

print_success "Arquivo .env encontrado"

# Carregar variáveis do .env
export $(cat .env | grep -v '^#' | xargs)

# Validar variáveis obrigatórias
if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL não está configurado no .env"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    print_error "SECRET_KEY não está configurado no .env"
    exit 1
fi

print_success "Variáveis de ambiente validadas"

echo ""
print_info "Construindo imagem Docker..."
docker build -t $IMAGE_NAME . || {
    print_error "Falha ao construir imagem Docker"
    exit 1
}
print_success "Imagem construída: $IMAGE_NAME"

echo ""
print_info "Verificando rede Docker..."
if ! docker network ls | grep -q $NETWORK; then
    print_warning "Rede $NETWORK não existe. Criando..."
    docker network create $NETWORK || {
        print_error "Falha ao criar rede $NETWORK"
        exit 1
    }
    print_success "Rede $NETWORK criada"
else
    print_success "Rede $NETWORK existe"
fi

echo ""
print_info "Parando container antigo..."
docker stop $CONTAINER_NAME 2>/dev/null || true
print_info "Removendo container antigo..."
docker rm $CONTAINER_NAME 2>/dev/null || true
print_success "Container antigo removido"

echo ""
print_info "Iniciando novo container..."
print_info "Porta: $HOST_PORT -> $CONTAINER_PORT"

docker run -d \
  --name $CONTAINER_NAME \
  --restart unless-stopped \
  --network $NETWORK \
  -p $HOST_PORT:$CONTAINER_PORT \
  -e DATABASE_URL="${DATABASE_URL}" \
  -e SECRET_KEY="${SECRET_KEY}" \
  -e MINIO_ENDPOINT="${MINIO_ENDPOINT:-minio:9000}" \
  -e MINIO_SECURE="${MINIO_SECURE:-false}" \
  -e MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY}" \
  -e MINIO_SECRET_KEY="${MINIO_SECRET_KEY}" \
  -e MINIO_BUCKET="${MINIO_BUCKET:-sgpi-files}" \
  -e MINIO_PUBLIC_ENDPOINT="${MINIO_PUBLIC_ENDPOINT}" \
  -e MINIO_PUBLIC_SECURE="${MINIO_PUBLIC_SECURE:-false}" \
  -e ENVIRONMENT="${ENVIRONMENT:-production}" \
  $IMAGE_NAME || {
    print_error "Falha ao iniciar container"
    exit 1
}

print_success "Container iniciado: $CONTAINER_NAME"

echo ""
print_info "Aguardando container inicializar..."
sleep 10

echo ""
print_info "Verificando status do container..."
if docker ps | grep -q $CONTAINER_NAME; then
    print_success "Container está rodando!"
    echo ""
    docker ps --filter name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    print_error "Container não está rodando!"
    echo ""
    print_info "Últimas 50 linhas do log:"
    docker logs --tail 50 $CONTAINER_NAME
    exit 1
fi

echo ""
print_info "Últimas 20 linhas do log:"
docker logs --tail 20 $CONTAINER_NAME

echo ""
print_info "Limpando imagens antigas..."
docker image prune -af --filter "until=24h" || true

echo ""
echo -e "${BLUE}==================================${NC}"
print_success "Deploy realizado com sucesso! 🎉"
echo -e "${BLUE}==================================${NC}"
echo ""
echo "Container: $CONTAINER_NAME"
echo "Porta: $HOST_PORT"
echo "API URL: http://localhost:$HOST_PORT"
echo "Docs: http://localhost:$HOST_PORT/docs"
echo ""
echo "Para ver logs:"
echo "  docker logs -f $CONTAINER_NAME"
echo ""
echo "Para parar o container:"
echo "  docker stop $CONTAINER_NAME"
echo ""

