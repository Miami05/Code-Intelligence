"""
Security scanning API endpoints.
"""

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models.file import File
from models.repository import Repository
from models.vulnerability import Vulnerability
from services.security_scanner import SecurityScanner

router = APIRouter(prefix="/api/security", tags=["security"])


@router.post("/repositories/{repository_id}/scan")
def scan_repository_security(
    repository_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    Trigger security scan for a repository.
    Scans all files and stores vulnerabilities in database.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    db.query(Vulnerability).filter(
        Vulnerability.repository_id == repository_id
    ).delete()
    db.commit()
    background_tasks.add_task(_perform_security_scan, repository_id, db)
    return {
        "status": "scanning",
        "message": "Security scan started",
        "repository_id": repository_id,
    }


def _perform_security_scan(repository_id: str, db: Session):
    """Background task: Perform security scan on repository"""
    scanner = SecurityScanner()
    files = (
        db.query(File)
        .filter(File.repository_id == repository_id, File.source.isnot(None))
        .all()
    )
    total_issues = 0
    for file in files:
        if file.source is None:
            continue
        issues = scanner.scan_file(file.file_path, file.source, file.language)
        for issue in issues:
            vuln = Vulnerability(
                repository_id=repository_id,
                type=issue.type,
                severity=issue.severity,
                cwe_id=issue.cwe_id,
                owasp_category=issue.owasp_category,
                file_path=file.file_path,
                line_number=issue.line_number,
                code_snippet=issue.code_snippet,
                description=issue.description,
                recommendation=issue.recommendation,
                confidence=issue.confidence,
            )
            db.add(vuln)
            total_issues += 1
    db.commit()
    print(f"✅ Security scan complete: {total_issues} vulnerabilities found")


@router.get("/repositories/{repository_id}/vulnerabilities")
def get_vulnerabilities(
    repository_id: str,
    severity: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get all vulnerabilities for a repository.
    Supports filtering by severity and type.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    vuln_query = db.query(Vulnerability).filter(
        Vulnerability.repository_id == repository_id
    )
    if severity is not None:
        vuln_query = vuln_query.filter(Vulnerability.severity == severity)
    if type is not None:
        vuln_query = vuln_query.filter(Vulnerability.type == type)

    vulnerabilities = vuln_query.order_by(
        Vulnerability.severity.desc(), Vulnerability.created_at.desc()
    ).all()

    return {
        "repository_id": repository_id,
        "total_vulnerabilities": len(vulnerabilities),
        "vulnerabilities": [
            {
                "id": str(vuln.id),
                "type": vuln.type,
                "severity": vuln.severity,
                "cwe_id": vuln.cwe_id,
                "owasp_category": vuln.owasp_category,
                "file_path": vuln.file_path,
                "line_number": vuln.line_number,
                "code_snippet": vuln.code_snippet,
                "description": vuln.description,
                "recommendation": vuln.recommendation,
                "confidence": vuln.confidence,
                "created_at": vuln.created_at.isoformat(),
            }
            for vuln in vulnerabilities
        ],
    }


@router.get("/repositories/{repository_id}/security-stats")
def get_security_stats(repository_id: str, db: Session = Depends(get_db)):
    """
    Get security statistics for dashboard cards.
    """
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    critical_count = (
        db.query(func.count(Vulnerability.id))
        .filter(
            Vulnerability.repository_id == repository_id,
            Vulnerability.severity == "critical",
        )
        .scalar()
        or 0
    )
    high_count = (
        db.query(func.count(Vulnerability.id))
        .filter(
            Vulnerability.repository_id == repository_id,
            Vulnerability.severity == "high",
        )
        .scalar()
        or 0
    )
    medium_count = (
        db.query(func.count(Vulnerability.id))
        .filter(
            Vulnerability.repository_id == repository_id,
            Vulnerability.severity == "medium",
        )
        .scalar()
        or 0
    )
    low_count = (
        db.query(func.count(Vulnerability.id))
        .filter(
            Vulnerability.repository_id == repository_id,
            Vulnerability.severity == "low",
        )
        .scalar()
        or 0
    )
    type_counts = (
        db.query(Vulnerability.type, func.count(Vulnerability.id).label("count"))
        .filter(Vulnerability.repository_id == repository_id)
        .group_by(Vulnerability.type)
        .all()
    )
    return {
        "repository_id": repository_id,
        "total_vulnerabilities": critical_count + high_count + medium_count + low_count,
        "by_severity": {
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
        },
        "by_type": {t.type: t.count for t in type_counts},
    }
