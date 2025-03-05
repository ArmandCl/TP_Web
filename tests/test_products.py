import json

# --- Test de la récupération de produits ---

def test_get_all_products(client):
    """Tester la récupération de tous les produits"""
    response = client.get("/products")
    assert response.status_code == 200
    products = json.loads(response.data)['products']
    assert isinstance(products, list)  

def test_get_single_product(client, add_products):
    """Tester la récupération d'un produit spécifique"""
    product_id = add_products[0].id
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    product_data = json.loads(response.data)
    assert product_data['product']['name'] == add_products[0].name

def test_get_nonexistent_product(client):
    """Tester la récupération d'un produit qui n'existe pas"""
    response = client.get("/products/999")
    assert response.status_code == 404
    error = json.loads(response.data)
    assert error == {"error": "Product not found"}

# --- Test de la création de produits ---

def test_create_product_valid(client):
    """Tester la création d'un produit valide"""
    product_data = {
        "name": "New Product",
        "price": 19.99,
        "description": "Test Description",
        "in_stock": True,
        "weight": 0.5,
        "image": "path/to/image.jpg"
    }
    response = client.post("/products", json=product_data)
    assert response.status_code == 201
    product = json.loads(response.data)
    assert product['name'] == "New Product"

def test_create_product_invalid(client):
    """Tester la création d'un produit avec des données invalides"""
    product_data = {"name": "Faulty Product", "price": -10}  # Prix négatif
    response = client.post("/products", json=product_data)
    assert response.status_code == 400
    error = json.loads(response.data)
    assert error == {"error": "Invalid 'price', must be a positive number"}

# --- Test de la mise à jour de produits ---

def test_update_product_valid(client, add_products):
    """Tester la mise à jour d'un produit valide"""
    product_id = add_products[0].id
    update_data = {"price": 22.50}
    response = client.put(f"/products/{product_id}", json=update_data)
    assert response.status_code == 200
    updated = json.loads(response.data)
    assert updated['price'] == 22.50

def test_update_product_invalid(client, add_products):
    """Tester la mise à jour d'un produit avec des données invalides"""
    product_id = add_products[0].id
    update_data = {"price": "not a number"}
    response = client.put(f"/products/{product_id}", json=update_data)
    assert response.status_code == 400
    error = json.loads(response.data)
    assert error == {"error": "Invalid 'price', must be a number"}

# --- Test de la suppression de produits ---

def test_delete_product_valid(client, add_products):
    """Tester la suppression d'un produit existant"""
    product_id = add_products[0].id
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 204

def test_delete_nonexistent_product(client):
    """Tester la suppression d'un produit inexistant"""
    response = client.delete("/products/999")
    assert response.status_code == 404
    error = json.loads(response.data)
    assert error == {"error": "Product not found"}
