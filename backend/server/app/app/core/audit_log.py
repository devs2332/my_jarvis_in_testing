"""
Audit logging for security-sensitive operations.
"""

import logging
import json
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("audit")


def audit_log(
    action: str,
    user_id: Optional[str] = None,
    resource: Optional[str] = None,
    detail: Optional[dict] = None,
    ip_address: Optional[str] = None,
    status: str = "success",
) -> None:
    """
    Write a structured audit log entry.
    In production, this should be forwarded to a SIEM or dedicated audit store.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "user_id": user_id,
        "resource": resource,
        "status": status,
        "ip_address": ip_address,
        "detail": detail or {},
    }
    logger.info(json.dumps(entry))
