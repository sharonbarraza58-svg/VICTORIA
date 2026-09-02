"""primera migracion

Revision ID: ba2675917d50
Revises: a2869a2e1d9b
Create Date: 2026-08-11 14:35:05.494705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba2675917d50'
down_revision: Union[str, Sequence[str], None] = 'a2869a2e1d9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
