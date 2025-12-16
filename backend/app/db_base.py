"""Shared SQLAlchemy declarative Base.

Why this exists:
- Models need a `Base` to inherit from.
- The database module needs the same `Base` for `Base.metadata.create_all()`.

Keeping `Base` in its own module avoids circular imports between `database.py` and
`models/*`.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
