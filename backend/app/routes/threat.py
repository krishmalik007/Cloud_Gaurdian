from fastapi import APIRouter, Depends

from app.auth.permissions import require_role
from app.services.threat_service import threat_service

router = APIRouter(
    prefix="/threat",
    tags=["Threat Intelligence"]
)


# ------------------------------------
# Get All IOC Lists
# ------------------------------------
@router.get("/iocs")
async def get_iocs(
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve all locally configured Indicators of Compromise (IOCs).
    """

    return threat_service.get_all_iocs()


# ------------------------------------
# Check IP
# ------------------------------------
@router.get("/ip/{ip}")
async def check_ip(
    ip: str,
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Check whether an IP is malicious.
    """

    return threat_service.check_ip(ip)


# ------------------------------------
# Check Domain
# ------------------------------------
@router.get("/domain/{domain}")
async def check_domain(
    domain: str,
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Check whether a domain is malicious.
    """

    return threat_service.check_domain(domain)


# ------------------------------------
# Check Username
# ------------------------------------
@router.get("/user/{username}")
async def check_username(
    username: str,
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Check whether a username is suspicious.
    """

    return threat_service.check_username(username)