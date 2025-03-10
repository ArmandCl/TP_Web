import json

# --- Test de la création de commandes ---

def test_create_order(client):
    """Tester la création d'une commande valide"""
    response = client.post("/order", json={"product": {"id": 1, "quantity": 2}})
    assert response.status_code == 201  # Conformément à l'énoncé
    data = json.loads(response.data)
    assert "order_id" in data
    assert "location" in data

# --- Test de la création de commandes avec erreurs ---

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

def test_create_order_out_of_stock(client, add_out_of_stock_product):
    """Tester la création d'une commande avec un produit hors stock"""
    response = client.post("/order", json={"product": {"id": add_out_of_stock_product.id, "quantity": 1}})
    assert response.status_code == 422  
    data = json.loads(response.data)
    assert data == {
        "errors": {
            "product": {
                "code": "out-of-inventory",
                "name": "Le produit demandé n'est pas en inventaire"
            }
        }
    }

# --- Test de la récupération de commandes ---

def test_get_order(client, valid_order):
    """Tester la récupération d'une commande existante"""
    response = client.get(f"/order/{valid_order}") 
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Vérifications des clés attendues
    assert "order" in data
    assert "id" in data["order"]
    assert "paid" in data["order"]


def test_get_nonexistent_order(client):
    """Tester la récupération d'une commande qui n'existe pas"""
    response = client.get("/order/9999")
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data == {"error": "Order not found"}
