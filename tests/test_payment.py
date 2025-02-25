import json
from unittest.mock import patch

@patch("requests.post")
def test_payment_success(mock_post, client):
    """Tester un paiement réussi avec une carte valide"""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "transaction": {"id": "123456", "success": True, "amount_charged": 100}
    }

    client.put("/order/1", json={"email": "client@example.com", "shipping_information": {
        "country": "Canada",
        "address": "123 rue du Client",
        "postal_code": "G7X 3Y7",
        "city": "Chicoutimi",
        "province": "QC"
    }})

    response = client.put("/order/1", json={"credit_card": {
        "name": "John Doe",
        "number": "4242 4242 4242 4242",
        "expiration_year": 2025,
        "expiration_month": 9,
        "cvv": "123"
    }})

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["order"]["paid"] is True

@patch("requests.post")
def test_payment_missing_email(mock_post, client):
    """Tester un paiement sans email et informations d'expédition"""
    response = client.put("/order/1", json={"credit_card": {
        "name": "John Doe",
        "number": "4242 4242 4242 4242",
        "expiration_year": 2025,
        "expiration_month": 9,
        "cvv": "123"
    }})

    assert response.status_code == 422
    data = json.loads(response.data)
    assert data == {
        "errors": {
            "order": {
                "code": "missing-fields",
                "name": "Les informations du client sont nécessaires avant d'appliquer une carte de crédit"
            }
        }
    }

@patch("requests.post")
def test_payment_already_paid(mock_post, client):
    """Tester un paiement sur une commande déjà payée"""
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {
        "errors": {
            "order": {
                "code": "already-paid",
                "name": "La commande a déjà été payée."
            }
        }
    }

    response = client.put("/order/1", json={"credit_card": {
        "name": "John Doe",
        "number": "4242 4242 4242 4242",
        "expiration_year": 2025,
        "expiration_month": 9,
        "cvv": "123"
    }})

    assert response.status_code == 422
    data = json.loads(response.data)
    assert data == {
        "errors": {
            "order": {
                "code": "already-paid",
                "name": "La commande a déjà été payée."
            }
        }
    }

@patch("requests.post")
def test_payment_declined(mock_post, client):
    """Tester un paiement refusé par la banque"""
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {
        "errors": {
            "credit_card": {
                "code": "card-declined",
                "name": "La carte de crédit a été déclinée"
            }
        }
    }

    response = client.put("/order/1", json={"credit_card": {
        "name": "John Doe",
        "number": "4000 0000 0000 0002",
        "expiration_year": 2025,
        "expiration_month": 9,
        "cvv": "123"
    }})

    assert response.status_code == 422
    data = json.loads(response.data)
    assert data == {
        "errors": {
            "credit_card": {
                "code": "card-declined",
                "name": "La carte de crédit a été déclinée"
            }
        }
    }
