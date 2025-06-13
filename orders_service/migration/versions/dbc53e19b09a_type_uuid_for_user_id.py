"""type uuid for user_id

Revision ID: dbc53e19b09a
Revises: ce3a96c2cd2e
Create Date: 2025-05-10 22:41:50.156697

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "dbc53e19b09a"
down_revision = "ce3a96c2cd2e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("orders", "user_id")
    op.add_column("orders", sa.Column("user_id", UUID(as_uuid=True), nullable=False))


def downgrade() -> None:
    op.drop_column("orders", "user_id")
    op.add_column("orders", sa.Column("user_id", sa.Integer, nullable=False))
