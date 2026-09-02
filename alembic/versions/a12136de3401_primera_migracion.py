"""primera migracion

Revision ID: a12136de3401
Revises: a77af7871bed
Create Date: 2026-07-27 21:09:56.527850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a12136de3401'
down_revision: Union[str, Sequence[str], None] = 'a77af7871bed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
