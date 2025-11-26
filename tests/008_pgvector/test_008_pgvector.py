import os
import sys
from unittest.mock import MagicMock, patch

import psycopg2
import pytest

# Add tests directory to path to import test_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from tests.test_utils import load_spike_module

main_server = load_spike_module("008_pgvector", "main_server")
add_knowledge = main_server.add_knowledge
add_reading = main_server.add_reading
add_sensor = main_server.add_sensor
get_connection = main_server.get_connection
get_readings = main_server.get_readings
search_knowledge = main_server.search_knowledge


@pytest.fixture(autouse=True)
def mock_sentence_transformer():
    with patch.object(main_server, "SentenceTransformer") as mock_cls:
        mock_model = MagicMock()
        # Return a list of floats, not a Mock
        mock_model.encode.return_value.tolist.return_value = [0.1] * 384
        mock_cls.return_value = mock_model
        yield


@pytest.fixture(autouse=True)
def mock_db():
    with patch.object(main_server.psycopg2, "connect") as mock_connect, patch.object(main_server, "register_vector"):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        yield mock_connect, mock_cursor


def test_sensor_lifecycle(mock_db):
    _, mock_cursor = mock_db

    # 1. Add Sensor
    result = add_sensor("s001", "Temp Sensor 1", "temperature", "Lab A")
    assert "added successfully" in result

    # 2. Add Duplicate Sensor
    # Simulate IntegrityError for duplicate
    mock_cursor.execute.side_effect = psycopg2.IntegrityError("Duplicate")
    result = add_sensor("s001", "Temp Sensor 1", "temperature", "Lab A")
    assert "already exists" in result
    mock_cursor.execute.side_effect = None  # Reset

    # 3. Add Reading
    # Mock fetchone to return something (sensor exists)
    mock_cursor.fetchone.return_value = (1,)
    result = add_reading("s001", 25.5)
    assert "Reading 25.5 recorded" in result

    # 4. Get Readings
    # Mock fetchall to return readings as dict-like objects
    mock_cursor.fetchall.return_value = [{"value": 25.5, "timestamp": "2023-01-01"}]
    result = get_readings("s001")
    assert "25.5" in result


def test_knowledge_vector_search(mock_db):
    _, mock_cursor = mock_db

    # Ensure sensor exists
    mock_cursor.fetchone.return_value = (1,)  # Sensor exists

    # 1. Add Knowledge
    res1 = add_knowledge("s002", "doc1")
    assert "Knowledge added" in res1

    # 2. Search Knowledge
    # Mock fetchall to return search results as dict-like objects
    mock_cursor.fetchall.return_value = [
        {"content": "doc1", "sensor_name": "s002", "created_at": "2023-01-01", "distance": 0.1}
    ]
    search_res = search_knowledge("query")
    assert "doc1" in search_res


def test_missing_sensor(mock_db):
    _, mock_cursor = mock_db

    # Mock fetchone to return None (sensor doesn't exist)
    mock_cursor.fetchone.return_value = None

    res = add_reading("non_existent", 10.0)
    assert "not found" in res

    res = add_knowledge("non_existent", "Some info")
    assert "not found" in res


def test_add_sensor_duplicate(mock_db):
    _, mock_cursor = mock_db
    mock_cursor.execute.side_effect = psycopg2.IntegrityError("Duplicate")
    res = add_sensor("s_dup", "Dup", "type", "loc")
    assert "already exists" in res


def test_add_reading_error(mock_db):
    _, mock_cursor = mock_db

    # We need to ensure fetchone returns something so it tries to insert reading
    mock_cursor.fetchone.return_value = (1,)

    # The first execute is SELECT 1 (check sensor), second is INSERT
    # We want INSERT to fail
    mock_cursor.execute.side_effect = [None, Exception("DB Error")]

    res = add_reading("s1", 1.0)
    assert "Error adding reading" in res


def test_add_knowledge_error(mock_db):
    _, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = (1,)
    mock_cursor.execute.side_effect = [None, Exception("DB Error")]

    res = add_knowledge("s1", "content")
    assert "Error adding knowledge" in res


def test_search_knowledge_error(mock_db):
    _, mock_cursor = mock_db
    mock_cursor.execute.side_effect = Exception("DB Error")

    res = search_knowledge("query")
    assert "Error searching knowledge" in res


def test_search_knowledge_no_results(mock_db):
    _, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []

    res = search_knowledge("query")
    assert "No relevant knowledge found" in res


def test_add_sensor_generic_error(mock_db):
    _, mock_cursor = mock_db
    mock_cursor.execute.side_effect = Exception("Generic Error")
    res = add_sensor("s1", "n", "t", "l")
    assert "Error adding sensor" in res


def test_get_readings_no_results(mock_db):
    _, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = []
    res = get_readings("s1")
    assert "No readings found" in res


def test_get_connection_error():
    # We need to patch connect specifically for this test to raise exception
    with patch.object(main_server.psycopg2, "connect", side_effect=Exception("Conn Error")):
        with pytest.raises(RuntimeError):
            get_connection()
