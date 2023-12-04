"""create base models

Revision ID: 4ecb8509214a
Revises: 
Create Date: 2023-12-04 07:32:56.699137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

type = postgresql.ENUM('east_bunk_bed', 'north_ground_floor_wooden_bed', 'south_bunk_bed', name='type')
amount_for = postgresql.ENUM('event', 'day', name='amount_for')
floor = postgresql.ENUM('gf', 'ff', name='floor')
bed_type = postgresql.ENUM('bunk', 'metal', 'wood', name='bed_type')
participant_type = postgresql.ENUM('general', 'sisters_only', 'overseas_only', name='participant_type')
level = postgresql.ENUM('lower', 'upper', name='level')

# revision identifiers, used by Alembic.
revision: str = '4ecb8509214a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dorm',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('type', sa.Enum('east_bunk_bed', 'north_ground_floor_wooden_bed', 'south_bunk_bed', name='type'), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('amount_for', sa.Enum('event', 'day', name='amount_type'), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dorm_id'), 'dorm', ['id'], unique=False)
    op.create_index(op.f('ix_dorm_name'), 'dorm', ['name'], unique=True)
    op.create_table('room',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('dorm_id', sa.UUID(), nullable=False),
    sa.Column('room_identifier', sa.Integer(), nullable=False),
    sa.Column('ac_available', sa.Boolean(), nullable=True),
    sa.Column('floor', sa.Enum('gf', 'ff', name='floor'), nullable=False),
    sa.Column('close_to_dorm_entrance', sa.Boolean(), nullable=True),
    sa.Column('close_to_bath', sa.Boolean(), nullable=True),
    sa.Column('percent_released', sa.Integer(), nullable=True),
    sa.Column('bed_type', sa.Enum('bunk', 'metal', 'wood', name='bed_type'), nullable=False),
    sa.Column('is_multibatch', sa.Boolean(), nullable=True),
    sa.Column('max_count', sa.Integer(), nullable=True),
    sa.Column('participant_type', sa.Enum('general', 'sisters_only', 'overseas_only', name='participant_type'), nullable=False),
    sa.Column('reset_allowed', sa.Boolean(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['dorm_id'], ['dorm.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_id'), 'room', ['id'], unique=False)
    op.create_index(op.f('ix_room_name'), 'room', ['name'], unique=False)
    op.create_table('bed',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('room_id', sa.UUID(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('blocked', sa.Boolean(), nullable=True),
    sa.Column('level', sa.Enum('lower', 'upper', name='level'), nullable=False),
    sa.Column('close_to_dorm_entrance', sa.Boolean(), nullable=True),
    sa.Column('close_to_bath', sa.Boolean(), nullable=True),
    sa.Column('allocated', sa.Boolean(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bed_id'), 'bed', ['id'], unique=False)
    op.create_index(op.f('ix_bed_name'), 'bed', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bed_name'), table_name='bed')
    op.drop_index(op.f('ix_bed_id'), table_name='bed')
    op.drop_table('bed')
    op.execute(sa.text('DROP TYPE level'))

    op.drop_index(op.f('ix_room_name'), table_name='room')
    op.drop_index(op.f('ix_room_id'), table_name='room')
    op.drop_table('room')
    op.execute(sa.text('DROP TYPE floor'))
    op.execute(sa.text('DROP TYPE bed_type'))
    op.execute(sa.text('DROP TYPE participant_type'))

    op.drop_index(op.f('ix_dorm_name'), table_name='dorm')
    op.drop_index(op.f('ix_dorm_id'), table_name='dorm')
    op.drop_table('dorm')
    op.execute(sa.text('DROP TYPE type'))
    op.execute(sa.text('DROP TYPE amount_type'))
    # ### end Alembic commands ###
