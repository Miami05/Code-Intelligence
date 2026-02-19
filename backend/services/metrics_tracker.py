"""Metrics History Tracking Service"""

import re
import uuid
from datetime import datetime
from typing import List

from models.code_duplication import CodeDuplication
from models.code_smell import CodeSmell
from models.file import File
from models.metrics_history import MetricsSnapshot
from models.symbol import Symbol
from models.vulnerability import Vulnerability
from sqlalchemy import distinct, func, case
from sqlalchemy.orm import Session


class MetricsTracker:
    """Tracks code quality metrics over time"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_qualty_score(self, metrics: dict) -> float:
        """
        Calculate overall quality score (0-100) based on various metrics.

        Formula weights:
        - Complexity: 25%
        - Duplications: 25%
        - Code Smells: 25%
        - Vulnerabilities: 25%
        """
        score = 100.0
        if metrics.get("avg_complexity", 0) > 10:
            complexity_penalty = min(25, (metrics["avg_complexity"] - 10) * 2)
            score -= complexity_penalty
        dup_percentage = metrics.get("duplication_percentage", 0)
        if dup_percentage > 3:
            dup_penalty = min(25, (dup_percentage - 3) * 5)
            score -= dup_penalty
        total_smells = metrics.get("code_smells_count", 0)
        if total_smells > 0:
            smell_penalty = min(25, total_smells * 0.5)
            score -= smell_penalty
        critical_vulns = metrics.get("critical_vulnerabilities", 0)
        high_vulns = metrics.get("high_vulnerabilities", 0)
        vuln_penalty = min(25, critical_vulns * 5 + high_vulns * 2)
        score -= vuln_penalty
        return max(0.0, score)

    async def create_snapshot(self, repository_id: uuid.UUID) -> MetricsSnapshot:
        """Create a new metrics snapshot for a repository"""
        metrics = {}
        file_stats = (
            self.db.query(
                func.count(distinct(File.id)).label("total_files"),
                func.sum(File.line_count).label("total_lines"),
            )
            .filter(File.repository_id == repository_id)
            .one()
        )
        metrics["total_files"] = int(file_stats.total_files or 0)
        metrics["total_lines"] = int(file_stats.total_lines or 0)
        
        complexity_stats = (
            self.db.query(
                func.avg(Symbol.cyclomatic_complexity).label("avg_complexity"),
                func.max(Symbol.cyclomatic_complexity).label("max_complexity"),
                func.count(Symbol.id).label("high_complexity_count"),
            )
            .join(File, Symbol.file_id == File.id)
            .filter(
                File.repository_id == repository_id,
                Symbol.cyclomatic_complexity > 10,
            )
            .one()
        )
        metrics["avg_complexity"] = float(complexity_stats.avg_complexity or 0.0)
        metrics["max_complexity"] = float(complexity_stats.max_complexity or 0.0)
        metrics["high_complexity_count"] = float(
            complexity_stats.high_complexity_count or 0.0
        )
        
        dup_stats = (
            self.db.query(
                func.count(CodeDuplication.id).label("count"),
                func.sum(CodeDuplication.duplicated_lines).label("lines"),
            )
            .filter_by(repository_id=repository_id)
            .one()
        )
        metrics["duplication_count"] = dup_stats.count or 0
        metrics["duplicate_lines"] = dup_stats.lines or 0
        metrics["duplication_percentage"] = (
            (metrics["duplicate_lines"] / metrics["total_lines"] * 100)
            if metrics["total_lines"] > 0
            else 0.0
        )
        
        smell_stats = (
            self.db.query(
                func.count(CodeSmell.id).label("total"),
                func.sum(
                    case((CodeSmell.severity == "critical", 1), else_=0)
                ).label("critical"),
                func.sum(case((CodeSmell.severity == "high", 1), else_=0)).label(
                    "high"
                ),
                func.sum(case((CodeSmell.severity == "medium", 1), else_=0)).label(
                    "medium"
                ),
                func.sum(case((CodeSmell.severity == "low", 1), else_=0)).label(
                    "low"
                ),
            )
            .filter_by(repository_id=repository_id)
            .one()
        )
        metrics["code_smells_count"] = smell_stats.total or 0
        metrics["critical_smells"] = smell_stats.critical or 0
        metrics["high_smells"] = smell_stats.high or 0
        metrics["medium_smells"] = smell_stats.medium or 0
        metrics["low_smells"] = smell_stats.low or 0

        vuln_stats = (
            self.db.query(
                func.count(Vulnerability.id).label("total"),
                func.sum(
                    case((Vulnerability.severity == "critical", 1), else_=0)
                ).label("critical"),
                func.sum(
                    case((Vulnerability.severity == "high", 1), else_=0)
                ).label("high"),
            )
            .filter_by(repository_id=repository_id)
            .one()
        )
        metrics["vulnerability_count"] = vuln_stats.total or 0
        metrics["critical_vulnerabilities"] = vuln_stats.critical or 0
        metrics["high_vulnerabilities"] = vuln_stats.high or 0
        
        metrics["quality_score"] = self.calculate_qualty_score(metrics)
        snapshot = MetricsSnapshot(repository_id=repository_id, **metrics)
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def get_history(
        self, repository_id: uuid.UUID, limit: int = 30
    ) -> List[MetricsSnapshot]:
        """Get metrics history for a repository"""
        snapshot = (
            self.db.query(MetricsSnapshot)
            .filter_by(repository_id=repository_id)
            .order_by(MetricsSnapshot.created_at.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(snapshot))
