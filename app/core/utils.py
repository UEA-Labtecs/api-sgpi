def _scope_user_patents_query(db, current_user):
    from app.models.userPatents import UserPatent
    role = (current_user.role or "").lower()
    q = db.query(UserPatent)
    if role in ("viewer", "read_only", "leitor", "admin"):
        return q
    else:
        return q.filter(UserPatent.owner_id == current_user.id)