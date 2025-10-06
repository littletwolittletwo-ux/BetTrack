from __future__ import annotations
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.base import Base  # noqa
from app.models import User, BetSet, Bookmaker, Bet, CsvUpload  # noqa

config = context.config
if config.get_main_option("sqlalchemy.url") is None:
 config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL", ""))

fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
 context.configure(
     url=config.get_main_option("sqlalchemy.url"),
     target_metadata=target_metadata,
     literal_binds=True,
     dialect_opts={"paramstyle": "named"},
 )
 with context.begin_transaction():
     context.run_migrations()

def run_migrations_online():
 connectable = engine_from_config(
     config.get_section(config.config_ini_section),
     prefix="sqlalchemy.",
     poolclass=pool.NullPool,
 )
 with connectable.connect() as connection:
     context.configure(connection=connection, target_metadata=target_metadata)
     with context.begin_transaction():
         context.run_migrations()

if context.is_offline_mode():
 run_migrations_offline()
else:
 run_migrations_online()