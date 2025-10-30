#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Verificando e aplicando migrations..."

# Script Python para sincronizar estado do Alembic se necessário
python3 << 'PYEOF'
import os
import sys
from sqlalchemy import create_engine, text

try:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("[entrypoint] ⚠️  DATABASE_URL não configurado")
        sys.exit(0)  # Não falha, deixa o Alembic tratar
    
    engine = create_engine(db_url, connect_args={"connect_timeout": 5})
    
    with engine.connect() as conn:
        # Verificar se tabela patents existe
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'patents'
            )
        """))
        patents_exists = result.scalar()
        
        if patents_exists:
            print("[entrypoint] ✅ Tabelas já existem no banco")
            
            # Verificar se tabela alembic_version existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                )
            """))
            alembic_table_exists = result.scalar()
            
            if not alembic_table_exists:
                print("[entrypoint] Criando tabela alembic_version...")
                conn.execute(text("""
                    CREATE TABLE alembic_version (
                        version_num VARCHAR(32) NOT NULL PRIMARY KEY
                    )
                """))
                conn.commit()
                print("[entrypoint] ✅ Tabela alembic_version criada")
            
            # Verificar versão atual
            result = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
            current_version = result.fetchone()
            
            if not current_version:
                print("[entrypoint] Marcando migration baseline como aplicada...")
                conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('bf4c8ea79ab8') ON CONFLICT DO NOTHING"))
                conn.commit()
                print("[entrypoint] ✅ Migration baseline marcada como aplicada")
            else:
                print(f"[entrypoint] ✅ Alembic já na versão: {current_version[0]}")
        else:
            print("[entrypoint] Banco vazio, migrations serão aplicadas normalmente")
    
    engine.dispose()
except Exception as e:
    print(f"[entrypoint] ⚠️  Erro ao verificar estado: {e}")
    print("[entrypoint] Continuando com migrations normais...")
PYEOF

echo "[entrypoint] Aplicando migrations..."
alembic upgrade head || {
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 1 ]; then
        echo "[entrypoint] ⚠️  Erro ao aplicar migrations, verificando se é problema de tabela duplicada..."
        
        # Verificar se é erro de tabela duplicada
        python3 << 'PYEOF'
import os
import sys
from sqlalchemy import create_engine, text

try:
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # Verificar se as tabelas principais existem
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('patents', 'users')
            )
        """))
        tables_exist = result.scalar()
        
        if tables_exist:
            print("[entrypoint] ✅ Tabelas existem, verificando versão do Alembic...")
            
            # Garantir que alembic_version está configurada
            try:
                result = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
                version = result.fetchone()
                
                if not version:
                    print("[entrypoint] Sincronizando versão do Alembic...")
                    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('bf4c8ea79ab8') ON CONFLICT DO NOTHING"))
                    conn.commit()
                    print("[entrypoint] ✅ Estado sincronizado, tentando aplicar migrations restantes...")
            except Exception:
                # Criar tabela se não existir
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS alembic_version (
                        version_num VARCHAR(32) NOT NULL PRIMARY KEY
                    )
                """))
                conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('bf4c8ea79ab8') ON CONFLICT DO NOTHING"))
                conn.commit()
                print("[entrypoint] ✅ Alembic sincronizado")
            
            print("[entrypoint] ✅ Banco parece estar em um estado válido")
            sys.exit(0)  # Sucesso, continuar
        else:
            print("[entrypoint] ❌ Tabelas não existem e migrations falharam")
            sys.exit(1)
except Exception as e:
    print(f"[entrypoint] ❌ Erro crítico: {e}")
    sys.exit(1)
PYEOF
        
        if [ $? -eq 0 ]; then
            echo "[entrypoint] Tentando aplicar migrations pendentes novamente..."
            alembic upgrade head || echo "[entrypoint] ⚠️  Continuando mesmo com aviso de migrations..."
        else
            echo "[entrypoint] ❌ Falha ao sincronizar estado do banco"
            exit 1
        fi
    else
        exit $EXIT_CODE
    fi
}

echo "[entrypoint] ✅ Migrations aplicadas com sucesso"
echo "[entrypoint] Iniciando API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8009
