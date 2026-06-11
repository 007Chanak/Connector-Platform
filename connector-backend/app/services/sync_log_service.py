from sqlalchemy import text

from app.database import SessionLocal


def create_sync_log(
    user_id,
    entity_type,
    source,
    destination,
    external_id,
    status
):

    db = SessionLocal()
    try:

        db.execute(
            text("""
                INSERT INTO sync_logs
                (
                    user_id,
                    entity_type,
                    source,
                    destination,
                    external_id,
                    status
                )
                VALUES
                (
                    :user_id,
                    :entity_type,
                    :source,
                    :destination,
                    :external_id,
                    :status
                )
            """),
            {
                "user_id": user_id,
                "entity_type": entity_type,
                "source": source,
                "destination": destination,
                "external_id": external_id,
                "status": status
            }
        )

        db.commit()
    finally:
        db.close()