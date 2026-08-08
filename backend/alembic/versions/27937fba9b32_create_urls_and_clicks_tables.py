"""create urls and clicks tables

Revision ID: 27937fba9b32
Revises:
Create Date: 2026-07-30 23:27:13.136534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '27937fba9b32'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'urls',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('original_url', sa.String(), nullable=False),
        sa.Column('short_code', sa.String(length=20), nullable=False),
        sa.Column('custom_alias', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('click_count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('custom_alias'),
    )
    op.create_index('ix_urls_short_code', 'urls', ['short_code'], unique=True)

    op.create_table(
        'clicks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('url_id', sa.Integer(), nullable=False),
        sa.Column('clicked_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('referrer', sa.String(length=2048), nullable=True),
        sa.ForeignKeyConstraint(['url_id'], ['urls.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_clicks_url_id', 'clicks', ['url_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_clicks_url_id', table_name='clicks')
    op.drop_table('clicks')
    op.drop_index('ix_urls_short_code', table_name='urls')
    op.drop_table('urls')
