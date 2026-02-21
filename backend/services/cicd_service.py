import uuid
from datetime import datetime
from typing import Dict

from models.cicd_run import CICDRun
from models.code_smell import CodeSmell
from models.quality_gate import QualityGate
from models.vulnerability import Vulnerability
from sqlalchemy import func
from sqlalchemy.orm import Session


class CICDService:
    def get_or_create_quality_gate(
        self, db: Session, repository_id: uuid.UUID
    ) -> QualityGate:
        gate = (
            db.query(QualityGate)
            .filter(QualityGate.repository_id == repository_id)
            .first()
        )
        if not gate:
            gate = QualityGate(repository_id=repository_id)
            db.add(gate)
            db.commit()
            db.refresh(gate)
        return gate

    def run_quality_gate(self, db: Session, repository_id: uuid.UUID) -> Dict:
        gate = self.get_or_create_quality_gate(db, repository_id)
        total_smells = (
            db.query(func.count(CodeSmell.id))
            .filter(CodeSmell.repository_id == repository_id)
            .scalar()
        ) or 0
        critical_smells = (
            db.query(func.count(CodeSmell.id))
            .filter(
                CodeSmell.repository_id == repository_id,
                CodeSmell.severity == "critical",
            )
            .scalar()
        ) or 0
        total_vulns = (
            db.query(func.count(Vulnerability.id))
            .filter(Vulnerability.repository_id == repository_id)
            .scalar()
        ) or 0
        critical_vulns = (
            db.query(func.count(Vulnerability.id))
            .filter(
                Vulnerability.repository_id == repository_id,
                Vulnerability.severity == "critical",
            )
            .scalar()
        ) or 0
        checks = []
        passed = True

        def add_check(name, value, threshold):
            nonlocal passed
            ok = value <= threshold
            checks.append(
                {
                    "name": name,
                    "passed": ok,
                    "value": value,
                    "threshold": threshold,
                    "message": f"{value} (max: {threshold})",
                }
            )
            if not ok:
                passed = False

        add_check("Code Smells", total_smells, gate.max_code_smells)
        add_check("Critical Smells", critical_smells, gate.max_critical_smells)
        add_check("Vulnerabilities", total_vulns, gate.max_vulnerabilities)
        add_check(
            "Critical Vulnerabilities",
            critical_vulns,
            gate.max_critical_vulnerabilities,
        )
        ok_counts = sum(1 for c in checks if c["passed"])
        return {
            "passed": passed,
            "block_merge": bool(gate.block_on_failure and not passed),
            "checks": checks,
            "summary": f"{'✅ PASSED' if passed else '❌ FAILED'} — {ok_counts}/{len(checks)} checks passed",
        }

    def create_run(self, db: Session, repository_id: uuid.UUID, **kwargs) -> CICDRun:
        run = CICDRun(repository_id=repository_id, **kwargs)
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    def complete_run(
        self,
        db: Session,
        run: CICDRun,
        gate_result: Dict,
        report_html: str | None = None,
    ):
        run.status = "passed" if gate_result.get("passed") is True else "failed"
        run.quality_gate_passed = gate_result["passed"]
        run.quality_gate_details = gate_result
        run.completed_at = datetime.utcnow()
        if report_html:
            run.report_html = report_html
        db.commit()
        db.refresh(run)
        return run
