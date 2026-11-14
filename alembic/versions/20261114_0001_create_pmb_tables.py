"""create pmb tables

Revision ID: 20261114_0001
Revises: 
Create Date: 2026-11-14 20:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20261114_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Pastikan PRAGMA foreign_keys aktif di level koneksi SQLite
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        op.execute(sa.text("PRAGMA foreign_keys = ON;"))

    # 1. Tabel: program_studi
    op.create_table(
        'program_studi',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('kode', sa.String(length=3), nullable=False),
        sa.Column('nama', sa.String(length=100), nullable=False),
        sa.Column('fakultas', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_program_studi')),
        sa.UniqueConstraint('kode', name=op.f('uq_program_studi_kode'))
    )
    op.create_index(op.f('ix_program_studi_kode'), 'program_studi', ['kode'], unique=True)

    # 2. Tabel: jalur_masuk
    op.create_table(
        'jalur_masuk',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nama', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_jalur_masuk')),
        sa.UniqueConstraint('nama', name=op.f('uq_jalur_masuk_nama'))
    )
    op.create_index(op.f('ix_jalur_masuk_nama'), 'jalur_masuk', ['nama'], unique=True)

    # 3. Tabel: calon_mahasiswa
    op.create_table(
        'calon_mahasiswa',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nama_lengkap', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('tanggal_lahir', sa.Date(), nullable=True),
        sa.Column('alamat', sa.Text(), nullable=True),
        sa.Column('program_studi_id', sa.Integer(), nullable=False),
        sa.Column('jalur_masuk_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('nim', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ['program_studi_id'],
            ['program_studi.id'],
            name=op.f('fk_calon_mahasiswa_program_studi_id'),
            ondelete='RESTRICT'
        ),
        sa.ForeignKeyConstraint(
            ['jalur_masuk_id'],
            ['jalur_masuk.id'],
            name=op.f('fk_calon_mahasiswa_jalur_masuk_id'),
            ondelete='SET NULL'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_calon_mahasiswa')),
        sa.UniqueConstraint('nim', name=op.f('uq_calon_mahasiswa_nim')),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name=op.f('ck_calon_mahasiswa_status')
        )
    )
    op.create_index(op.f('ix_calon_mahasiswa_email'), 'calon_mahasiswa', ['email'], unique=True)


def downgrade() -> None:
    # 0. Pastikan PRAGMA foreign_keys aktif
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        op.execute(sa.text("PRAGMA foreign_keys = ON;"))

    # 1. Hapus calon_mahasiswa terlebih dahulu (tabel child/penyimpan FK)
    # Ini menjamin referential integrity tidak dilanggar saat tabel parent dihapus
    op.drop_index(op.f('ix_calon_mahasiswa_email'), table_name='calon_mahasiswa')
    op.drop_table('calon_mahasiswa')

    # 2. Hapus jalur_masuk (tabel parent)
    op.drop_index(op.f('ix_jalur_masuk_nama'), table_name='jalur_masuk')
    op.drop_table('jalur_masuk')

    # 3. Hapus program_studi (tabel parent)
    op.drop_index(op.f('ix_program_studi_kode'), table_name='program_studi')
    op.drop_table('program_studi')
