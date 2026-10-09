"""Add BrandDNA and ContentContext

Revision ID: 971598b50354
Revises: 7ee5f5f5bf0f
Create Date: 2026-10-08 13:14:08.155281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '971598b50354'
down_revision: Union[str, Sequence[str], None] = '280fbb7fe8ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('brand_dna',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('colors', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('typography', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('layout', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('restrictions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('version')
    )
    op.create_table('content_contexts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('content_post_id', sa.UUID(), nullable=False),
    sa.Column('content_type', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('event', sa.String(), nullable=True),
    sa.Column('season', sa.String(), nullable=True),
    sa.Column('visual_mood', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['content_post_id'], ['content_posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('content_versions', sa.Column('negative_prompt', sa.String(), nullable=True))
    op.add_column('content_versions', sa.Column('brand_dna_version', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('content_versions', 'brand_dna_version')
    op.drop_column('content_versions', 'negative_prompt')
    op.drop_table('content_contexts')
    op.drop_table('brand_dna')
