"""add active to Allocation

Revision ID: fa643264e5fe
Revises: f88b83f9ce71
Create Date: 2023-12-22 17:19:03.373606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa643264e5fe'
down_revision: Union[str, None] = 'f88b83f9ce71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('allocation', sa.Column('active', sa.Boolean(), nullable=False, server_default='true'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('allocation', 'active')
    # ### end Alembic commands ###
