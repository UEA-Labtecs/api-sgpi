from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from playwright.sync_api import sync_playwright
import subprocess


# 🔧 Instala Playwright se não tiver
try:
    subprocess.run(["playwright", "install", "chromium"], check=True)
except Exception as e:
    print(f"Erro na instalação do navegador: {e}")


app = FastAPI(title="Crawler INPI API", version="1.0.0")


class Patente(BaseModel):
    numero_pedido: Optional[str]
    data_deposito: Optional[str]
    data_publicacao: Optional[str]
    data_concessao: Optional[str]
    classificacao_ipc: Optional[List[str]]
    classificacao_cpc: Optional[List[str]]
    titulo: Optional[str]
    resumo: Optional[str]
    depositante: Optional[str]
    inventores: Optional[str]
    url_detalhe: Optional[str]


def navegar_com_retry(page, url, tentativas=3):
    for tentativa in range(1, tentativas + 1):
        try:
            print(f"Tentando acessar {url} - tentativa {tentativa}")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return
        except Exception as e:
            print(f"⚠️ Tentativa {tentativa} falhou: {e}")
            if tentativa == tentativas:
                raise e


@app.get("/buscar-patentes", response_model=List[Patente])
def buscar_patentes(termo: str = Query(..., description="Termo de busca"), quantidade: int = 1):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        page = context.new_page()
        page.goto('https://busca.inpi.gov.br/pePI/')

        with context.expect_page() as nova_pagina_info:
            page.click('a[href="/pePI/servlet/LoginController?action=login"]')

        nova_pagina = nova_pagina_info.value
        nova_pagina.wait_for_load_state()

        url_busca = "https://busca.inpi.gov.br/pePI/jsp/patentes/PatenteSearchBasico.jsp"
        nova_pagina.goto(url_busca)
        nova_pagina.wait_for_load_state()

        nova_pagina.fill('input[name="ExpressaoPesquisa"]', termo)
        nova_pagina.click('input[value=" pesquisar » "]')
        nova_pagina.wait_for_timeout(4000)

        links = nova_pagina.locator('a').all()
        links_pedidos = [
            link for link in links
            if link.get_attribute('href') and 'PatenteServletController?Action=detail' in link.get_attribute('href')
        ]

        resultados = []

        for link in links_pedidos[:quantidade]:
            href = link.get_attribute('href')
            url_detalhe = f"https://busca.inpi.gov.br{href}" if href.startswith('/') else f"https://busca.inpi.gov.br/pePI/{href}"

            try:
                navegar_com_retry(nova_pagina, url_detalhe)

                def pega_texto(selector):
                    try:
                        texto = nova_pagina.locator(selector).inner_text().strip()
                        return texto if texto and texto != "-" else None
                    except:
                        return None

                numero_pedido = pega_texto('font.marcador')
                titulo = pega_texto('#tituloContext')
                resumo = pega_texto('#resumoContext')
                data_deposito = pega_texto('xpath=//td[font[contains(text(),"(22)")]]/following-sibling::td/font')
                data_publicacao = pega_texto('xpath=//td[font[contains(text(),"(43)")]]/following-sibling::td/font')
                data_concessao = pega_texto('xpath=//td[font[contains(text(),"(47)")]]/following-sibling::td/font')
                depositante = pega_texto('xpath=//td[font[contains(text(),"(71)")]]/following-sibling::td/font')
                inventores = pega_texto('xpath=//td[font[contains(text(),"(72)")]]/following-sibling::td/font')

                ipc = nova_pagina.locator('xpath=//td[font[contains(text(),"(51)")]]/following-sibling::td//a').all()
                classificacao_ipc = [
                    i.inner_text().strip().rstrip(';')
                    for i in ipc if i.inner_text().strip()
                ] if ipc else []

                cpc = nova_pagina.locator('xpath=//td[font[contains(text(),"(52)")]]/following-sibling::td//a').all()
                classificacao_cpc = [
                    i.inner_text().strip().rstrip(';')
                    for i in cpc if i.inner_text().strip()
                ] if cpc else []

                resultado = {
                    "numero_pedido": numero_pedido,
                    "data_deposito": data_deposito,
                    "data_publicacao": data_publicacao,
                    "data_concessao": data_concessao,
                    "classificacao_ipc": classificacao_ipc if classificacao_ipc else None,
                    "classificacao_cpc": classificacao_cpc if classificacao_cpc else None,
                    "titulo": titulo,
                    "resumo": resumo,
                    "depositante": depositante,
                    "inventores": inventores,
                    "url_detalhe": url_detalhe,
                }

                resultados.append(resultado)

            except Exception as e:
                print(f"❌ Erro ao processar {url_detalhe}. Pulando... {e}")
                continue  # Vai para o próximo link

            nova_pagina.go_back()
            nova_pagina.wait_for_timeout(2000)

        browser.close()
        return resultados
