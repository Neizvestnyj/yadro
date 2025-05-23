"""Init

Revision ID: 0c2f5ad7073e
Revises: 
Create Date: 2025-05-24 00:13:15.444022
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0c2f5ad7073e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Проверяем, существует ли таблица users
    if not op.get_bind().execute(
        sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
    ).scalar():
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('gender', sa.String(length=50), nullable=False),
            sa.Column('title', sa.String(length=50), nullable=True),
            sa.Column('first_name', sa.String(length=100), nullable=False),
            sa.Column('last_name', sa.String(length=100), nullable=False),
            sa.Column('street_number', sa.Integer(), nullable=True),
            sa.Column('street_name', sa.String(length=100), nullable=True),
            sa.Column('city', sa.String(length=100), nullable=True),
            sa.Column('state', sa.String(length=100), nullable=True),
            sa.Column('country', sa.String(length=100), nullable=True),
            sa.Column('postcode', sa.String(length=10), nullable=True),
            sa.Column('latitude', sa.Float(), nullable=True),
            sa.Column('longitude', sa.Float(), nullable=True),
            sa.Column('timezone_offset', sa.String(length=10), nullable=True),
            sa.Column('phone', sa.String(length=50), nullable=True),
            sa.Column('cell', sa.String(length=50), nullable=True),
            sa.Column('email', sa.String(length=100), nullable=True),
            sa.Column('external_id', sa.String(length=100), nullable=True),
            sa.Column('username', sa.String(length=100), nullable=True),
            sa.Column('uuid', sa.String(length=100), nullable=True),
            sa.Column('picture', sa.String(length=255), nullable=True),
            sa.Column('dob', sa.DateTime(timezone=True), nullable=True),
            sa.Column('registered_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('nat', sa.String(length=10), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('uuid')
        )

    # Проверяем и создаём индексы, если они не существуют
    bind = op.get_bind()
    indexes = bind.execute(
        sa.text("SELECT indexname FROM pg_indexes WHERE tablename = 'users'")
    ).fetchall()
    index_names = {idx[0] for idx in indexes}

    if 'ix_users_city' not in index_names:
        op.create_index(op.f('ix_users_city'), 'users', ['city'], unique=False)
    if 'ix_users_country' not in index_names:
        op.create_index(op.f('ix_users_country'), 'users', ['country'], unique=False)
    if 'ix_users_email' not in index_names:
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    if 'ix_users_id' not in index_names:
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    if 'ix_users_username' not in index_names:
        op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)

def downgrade() -> None:
    # Удаляем индексы и таблицу только если они существуют
    bind = op.get_bind()
    indexes = bind.execute(
        sa.text("SELECT indexname FROM pg_indexes WHERE tablename = 'users'")
    ).fetchall()
    index_names = {idx[0] for idx in indexes}

    if 'ix_users_username' in index_names:
        op.drop_index(op.f('ix_users_username'), table_name='users')
    if 'ix_users_id' in index_names:
        op.drop_index(op.f('ix_users_id'), table_name='users')
    if 'ix_users_email' in index_names:
        op.drop_index(op.f('ix_users_email'), table_name='users')
    if 'ix_users_country' in index_names:
        op.drop_index(op.f('ix_users_country'), table_name='users')
    if 'ix_users_city' in index_names:
        op.drop_index(op.f('ix_users_city'), table_name='users')

    if bind.execute(
        sa.text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
    ).scalar():
        op.drop_table('users')