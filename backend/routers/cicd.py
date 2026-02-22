import hashlib
import hmac
import uuid
from typing import Optional

from config import settings
from database import get_db
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from models.cicd_run import CICDRun
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


@router.post("/webhook.gitlab")
async def gitlab_webhook(
    request: Request,
    x_gitlab_event: Optional[str] = Header(None),
    x_gitlab_token: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    if (
        settings.gitlab_webhook_token
        and x_gitlab_token != settings.gitlab_webhook_token
    ):
        raise HTTPException(status_code=401, detail="Invalid GitLab token")
    if x_gitlab_event != "Merge Request Hook":
        return {"status": "ignored", "event": x_gitlab_event}
    payload = await request.json()
    attrs = payload.get("object_attributes", {})
    if attrs.get("action") not in ["open", "update", "reopen"]:
        return {"status": "ignored", "action": attrs.get("action")}
    repo_path = payload.get("project", {}).get("path_with_namespace", "")
    repo = db.query(Repository).filter(Repository.github_repo_name == repo_path).first()
    if not repo:
        return {"status": "skipped", "reason": "repository not tracked"}
    run = cicd_service.create_run(
        db,
        repository_id=repo.id,
        branch=attrs.get("source_branch"),
        commit_sha=(attrs.get("last_commit") or {}).get("id"),
        pr_number=attrs.get("iid"),
        pr_title=attrs.get("title"),
        triggered_by="gitlab",
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
    }


@router.get("/quality-gate/{repository_id}")
def get_quality_gate(repository_id: uuid.UUID, db: Session = Depends(get_db)):
    return cicd_service.get_or_create_quality_gate(db, repository_id)


@router.put("/quality-gate/{repository_id}")
def update_quality_gate(
    repository_id: uuid.UUID, config: QualityGateConfig, db: Session = Depends(get_db)
):
    gate = cicd_service.get_or_create_quality_gate(db, repository_id)
    for field, value in config.dict().items():
        setattr(gate, field, value)
    db.commit()
    db.refresh(gate)
    return gate


@router.post("/quality-gate/{repository_id}/check")
def check_quality_gate(repository_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    result = cicd_service.run_quality_gate(db, repository_id)
    run = cicd_service.create_run(
        db, repository_id=repository_id, triggered_by="manual", status="runnning"
    )
    html = report_service.generate_html_report(repo.name, result)
    cicd_service.complete_run(db, run, result, html)
    return {**result, "run.id": str(run.id)}


@router.get("/report/{run_id}", response_class=HTMLResponse)
def get_report(run_id: uuid.UUID, db: Session = Depends(get_db)):
    run = db.query(CICDRun).filter(CICDRun.id == run_id).first()
    if not run or not run.report_html:
        raise HTTPException(status_code=404, detail="Report not found")
    return HTMLResponse(content=run.report_html)


@router.get("/runs/{repository_id}")
def get_runs(repository_id: uuid.UUID, limit: int = 20, db: Session = Depends(get_db)):
    return (
        db.query(CICDRun)
        .filter(CICDRun.repository_id == repository_id)
        .order_by(CICDRun.created_at.desc())
        .limit(limit)
        .all()
    )


@router.post("/notify/slack")
async def notify_slack(req: SlackNotifyRequest, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == req.repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    result = cicd_service.run_quality_gate(db, req.repository_id)
    sent = await notification_service.send_slack(
        req.webhook_url, repo.name, result, req.run_url
    )
    return {"sent": sent, "quality_gate": result["passed"]}


@router.post("/notify/email")
def notify_email(req: EmailNotifyRequest, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == req.repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    result = cicd_service.run_quality_gate(db, req.repository_id)
    html = report_service.generate_html_report(repo.name, result)
    sent = notification_service.send_email(req.to_email, repo.name, result, html)
    return {"sent": sent, "quality_gate": result["passed"]}
