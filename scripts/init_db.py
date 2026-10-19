
from app.database import Base, engine
from app.models.task import Task  # noqa: F401


def main():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
