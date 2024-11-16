"""make email and number field unique

Revision ID: 887e06b208ee
Revises: 
Create Date: 2024-10-21 21:27:58.529104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '887e06b208ee'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('uq_user_name', 'users', ['email', 'phone_number'])


def downgrade() -> None:
    pass
