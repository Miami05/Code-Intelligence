"""create code_smells table

Revision ID: create_code_smells
Revises: 7c9c52b4cdbe
Create Date: 2026-02-19 21:45:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'create_code_smells'
down_revision: Union[str, None] = '7c9c52b4cdbe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, create the enum types if they don't exist
    conn = op.get_bind()
    
    # Check and create smelltype enum
    result = conn.execute(sa.text(
        "SELECT 1 FROM pg_type WHERE typname = 'smelltype'"
    ))
    if not result.fetchone():
        op.execute(
            "CREATE TYPE smelltype AS ENUM ('long_method', 'god_class', 'feature_envy', "
            "'large_class', 'long_parameter_list', 'duplicate_code', 'dead_code', 'missing_docstring')"
        )
    else:
        # Enum exists, make sure missing_docstring is in it
        with op.get_context().autocommit_block():
            op.execute("ALTER TYPE smelltype ADD VALUE IF NOT EXISTS 'missing_docstring'")
    
    # Check and create smellseverity enum
    result = conn.execute(sa.text(
        "SELECT 1 FROM pg_type WHERE typname = 'smellseverity'"
    ))
    if not result.fetchone():
        op.execute(
            "CREATE TYPE smellseverity AS ENUM ('low', 'medium', 'high', 'critical')"
        )
    
    # Check if code_smells table exists
    result = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables WHERE table_name = 'code_smells'"
    ))
    if not result.fetchone():
        # Create the table
        op.create_table(
            'code_smells',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('repository_id', postgresql.UUID(as_uuid=True), 
                     sa.ForeignKey('repositories.id', ondelete='CASCADE'), nullable=False),
            sa.Column('file_id', postgresql.UUID(as_uuid=True), 
                     sa.ForeignKey('files.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('symbol_id', postgresql.UUID(as_uuid=True), 
                     sa.ForeignKey('symbols.id', ondelete='CASCADE'), nullable=True, index=True),
            sa.Column('smell_type', postgresql.ENUM(
                'long_method', 'god_class', 'feature_envy', 'large_class', 
                'long_parameter_list', 'duplicate_code', 'dead_code', 'missing_docstring',
                name='smelltype', create_type=False
            ), nullable=False, index=True),
            sa.Column('severity', postgresql.ENUM(
                'low', 'medium', 'high', 'critical',
                name='smellseverity', create_type=False
            ), nullable=False, index=True),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('suggestion', sa.Text(), nullable=True),
            sa.Column('start_line', sa.Integer(), nullable=False),
            sa.Column('end_line', sa.Integer(), nullable=False),
            sa.Column('metric_value', sa.Integer(), nullable=True),
            sa.Column('metric_threshold', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), 
                     server_default=sa.text('now()'), nullable=False, index=True),
        )


def downgrade() -> None:
    op.drop_table('code_smells')
    op.execute('DROP TYPE IF EXISTS smelltype CASCADE')
    op.execute('DROP TYPE IF EXISTS smellseverity CASCADE')
