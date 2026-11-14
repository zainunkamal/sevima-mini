import os
import sys
from logging.config import fileConfig

import sqlalchemy as sa
from sqlalchemy import engine_from_config, pool

from alembic import context

# Tambahkan direktori root proyek ke sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import Base, DATABASE_URL
import app.models  # Memuat seluruh model agar terdaftar di Base.metadata

config = context.config

# Gunakan DATABASE_URL dari .env / app.database jika disetel
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    is_sqlite = url.startswith("sqlite") if url else True
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=is_sqlite,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        is_sqlite = connection.dialect.name == "sqlite"
        # Aktifkan penegakan Foreign Key di level koneksi SQLite saat migrasi
        if is_sqlite:
            connection.execute(sa.text("PRAGMA foreign_keys = ON;"))
            connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=is_sqlite,  # render_as_batch hanya untuk SQLite
        )

        with context.begin_transaction():
            context.run_migrations()
        connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
