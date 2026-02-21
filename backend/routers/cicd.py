import hashlib
import hmac
import uuid
from typing import Optional

from config import settings
from database import get_db
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from models import repository
from models.cicd_run import CICDRun
from models.quality_gate import QualityGate
from models.repository import Repository
from pydantic import BaseModel
from services.cicd_service import CICDService
from services.notification_service import NotificationService
from services.report_service import ReportService
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/cicd", tags=["CI/CD"])

cicd_service = CICDService()
report_service = ReportService()
notification_service = NotificationService()


class QualityGateConfig(BaseModel):
    max_complexity: int = 10
    max_code_smells: int = 20
    max_critical_smells: int = 0
    max_vulnerabilities: int = 5
    max_critical_vulnerabilities: int = 0
    min_quality_score: float = 70.0
    max_duplication_percentage: float = 10.0
    block_on_failure: bool = True


class SlackNotifyRequest(BaseModel):
    repository_id: uuid.UUID
    webhook_url: str
    run_url: Optional[str] = None


class EmailNotifyRequest(BaseModel):
    repository_id: uuid.UUID
    to_email: str


@router.post("/webhook/github")
async def webhook_github(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    body = await request.body()
    if settings.github_webhook_secret:
        sig = (
            "sha256="
            + hmac.new(
                settings.github_webhook_secret.encode(), body, hashlib.sha256
            ).hexdigest()
        )
        if not hmac.compare_digest(sig, x_hub_signature_256 or ""):
            raise HTTPException(status_code=401, detail="Invalid signature")
    if x_github_event != "pull_request":
        return {"status": "ignored", "event": x_github_event}
    payload = await request.json()
    action = payload.get("action", "")
    if action not in ["opened", "synchronize", "reopened"]:
        return {"status": "ignored", "action": action}
    pr = payload.get("pull_request", {})
    full_name = payload.get("repository", {}).get("full_name", "")
    repo = db.query(Repository).filter(Repository.github_repo_name == full_name).first()
    if not repo:
        return {"status": "skipped", "reason": "repository not tracked"}
    run = cicd_service.create_run(
        db,
        repository_id=repo.id,
        branch=pr.get("head", {}).get("ref"),
        commit_sha=pr.get("head", {}).get("sha"),
        pr_number=pr.get("number"),
        pr_title=pr.get("title"),
        triggered_by="github",
        status="running",
    )
    gate_result = cicd_service.run_quality_gate(db, repo.id)
    html = report_service.generate_html_report(repo.name, gate_result)
    cicd_service.complete_run(db, run, gate_result, html)
    return {
        "status": "completed",
        "run_id": str(run.id),
        "quality_gate": gate_result["passed"],
        "block_merge": gate_result["block_merge"],
        "summary": gate_result["summary"],
    }
