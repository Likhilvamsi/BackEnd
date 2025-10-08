import pytest
from httpx import AsyncClient
from main import app


# -------------------------
# Helpers for mocking engine
# -------------------------
class MockConnection:
    def __init__(self, execute_behavior):
        self.execute_behavior = execute_behavior

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, query, params=None):
        return await self.execute_behavior(query, params)

    async def commit(self):
        return None


class MockEngine:
    def __init__(self, execute_behavior):
        self.execute_behavior = execute_behavior

    def connect(self):
        return MockConnection(self.execute_behavior)


# -------------------------
# Tests
# -------------------------

@pytest.mark.asyncio
async def test_add_phone_number_success(monkeypatch):
    async def mock_execute(query, params=None):
        q = str(query)
        if "FROM employee_details" in q:
            class MockResult: 
                def fetchone(self): return (1,)
            return MockResult()
        if "FROM phone_numbers" in q:
            class MockResult: 
                def fetchone(self): return None
            return MockResult()
        if "INSERT INTO phone_numbers" in q:
            return None

    monkeypatch.setattr("db.database.async_engine", MockEngine(mock_execute))

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/phones/", json={"emp_id": 1, "phone_number": "1234567890"})

    assert response.status_code == 200
    assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_add_phone_number_employee_not_found(monkeypatch):
    async def mock_execute(query, params=None):
        if "FROM employee_details" in str(query):
            class MockResult: 
                def fetchone(self): return None
            return MockResult()

    monkeypatch.setattr("db.database.async_engine", MockEngine(mock_execute))

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/phones/", json={"emp_id": 99, "phone_number": "1234567890"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee ID does not exist."


@pytest.mark.asyncio
async def test_add_phone_number_duplicate(monkeypatch):
    async def mock_execute(query, params=None):
        q = str(query)
        if "FROM employee_details" in q:
            class MockResult: 
                def fetchone(self): return (1,)
            return MockResult()
        if "FROM phone_numbers" in q:
            class MockResult: 
                def fetchone(self): return (1,)
            return MockResult()

    monkeypatch.setattr("db.database.async_engine", MockEngine(mock_execute))

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/phones/", json={"emp_id": 1, "phone_number": "1234567890"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Phone number already exists for this employee."


@pytest.mark.asyncio
async def test_add_phone_number_db_error(monkeypatch):
    async def mock_execute(query, params=None):
        raise Exception("Simulated DB error")

    monkeypatch.setattr("db.database.async_engine", MockEngine(mock_execute))

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/phones/", json={"emp_id": 1, "phone_number": "1234567890"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Unexpected error occurred"
