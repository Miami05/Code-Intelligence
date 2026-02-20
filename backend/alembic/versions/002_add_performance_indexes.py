"""Add performance indexes for Sprint 10

Revision ID: 002_performance
Revises: 001_initial
Create Date: 2026-02-19
"""

from alembic import op

revision = "002_performance"
down_revision = "001_initial"  # Update with your actual previous revision


def upgrade():
    # Files table indexes
    op.create_index("idx_files_repo_id", "files", ["repository_id"])
    op.create_index("idx_files_path", "files", ["path"])
    op.create_index("idx_files_language", "files", ["language"])
    op.create_index(
        "idx_files_repo_path", "files", ["repository_id", "path"], unique=True
    )

    # Symbols table indexes
    op.create_index("idx_symbols_file_id", "symbols", ["file_id"])
    op.create_index("idx_symbols_name", "symbols", ["name"])
    op.create_index("idx_symbols_type", "symbols", ["type"])
    op.create_index("idx_symbols_file_name", "symbols", ["file_id", "name"])

    # Embeddings table indexes
    op.create_index("idx_embeddings_file_id", "embeddings", ["file_id"])
    op.create_index("idx_embeddings_symbol_id", "embeddings", ["symbol_id"])

    # Call relationships indexes
    op.create_index("idx_call_rel_caller", "call_relationships", ["caller_id"])
    op.create_index("idx_call_rel_callee", "call_relationships", ["callee_id"])
    op.create_index("idx_call_rel_repo", "call_relationships", ["repository_id"])

    # Code smells indexes
    op.create_index("idx_code_smells_file", "code_smells", ["file_id"])
    op.create_index("idx_code_smells_severity", "code_smells", ["severity"])
    op.create_index("idx_code_smells_type", "code_smells", ["smell_type"])

    # Vulnerabilities indexes
    op.create_index("idx_vulnerabilities_repo", "vulnerabilities", ["repository_id"])
    op.create_index("idx_vulnerabilities_severity", "vulnerabilities", ["severity"])

    # Metrics history indexes
    op.create_index("idx_metrics_repo", "metrics_history", ["repository_id"])
    op.create_index("idx_metrics_timestamp", "metrics_history", ["captured_at"])
    op.create_index(
        "idx_metrics_repo_time", "metrics_history", ["repository_id", "captured_at"]
    )


def downgrade():
    # Drop all indexes
    op.drop_index("idx_files_repo_id", table_name="files")
    op.drop_index("idx_files_path")
    op.drop_index("idx_files_language")
    op.drop_index("idx_files_repo_path")
    op.drop_index("idx_symbols_file_id")
    op.drop_index("idx_symbols_name")
    op.drop_index("idx_symbols_type")
    op.drop_index("idx_symbols_file_name")
    op.drop_index("idx_embeddings_file_id")
    op.drop_index("idx_embeddings_symbol_id")
    op.drop_index("idx_call_rel_caller")
    op.drop_index("idx_call_rel_callee")
    op.drop_index("idx_call_rel_repo")
    op.drop_index("idx_code_smells_file")
    op.drop_index("idx_code_smells_severity")
    op.drop_index("idx_code_smells_type")
    op.drop_index("idx_vulnerabilities_repo")
    op.drop_index("idx_vulnerabilities_severity")
    op.drop_index("idx_metrics_repo")
    op.drop_index("idx_metrics_timestamp")
    op.drop_index("idx_metrics_repo_time")
