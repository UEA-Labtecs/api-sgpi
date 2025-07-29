from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session
from app.models.patent import Patent
from app.schemas.patent import PatentSchema

def run_crawler(db: Session, termo: str, quantidade: int):
    from ..crawler.crawler import crawler_logic

    results = crawler_logic(termo, quantidade)

    patents = []
    for item in results:
        patent = Patent(**item)
        db.add(patent)
        patents.append(patent)

    db.commit()
    return patents
