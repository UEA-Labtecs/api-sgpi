from typing import Optional
from sqlalchemy.orm import Session
from app.models.patent import Patent

def run_crawler(db: Session, termo: str, quantidade: int, user_patent_id: Optional[int] = None):
    from ..crawler.crawler import crawler_logic

    results = crawler_logic(termo, quantidade)

    patents = []
    for item in results:
        patent = Patent(**item, user_patent_id=user_patent_id)
        db.add(patent)
        patents.append(patent)

    db.commit()
    return patents
