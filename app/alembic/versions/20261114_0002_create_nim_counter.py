"""create nim counter table

Revision ID: 20261114_0002
Revises: 20261114_0001
Create Date: 2026-11-14 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20261114_0002'
down_revision: Union[str, None] = '20261114_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Pastikan PRAGMA foreign_keys aktif di level koneksi SQLite
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        op.execute(sa.text("PRAGMA foreign_keys = ON;"))

    # Tabel: nim_counter
    op.create_table(
        'nim_counter',
        sa.Column('tahun', sa.Integer(), nullable=False),
        sa.Column('kode_prodi', sa.String(length=3), nullable=False),
        sa.Column('last_number', sa.Integer(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('tahun', 'kode_prodi', name=op.f('pk_nim_counter')),
    )


def downgrade() -> None:
    op.drop_table('nim_counter')
