import json
from unittest.mock import patch

# --- Test de paiement réussi ---

@patch("requests.post")
def test_payment_success(mock_post, client, add_unpaid_order):
    """Tester un paiement réussi avec une carte valide"""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "transaction": {"id": "123456", "success": True, "amount_charged": 100}
    }

    # Ajout des infos client AVANT le paiement
    response = client.put(f"/order/{add_unpaid_order}", json={
        "email": "client@example.com", "shipping_information": {
        "country": "Canada",
        "address": "123 rue du Client",
        "postal_code": "G7X 3Y7",
        "city": "Chicoutimi",
        "province": "QC"
    }})
    assert response.status_code == 200 

    # Effectuer le paiement
    response = client.put(f"/order/{add_unpaid_order}", json={"credit_card": {
        "name": "John Doe",
        "number": "4242 4242 4242 4242",
        "expiration_year": 2025,
        "expiration_month": 9,
        "cvv": "123"
    }})

    data = json.loads(response.data)
    assert data["order"]["paid"] is True

# --- Test des erreurs de paiement ---

@patch("requests.post")
def test_payment_missing_email(mock_post, client, add_unpaid_order):
    """Tester un paiement sans email et informations d'expédition"""
    response = client.put(f"/order/{add_unpaid_order}", json={"credit_card": {
        "name": "John Doe",
        "number": "4242 4242 4242 4242",
        "expiration_year": 2025,
        "expiration_month": 9,
        "cvv": "123"
    }})

    assert response.status_code == 422
    data = json.loads(response.data)
    
    # Vérifier que l'API bloque bien pour manque d'infos client
    assert data["errors"]["order"]["code"] == "missing-fields", f"Erreur API: {response.data}"


@patch("requests.post")
def test_payment_already_paid(mock_post, client, add_paid_order):
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

    # Ajout des infos client AVANT le paiement
    response = client.put(f"/order/{add_paid_order}", json={
        "email": "client@example.com",
        "shipping_information": {
            "country": "Canada",
            "address": "123 rue du Client",
            "postal_code": "G7X 3Y7",
            "city": "Chicoutimi",
            "province": "QC"
        }
    })
    assert response.status_code == 200

    response = client.put(f"/order/{add_paid_order}", json={"credit_card": {
        "name": "John Doe",
        "number": "4242 4242 4242 4242",
        "expiration_year": 2025,
        "expiration_month": 9,
        "cvv": "123"
    }})

    assert response.status_code == 422
    data = json.loads(response.data)

    # Vérifier que l'API bloque bien pour commande déjà payée
    assert data["errors"]["order"]["code"] == "already-paid", f"Erreur API: {response.data}"



@patch("requests.post")
def test_payment_declined(mock_post, client, add_unpaid_order):
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

    # Ajout des infos client AVANT le paiement
    response = client.put(f"/order/{add_unpaid_order}", json={
        "email": "client@example.com", "shipping_information": {
        "country": "Canada",
        "address": "123 rue du Client",
        "postal_code": "G7X 3Y7",
        "city": "Chicoutimi",
        "province": "QC"
    }})
    assert response.status_code == 200

    response = client.put(f"/order/{add_unpaid_order}", json={"credit_card": {
        "name": "John Doe",
        "number": "4000 0000 0000 0002",  # Simule une carte refusée
        "expiration_year": 2025,
        "expiration_month": 9,
        "cvv": "123"
    }})

    assert response.status_code == 422
    data = json.loads(response.data)

    assert "credit_card" in data["errors"], f"Erreur API: {response.data}"
    assert data["errors"]["credit_card"]["code"] == "card-declined"


