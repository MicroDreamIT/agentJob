from core.database import create_connection, close_connection, Job
import datetime

def test_store_job():
    session = create_connection()

    # Create test job entry
    test_job = Job(
        provider='TEST',
        provider_id=123456,
        title='Test Job',
        link='https://example.com/test-job',
        quick_apply=True,
        applied_on=datetime.datetime.utcnow()
    )

    # Store job in database
    session.add(test_job)
    session.commit()
    print("Test Job stored successfully.")

    # Retrieve the job to verify storage
    retrieved_job = session.query(Job).filter_by(provider='TEST', provider_id=123456).first()
    assert retrieved_job is not None, "Failed to store job."
    print("Retrieved job from database:", retrieved_job.title, retrieved_job.link)

    # Clean up after test
    session.delete(retrieved_job)
    session.commit()
    print("Cleaned up test entry.")

    close_connection(session)

if __name__ == "__main__":
    test_store_job()
