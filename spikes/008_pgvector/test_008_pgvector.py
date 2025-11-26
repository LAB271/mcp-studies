import time

import pytest
from main_server import add_knowledge, add_reading, add_sensor, get_connection, get_readings, search_knowledge

# Wait for DB to be ready (simple retry logic)
def wait_for_db():
    retries = 5
    while retries > 0:
        try:
            conn = get_connection()
            conn.close()
            return
        except Exception:
            time.sleep(2)
            retries -= 1
    raise Exception("Database not ready")

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Setup and teardown for the test module."""
    wait_for_db()

    # Clean up before tests
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE sensors, sensor_readings, sensor_knowledge CASCADE;")
    conn.commit()
    conn.close()

    yield

    # Clean up after tests
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE sensors, sensor_readings, sensor_knowledge CASCADE;")
    conn.commit()
    conn.close()

def test_sensor_lifecycle():
    """Test adding a sensor and readings."""
    # 1. Add Sensor
    result = add_sensor("s001", "Temp Sensor 1", "temperature", "Lab A")
    assert "added successfully" in result

    # 2. Add Duplicate Sensor (should fail gracefully)
    result = add_sensor("s001", "Temp Sensor 1", "temperature", "Lab A")
    assert "already exists" in result

    # 3. Add Reading
    result = add_reading("s001", 25.5)
    assert "Reading 25.5 recorded" in result

    # 4. Get Readings
    result = get_readings("s001")
    assert "25.5" in result

def test_knowledge_vector_search():
    """Test adding knowledge and semantic search."""
    # Ensure sensor exists
    add_sensor("s002", "Complex Machine", "machinery", "Factory Floor")

    # 1. Add Knowledge
    doc1 = "The emergency shutoff valve is located under the main control panel."
    doc2 = "Routine maintenance requires checking the oil level every 50 hours."

    res1 = add_knowledge("s002", doc1)
    res2 = add_knowledge("s002", doc2)

    assert "Knowledge added" in res1
    assert "Knowledge added" in res2

    # 2. Search Knowledge (Exact match intent)
    # "Where is the shutoff?" should match doc1
    search_res = search_knowledge("Where is the shutoff valve?")
    assert "emergency shutoff valve" in search_res

    # 3. Search Knowledge (Different intent)
    # "How often to check oil?" should match doc2
    search_res = search_knowledge("oil check frequency")
    assert "checking the oil level" in search_res

def test_missing_sensor():
    """Test operations on non-existent sensors."""
    res = add_reading("non_existent", 10.0)
    assert "not found" in res

    res = add_knowledge("non_existent", "Some info")
    assert "not found" in res
