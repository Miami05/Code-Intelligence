"""Sprint 14: CI/CD tables

Revision ID: sprint14_cicd
Revises: 002_performance
Create Date: 2026-02-20
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "sprint14_cicd"
down_revision = "002_performance"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "quality_gates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "repository_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("max_complexity", sa.Integer(), server_default="10"),
        sa.Column("max_code_smells", sa.Integer(), server_default="20"),
        sa.Column("max_critical_smells", sa.Integer(), server_default="0"),
        sa.Column("max_vulnerabilities", sa.Integer(), server_default="5"),
        sa.Column("max_critical_vulnerabilities", sa.Integer(), server_default="0"),
        sa.Column("min_quality_score", sa.Float(), server_default="70.0"),
        sa.Column("max_duplication_percentage", sa.Float(), server_default="10.0"),
        sa.Column("block_on_failure", sa.Boolean(), server_default="true"),
    )

    op.create_table(
        "cicd_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "repository_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("repositories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("branch", sa.String(255), nullable=True),
        sa.Column("commit_sha", sa.String(40), nullable=True),
        sa.Column("pr_number", sa.Integer(), nullable=True),
        sa.Column("pr_title", sa.String(500), nullable=True),
        sa.Column("triggered_by", sa.String(50), server_default="manual"),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("quality_gate_passed", sa.Boolean(), nullable=True),
        sa.Column("quality_gate_details", postgresql.JSONB(), nullable=True),
        sa.Column("report_html", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("idx_cicd_runs_repo", "cicd_runs", ["repository_id"])
    op.create_index("idx_cicd_runs_status", "cicd_runs", ["status"])
    op.create_index("idx_cicd_runs_created", "cicd_runs", ["created_at"])


def downgrade():
    op.drop_index("idx_cicd_runs_created", table_name="cicd_runs")
    op.drop_index("idx_cicd_runs_status", table_name="cicd_runs")
    op.drop_index("idx_cicd_runs_repo", table_name="cicd_runs")
    op.drop_table("cicd_runs")
    op.drop_table("quality_gates")
