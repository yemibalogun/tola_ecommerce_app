from flask_sqlalchemy import SQLAlchemy

# expire_on_commit=False prevents objects from becoming detached
db: SQLAlchemy = SQLAlchemy(
    session_options={"expire_on_commit": False}
)
