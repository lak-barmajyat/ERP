from __future__ import annotations

import os
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from .sql.sql_db_tables import AuditLog


_AUDIT_ACTIONS = {"INSERT", "UPDATE", "DELETE", "STATUS_CHANGE"}


def get_current_user_id() -> Optional[int]:
    raw = (os.getenv("USER_ID") or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def log_audit_event(
    session: Session,
    *,
    table_name: str,
    record_id: str | int,
    action: str,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    comment: Optional[str] = None,
    user_id: Optional[int] = None,
    ip_client: Optional[str] = None,
) -> AuditLog:
    """Add one audit_log row to the current session.

    Notes:
    - Does not commit; caller controls transaction boundaries.
    - `record_id` is stored as string in DB.
    """
    if session is None:
        raise ValueError("session is required")

    action_value = (action or "").strip().upper()
    if action_value not in _AUDIT_ACTIONS:
        raise ValueError(f"Invalid audit action: {action}")

    table_value = (table_name or "").strip()
    if not table_value:
        raise ValueError("table_name is required")

    record_value = str(record_id).strip()
    if not record_value:
        raise ValueError("record_id is required")

    audit = AuditLog(
        id_utilisateur=int(user_id) if user_id is not None else get_current_user_id(),
        table_name=table_value,
        record_id=record_value,
        action=action_value,
        old_values_json=old_values,
        new_values_json=new_values,
        commentaire=(comment or "").strip() or None,
        ip_client=(ip_client or "").strip() or None,
    )

    session.add(audit)
    return audit
