"""add user_id fk to urls

Revision ID: 00ed2a17ff7e
Revises: 88be09299388
Create Date: 2026-08-03 12:37:26.487521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00ed2a17ff7e'
down_revision: Union[str, Sequence[str], None] = '88be09299388'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('urls', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index('ix_urls_user_id', 'urls', ['user_id'], unique=False)
    op.create_foreign_key(
        'fk_urls_user_id_users',
        'urls',
        'users',
        ['user_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_urls_user_id_users', 'urls', type_='foreignkey')
    op.drop_index('ix_urls_user_id', table_name='urls')
    op.drop_column('urls', 'user_id')
