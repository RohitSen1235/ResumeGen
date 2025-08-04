from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text('SELECT version_num FROM alembic_version'))
    print('Current version:', result.scalar())
