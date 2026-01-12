import pytest
from app.services.auth import AuthService


class TestAuthService:
    """Unit tests for AuthService"""

    def test_password_hash_and_verify(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)

        assert hashed != password
        assert AuthService.verify_password(password, hashed) is True
        assert AuthService.verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """Test access token creation"""
        token = AuthService.create_access_token(user_id=1)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test refresh token creation"""
        token = AuthService.create_refresh_token(user_id=1)

        assert token is not None
        assert isinstance(token, str)

    def test_decode_valid_token(self):
        """Test decoding a valid token"""
        token = AuthService.create_access_token(user_id=42)
        payload = AuthService.decode_token(token)

        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["type"] == "access"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token returns None"""
        payload = AuthService.decode_token("invalid.token.here")

        assert payload is None


@pytest.mark.asyncio
async def test_register_user(client, test_user_data):
    """Test user registration endpoint"""
    response = await client.post("/v1/auth/register", json=test_user_data)

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == test_user_data["email"]
    assert data["user"]["first_name"] == test_user_data["first_name"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user_data):
    """Test registration with duplicate email fails"""
    # First registration
    await client.post("/v1/auth/register", json=test_user_data)

    # Second registration with same email
    response = await client.post("/v1/auth/register", json=test_user_data)

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client, test_user_data):
    """Test successful login"""
    # Register first
    await client.post("/v1/auth/register", json=test_user_data)

    # Login
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    }
    response = await client.post("/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == test_user_data["email"]


@pytest.mark.asyncio
async def test_login_invalid_password(client, test_user_data):
    """Test login with wrong password fails"""
    # Register first
    await client.post("/v1/auth/register", json=test_user_data)

    # Login with wrong password
    login_data = {
        "email": test_user_data["email"],
        "password": "wrongpassword",
    }
    response = await client.post("/v1/auth/login", json=login_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    """Test login with non-existent user fails"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "somepassword",
    }
    response = await client.post("/v1/auth/login", json=login_data)

    assert response.status_code == 401
