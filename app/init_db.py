from app.db import Base, engine

# Import models so SQLAlchemy has registered all tables before create_all.
from app import models  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database schema is ready.")


if __name__ == "__main__":
    main()
