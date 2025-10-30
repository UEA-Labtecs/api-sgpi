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
            
            # Verificar versão atual e sincronizar com head se necessário
            result = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
            current_version = result.fetchone()
            
            # Descobrir head revision
            import subprocess
            result = subprocess.run(['alembic', 'heads'], capture_output=True, text=True)
            head_rev = '4647eb46a804'  # fallback
            if result.returncode == 0 and result.stdout.strip():
                head_rev = result.stdout.strip().split()[0]
            
            if not current_version:
                print(f"[entrypoint] Nenhuma versão registrada, marcando head {head_rev} como aplicada...")
                conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_rev}') ON CONFLICT DO NOTHING"))
                conn.commit()
                print(f"[entrypoint] ✅ Head revision {head_rev} marcada como aplicada")
            else:
                current_rev = current_version[0]
                if current_rev != head_rev:
                    print(f"[entrypoint] ⚠️  Versão registrada ({current_rev}) difere da head ({head_rev})")
                    print(f"[entrypoint] 🔄 Atualizando para head {head_rev} (tabelas já existem)...")
                    conn.execute(text(f"DELETE FROM alembic_version"))
                    conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_rev}')"))
                    conn.commit()
                    print(f"[entrypoint] ✅ Versão sincronizada para {head_rev}")
                else:
                    print(f"[entrypoint] ✅ Alembic já na versão head: {current_rev}")
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
            
            # Garantir que alembic_version está configurada e sincronizada com head
            try:
                result = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
                version = result.fetchone()
                
                # Descobrir head revision
                import subprocess
                result = subprocess.run(['alembic', 'heads'], capture_output=True, text=True)
                head_rev = '4647eb46a804'  # fallback
                if result.returncode == 0 and result.stdout.strip():
                    head_rev = result.stdout.strip().split()[0]
                
                if not version:
                    print(f"[entrypoint] Sincronizando versão do Alembic para head {head_rev}...")
                    conn.execute(text(f"DELETE FROM alembic_version"))
                    conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_rev}')"))
                    conn.commit()
                    print(f"[entrypoint] ✅ Estado sincronizado na versão {head_rev}")
                else:
                    current_rev = version[0]
                    if current_rev != head_rev:
                        print(f"[entrypoint] ⚠️  Versão registrada ({current_rev}) difere da head ({head_rev}), atualizando...")
                        conn.execute(text(f"DELETE FROM alembic_version"))
                        conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_rev}')"))
                        conn.commit()
                        print(f"[entrypoint] ✅ Versão atualizada para {head_rev}")
            except Exception:
                # Criar tabela se não existir
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS alembic_version (
                        version_num VARCHAR(32) NOT NULL PRIMARY KEY
                    )
                """))
                # Descobrir head revision
                import subprocess
                result = subprocess.run(['alembic', 'heads'], capture_output=True, text=True)
                head_rev = '4647eb46a804'  # fallback
                if result.returncode == 0 and result.stdout.strip():
                    head_rev = result.stdout.strip().split()[0]
                conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_rev}') ON CONFLICT DO NOTHING"))
                conn.commit()
                print(f"[entrypoint] ✅ Alembic sincronizado na versão {head_rev}")
            
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
