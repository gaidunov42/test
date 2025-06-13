"""merge two heads

Revision ID: 583570ebaec6
Revises: 21e9700fed61, a4bc47a8f25e
Create Date: 2025-05-10 20:36:23.318936

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "583570ebaec6"
down_revision = ("21e9700fed61", "a4bc47a8f25e")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
