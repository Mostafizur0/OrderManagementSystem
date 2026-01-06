import time
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings
from app.middleware.metrics_middleware import DATABASE_QUERY_DURATION
from app.models.base import Base


def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    elapsed = time.time() - context._query_start_time
    query_type = statement.split()[0].lower()  # naive extraction: select/insert/update/delete
    DATABASE_QUERY_DURATION.labels(query_type=query_type).observe(elapsed)

# Create database engine
engine = create_engine(settings.DATABASE_URL)

event.listen(engine, "before_cursor_execute", before_cursor_execute)
event.listen(engine, "after_cursor_execute", after_cursor_execute)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
