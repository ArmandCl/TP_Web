import json

def test_create_order(client):
    """Tester la création d'une commande valide"""
    response = client.post("/order", json={"product": {"id": 1, "quantity": 2}})
    assert response.status_code == 201  # Conformément à l'énoncé
    data = json.loads(response.data)
    assert "order_id" in data
    assert "location" in data

def test_create_order_missing_product(client):
    """Tester la création d'une commande sans 'product'"""
    response = client.post("/order", json={})
    assert response.status_code == 422
    data = json.loads(response.data)
    assert data == {
        "errors": {
            "product": {
                "code": "missing-fields",
                "name": "La création d'une commande nécessite un produit"
            }
        }
    }

def test_create_order_quantity_zero(client):
    """Tester la création d'une commande avec une quantité invalide (0)"""
    response = client.post("/order", json={"product": {"id": 1, "quantity": 0}})
    assert response.status_code == 422
    data = json.loads(response.data)
    assert data == {
        "errors": {
            "product": {
                "code": "missing-fields",
                "name": "La quantité doit être supérieure ou égale à 1"
            }
        }
    }

def test_create_order_out_of_stock(client):
    """Tester la création d'une commande avec un produit hors stock"""
    response = client.post("/order", json={"product": {"id": 9999, "quantity": 1}})
    assert response.status_code == 422  # Modifié pour coller à l'énoncé
    data = json.loads(response.data)
    assert data == {
        "errors": {
            "product": {
                "code": "out-of-inventory",
                "name": "Le produit demandé n'est pas en inventaire"
            }
        }
    }

def test_get_nonexistent_order(client):
    """Tester la récupération d'une commande qui n'existe pas"""
    response = client.get("/order/9999")
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data == {"error": "Order not found"}
