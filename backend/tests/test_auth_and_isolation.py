import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.models import User, Submission, ErrorRecord
from backend.app.core.rate_limit import login_rate_limiter

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    login_rate_limiter.history.clear()
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_registration_validation():
    # Passwords mismatch
    res = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "Password123",
        "confirm_password": "DifferentPassword123"
    })
    assert res.status_code == 422
    assert "Passwords do not match" in res.text

    # Weak password (< 8 chars)
    res = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "pass1",
        "confirm_password": "pass1"
    })
    assert res.status_code == 422
    assert "at least 8 characters" in res.text

    # Valid registration
    res = client.post("/api/auth/register", json={
        "name": "Alice Student",
        "email": "alice@example.com",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "alice@example.com"
    assert "password" not in data

    # Duplicate registration
    res = client.post("/api/auth/register", json={
        "email": "alice@example.com",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    })
    assert res.status_code == 400
    assert "already exists" in res.text

def test_login_invalid_credentials_and_rate_limiting():
    # Register Alice
    client.post("/api/auth/register", json={
        "email": "alice@example.com",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    })

    # Wrong password: returns 401 without revealing whether email or password was wrong
    res = client.post("/api/auth/login", json={
        "email": "alice@example.com",
        "password": "WrongPassword999"
    })
    assert res.status_code == 401
    assert res.json()["detail"] == "Wrong email or password"

    # Non-existent email: returns identical message
    res = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "SecurePassword123"
    })
    assert res.status_code == 401
    assert res.json()["detail"] == "Wrong email or password"

    # Rate limiting: 4 more failed attempts from same client triggers 429
    for _ in range(4):
        client.post("/api/auth/login", json={
            "email": "alice@example.com",
            "password": "WrongPassword999"
        })
    res_rate_limited = client.post("/api/auth/login", json={
        "email": "alice@example.com",
        "password": "WrongPassword999"
    })
    assert res_rate_limited.status_code == 429
    assert "Too many login attempts" in res_rate_limited.text

def test_multi_tenant_data_isolation():
    """
    CRITICAL SECURITY TEST:
    Proves that User A cannot see or delete User B's submissions and vice-versa.
    """
    # 1. Register User A
    client.post("/api/auth/register", json={
        "name": "User A",
        "email": "usera@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
    })
    login_a = client.post("/api/auth/login", json={
        "email": "usera@example.com",
        "password": "Password123"
    })
    token_a = login_a.json()["token"]

    # 2. Register User B
    client.post("/api/auth/register", json={
        "name": "User B",
        "email": "userb@example.com",
        "password": "Password123",
        "confirm_password": "Password123"
    })
    login_b = client.post("/api/auth/login", json={
        "email": "userb@example.com",
        "password": "Password123"
    })
    token_b = login_b.json()["token"]

    # 3. Create a submission directly for User A in DB
    db = SessionLocal()
    user_a = db.query(User).filter(User.email == "usera@example.com").first()
    sub_a = Submission(
        user_id=user_a.id,
        code='int main() { return 0; }',
        compile_status='clean',
        duration_ms=120
    )
    db.add(sub_a)
    db.commit()
    db.refresh(sub_a)
    sub_a_id = sub_a.id
    db.close()

    # 4. User A requests their history -> sees submission
    headers_a = {"Authorization": f"Bearer {token_a}"}
    res_a = client.get("/api/history", headers=headers_a)
    assert res_a.status_code == 200
    assert len(res_a.json()) == 1
    assert res_a.json()[0]["id"] == sub_a_id

    # 5. User B requests their history -> sees 0 submissions (User A's submission is NOT returned)
    headers_b = {"Authorization": f"Bearer {token_b}"}
    res_b = client.get("/api/history", headers=headers_b)
    assert res_b.status_code == 200
    assert len(res_b.json()) == 0

    # 6. User B attempts to access User A's submission detail by ID -> 403 Forbidden!
    res_b_detail = client.get(f"/api/history/{sub_a_id}", headers=headers_b)
    assert res_b_detail.status_code == 403
    assert "Access forbidden" in res_b_detail.text

    # 7. User B attempts to delete User A's submission -> 403 Forbidden!
    res_b_delete = client.delete(f"/api/history/{sub_a_id}", headers=headers_b)
    assert res_b_delete.status_code == 403
    assert "Access forbidden" in res_b_delete.text
