"""add guest_id to urls

Revision ID: 9e5929bbdaf0
Revises: 00ed2a17ff7e
Create Date: 2026-08-05 13:15:32.199808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9e5929bbdaf0'
down_revision: Union[str, Sequence[str], None] = '00ed2a17ff7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('urls', sa.Column('guest_id', sa.String(length=36), nullable=True))
    op.create_index('ix_urls_guest_id', 'urls', ['guest_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_urls_guest_id', table_name='urls')
    op.drop_column('urls', 'guest_id')
