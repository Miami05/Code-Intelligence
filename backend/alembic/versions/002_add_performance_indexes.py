"""Add performance indexes for Sprint 10

Revision ID: 002_performance
Revises: merge_heads_final
Create Date: 2026-02-20
"""

from alembic import op

revision = "002_performance"
down_revision = "merge_heads_final"  # ✅ Correct: points to latest merge head
branch_labels = None
depends_on = None


def upgrade():
    # --- files table ---
    # file_path not path (matches File model)
    op.create_index("idx_files_repo_id", "files", ["repository_id"])
    op.create_index("idx_files_file_path", "files", ["file_path"])
    op.create_index("idx_files_language", "files", ["language"])
    op.create_index("idx_files_repo_language", "files", ["repository_id", "language"])

    # --- symbols table ---
    op.create_index("idx_symbols_file_id", "symbols", ["file_id"])
    op.create_index("idx_symbols_name", "symbols", ["name"])
    op.create_index("idx_symbols_type", "symbols", ["type"])
    op.create_index("idx_symbols_file_name", "symbols", ["file_id", "name"])

    # --- embeddings table ---
    # No file_id column — only symbol_id (matches Embedding model)
    op.create_index("idx_embeddings_symbol_id", "embeddings", ["symbol_id"])

    # --- call_relationships table ---
    # Model already defines: idx_caller_symbol_id, idx_callee_symbol_id, idx_repository_calls
    # Only add indexes for columns NOT already indexed by the model
    op.create_index("idx_callrel_caller_name", "call_relationships", ["caller_name"])
    op.create_index("idx_callrel_callee_name", "call_relationships", ["callee_name"])
    op.create_index("idx_callrel_is_external", "call_relationships", ["is_external"])

    # --- code_smells table ---
    op.create_index("idx_code_smells_repo", "code_smells", ["repository_id"])
    op.create_index("idx_code_smells_file_id", "code_smells", ["file_id"])
    op.create_index("idx_code_smells_severity", "code_smells", ["severity"])
    op.create_index("idx_code_smells_type", "code_smells", ["smell_type"])

    # --- vulnerabilities table ---
    op.create_index("idx_vulnerabilities_repo", "vulnerabilities", ["repository_id"])
    op.create_index("idx_vulnerabilities_severity", "vulnerabilities", ["severity"])

    # --- metrics_snapshots table (NOT metrics_history — matches MetricsSnapshot model) ---
    op.create_index("idx_metrics_repo", "metrics_snapshots", ["repository_id"])
    op.create_index("idx_metrics_created_at", "metrics_snapshots", ["created_at"])
    op.create_index(
        "idx_metrics_repo_time", "metrics_snapshots", ["repository_id", "created_at"]
    )


def downgrade():
    op.drop_index("idx_files_repo_id", table_name="files")
    op.drop_index("idx_files_file_path", table_name="files")
    op.drop_index("idx_files_language", table_name="files")
    op.drop_index("idx_files_repo_language", table_name="files")

    op.drop_index("idx_symbols_file_id", table_name="symbols")
    op.drop_index("idx_symbols_name", table_name="symbols")
    op.drop_index("idx_symbols_type", table_name="symbols")
    op.drop_index("idx_symbols_file_name", table_name="symbols")

    op.drop_index("idx_embeddings_symbol_id", table_name="embeddings")

    op.drop_index("idx_callrel_caller_name", table_name="call_relationships")
    op.drop_index("idx_callrel_callee_name", table_name="call_relationships")
    op.drop_index("idx_callrel_is_external", table_name="call_relationships")

    op.drop_index("idx_code_smells_repo", table_name="code_smells")
    op.drop_index("idx_code_smells_file_id", table_name="code_smells")
    op.drop_index("idx_code_smells_severity", table_name="code_smells")
    op.drop_index("idx_code_smells_type", table_name="code_smells")

    op.drop_index("idx_vulnerabilities_repo", table_name="vulnerabilities")
    op.drop_index("idx_vulnerabilities_severity", table_name="vulnerabilities")

    op.drop_index("idx_metrics_repo", table_name="metrics_snapshots")
    op.drop_index("idx_metrics_created_at", table_name="metrics_snapshots")
    op.drop_index("idx_metrics_repo_time", table_name="metrics_snapshots")
