from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text
from sqlalchemy.schema import MetaData

from alembic import context

from app.core.settings import settings
from app.models import Base


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Filter metadata to only include tables in orders schema
target_metadata = MetaData()
for table in Base.metadata.tables.values():
    if table.schema == 'orders':
        table.tometadata(target_metadata)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema='orders',
        version_table='alembic_version',
        include_schemas=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """Filter to only include objects from the orders schema"""
    if type_ == "schema":
        return name == "orders"
    elif hasattr(object, 'schema'):
        return object.schema == "orders"
    elif type_ == "table" and hasattr(object, 'table'):
        return object.table.schema == "orders"
    return True


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Create schema outside of transaction
    with connectable.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS orders"))
        connection.commit()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema='orders',
            version_table='alembic_version',
            include_schemas=True,
            process_revision_directives=None,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=False,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
