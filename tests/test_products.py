import json

def test_get_products(client):
    """Tester la récupération des produits"""
    response = client.get("/products")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "products" in data
    assert isinstance(data["products"], list)
