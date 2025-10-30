#!/bin/bash

# Script para verificar a saúde da API SGPI

set -e

# Configurações
API_URL="${1:-http://localhost:8009}"
TIMEOUT=10

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================="
echo "🏥 SGPI API - Health Check"
echo -e "==================================${NC}"
echo ""

# Função para verificar endpoint
check_endpoint() {
    local endpoint=$1
    local description=$2
    
    echo -n "Verificando $description... "
    
    if curl -sf --max-time $TIMEOUT "$API_URL$endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FALHOU${NC}"
        return 1
    fi
}

# Verificar conectividade básica
echo -n "Conectividade com $API_URL... "
if curl -sf --max-time $TIMEOUT "$API_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FALHOU${NC}"
    echo ""
    echo -e "${RED}Não foi possível conectar à API em $API_URL${NC}"
    echo "Verifique se a aplicação está rodando."
    exit 1
fi

echo ""

# Verificar endpoints principais
FAILED=0

check_endpoint "/docs" "Documentação Swagger" || FAILED=$((FAILED + 1))
check_endpoint "/redoc" "Documentação ReDoc" || FAILED=$((FAILED + 1))
check_endpoint "/openapi.json" "OpenAPI Schema" || FAILED=$((FAILED + 1))

echo ""
echo -e "${BLUE}Verificando endpoints da API...${NC}"

# Estes podem retornar 401/403 mas devem responder
echo -n "Verificando /auth/login... "
STATUS=$(curl -sf --max-time $TIMEOUT -o /dev/null -w "%{http_code}" "$API_URL/auth/login" -X POST -H "Content-Type: application/json" -d '{}' 2>/dev/null || echo "000")
if [ "$STATUS" != "000" ]; then
    echo -e "${GREEN}✅ OK${NC} (HTTP $STATUS)"
else
    echo -e "${RED}❌ FALHOU${NC}"
    FAILED=$((FAILED + 1))
fi

echo -n "Verificando /patents... "
STATUS=$(curl -sf --max-time $TIMEOUT -o /dev/null -w "%{http_code}" "$API_URL/patents" 2>/dev/null || echo "000")
if [ "$STATUS" != "000" ]; then
    echo -e "${GREEN}✅ OK${NC} (HTTP $STATUS)"
else
    echo -e "${RED}❌ FALHOU${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""

# Verificar container Docker (se aplicável)
if command -v docker &> /dev/null; then
    echo -e "${BLUE}Verificando container Docker...${NC}"
    
    if docker ps --format '{{.Names}}' | grep -q "api-sgpi"; then
        echo -e "${GREEN}✅ Container api-sgpi está rodando${NC}"
        
        # Mostrar informações do container
        echo ""
        echo "Informações do container:"
        docker ps --filter name=api-sgpi --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        echo ""
        echo "Últimas 5 linhas do log:"
        docker logs --tail 5 api-sgpi 2>&1
    else
        echo -e "${YELLOW}⚠️  Container api-sgpi não está rodando${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Docker não está disponível${NC}"
fi

echo ""
echo -e "${BLUE}==================================${NC}"

# Resultado final
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Todas as verificações passaram!${NC}"
    echo -e "${GREEN}🎉 A API está saudável e funcionando corretamente.${NC}"
    exit 0
else
    echo -e "${RED}❌ $FAILED verificação(ões) falharam${NC}"
    echo -e "${YELLOW}Verifique os logs da aplicação para mais detalhes.${NC}"
    exit 1
fi

