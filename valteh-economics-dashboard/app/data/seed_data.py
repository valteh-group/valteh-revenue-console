from app.data.database import init_db


def seed_database() -> None:
    """Initialize database tables.

    The first working version reads from CSV seed files at runtime. This function
    creates the schema so replacing CSV access with SQL repositories is direct.
    """

    init_db()
