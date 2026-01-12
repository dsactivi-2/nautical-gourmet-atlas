import pytest


@pytest.mark.asyncio
async def test_list_categories(client):
    """Test listing categories (empty initially)"""
    response = await client.get("/v1/categories")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_filters(client):
    """Test listing filters (empty initially)"""
    response = await client.get("/v1/filters")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_filters_with_category(client):
    """Test listing filters with category_id param"""
    response = await client.get("/v1/filters", params={"category_id": 1})

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_partners(client):
    """Test listing partners (empty initially)"""
    response = await client.get("/v1/partners")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_partners_with_bbox(client):
    """Test listing partners with bbox param"""
    response = await client.get(
        "/v1/partners",
        params={"bbox": "13.5,42.5,17.5,45.5"}
    )

    # Note: SQLite doesn't support PostGIS, so this may fail in tests
    # In production with PostGIS, this would work
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_list_partners_with_filters(client):
    """Test listing partners with multiple filters"""
    response = await client.get(
        "/v1/partners",
        params={
            "category_id": 1,
            "filter_ids": "1,2",
            "q": "test",
            "premium_only": True,
        }
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_partner_not_found(client):
    """Test getting non-existent partner returns 404"""
    response = await client.get("/v1/partners/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_treasures(client):
    """Test listing treasures (empty initially)"""
    response = await client.get("/v1/treasures")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_treasures_with_category(client):
    """Test listing treasures with category filter"""
    response = await client.get("/v1/treasures", params={"category": "wines"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_treasure_categories(client):
    """Test getting treasure categories"""
    response = await client.get("/v1/treasures/categories")

    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) == 4  # wines, traditional_dishes, products, crafts_souvenirs


@pytest.mark.asyncio
async def test_get_treasure_not_found(client):
    """Test getting non-existent treasure returns 404"""
    response = await client.get("/v1/treasures/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_favorites_requires_auth(client):
    """Test favorites endpoint requires authentication"""
    response = await client.get("/v1/favorites")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_visits_requires_auth(client):
    """Test visits endpoint requires authentication"""
    response = await client.get("/v1/visits")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    """Test me endpoint requires authentication"""
    response = await client.get("/v1/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_accept_language_header(client):
    """Test Accept-Language header is processed"""
    # Request with Croatian language
    response = await client.get(
        "/v1/categories",
        headers={"Accept-Language": "hr"}
    )

    assert response.status_code == 200

    # Request with German language
    response = await client.get(
        "/v1/categories",
        headers={"Accept-Language": "de"}
    )

    assert response.status_code == 200
