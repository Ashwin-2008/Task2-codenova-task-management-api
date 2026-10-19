
from datetime import datetime, timedelta, timezone

from app.database import Base, SessionLocal, engine
from app.models.task import Task


def main():
    # Ensure the database tables exist.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Get titles already present in the database.
        existing_titles = {
            title for (title,) in db.query(Task.title).all()
        }

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Define sample tasks.
        sample_tasks = [
            Task(
                title="Complete CodeNova Task 2",
                description="Finish the Task Management API",
                priority="High",
                status="In Progress",
                due_date=now + timedelta(days=3),
            ),
            Task(
                title="Write API documentation",
                description="Document endpoints and examples",
                priority="Medium",
                status="Todo",
                due_date=now + timedelta(days=5),
            ),
            Task(
                title="Test CRUD endpoints",
                description="Verify create, read, update and delete",
                priority="High",
                status="Todo",
                due_date=now + timedelta(days=2),
            ),
            Task(
                title="Learn SQLAlchemy",
                description="Practice database queries",
                priority="Low",
                status="Done",
                due_date=now + timedelta(days=7),
            ),
            Task(
                title="Prepare GitHub README",
                description="Add setup and usage instructions",
                priority="Medium",
                status="Todo",
                due_date=None,
            ),
        ]

        # Insert only tasks whose titles do not already exist.
        new_tasks = [
            task
            for task in sample_tasks
            if task.title not in existing_titles
        ]

        if not new_tasks:
            print("All sample tasks already exist. Nothing to insert.")
            return

        db.add_all(new_tasks)
        db.commit()

        print(f"Successfully inserted {len(new_tasks)} sample tasks.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
