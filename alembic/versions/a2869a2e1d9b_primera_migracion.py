"""primera migracion

Revision ID: a2869a2e1d9b
Revises: a12136de3401
Create Date: 2026-08-11 12:43:18.422340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2869a2e1d9b'
down_revision: Union[str, Sequence[str], None] = 'a12136de3401'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
