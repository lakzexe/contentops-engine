"""added_scheduled_for

Revision ID: 280fbb7fe8ca
Revises: 5ecf16a4003c
Create Date: 2026-10-08 10:26:38.187405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '280fbb7fe8ca'
down_revision: Union[str, Sequence[str], None] = '5ecf16a4003c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('content_posts', sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('content_posts', 'scheduled_for')
