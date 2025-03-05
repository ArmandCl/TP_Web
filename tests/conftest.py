# conftest.py
import json
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from app import app
from models import Orders, db, Products

@pytest.fixture
def client():
    """Créer un client de test pour Flask"""
    app.config["TESTING"] = True
    app.config["DATABASE"] = "sqlite:///:memory:"  # Base de test temporaire
    with app.test_client() as client:
        with app.app_context():
            db.create_tables([Products]) 
        yield client

@pytest.fixture
def add_products(client):
    """Fixture pour ajouter des produits avant les tests."""
    products = [
        Products.create(name="Produit Test 1", price=10.99, description="Description du premier produit", in_stock=True, weight=0.5, image=""),
        Products.create(name="Produit Test 2", price=15.49, description="Description du second produit", in_stock=False, weight=0.75, image=""),
    ]
    for product in products:
        print(f"Produit ajouté: {product.name, product.id}")
    yield products 
    for product in products:
        product.delete_instance()

@pytest.fixture
def add_out_of_stock_product(client):
    """Ajoute un produit hors stock dans la base de données de test."""
    product = Products.create(
        id=9999,  
        name="Produit hors stock",
        price=20.00,
        description="Ce produit est hors stock",
        in_stock=False,  # Marqué hors stock
        weight=1.0,
        image=""
    )
    yield product  # Passe le produit aux tests
    product.delete_instance()  # Nettoyage après les tests

@pytest.fixture
def add_unpaid_order(client):
    """Créer une commande NON PAYÉE pour tester les paiements."""
    # Ajouter un produit pour la commande
    product = Products.create(name="Produit Test", price=25.00, description="Produit de test", in_stock=True, weight=1.0, image="")

    # Créer une commande non payée
    response = client.post("/order", json={"product": {"id": product.id, "quantity": 1}})
    order_data = json.loads(response.data)

    yield order_data["order_id"]  # Retourne l'ID de la commande non payée

@pytest.fixture
def add_paid_order(client):
    """Créer une commande DÉJÀ PAYÉE pour tester les erreurs 'already-paid'."""
    product = Products.create(name="Produit Déjà Payé", price=50.00, description="Un produit déjà payé", in_stock=True, weight=1.0, image="")

    # Créer la commande
    response = client.post("/order", json={"product": {"id": product.id, "quantity": 1}})
    order_data = json.loads(response.data)
    order_id = order_data["order_id"]

    # Marquer la commande comme payée (simulation d'un paiement réussi)
    order = Orders.get(Orders.id == order_id)
    order.paid = True
    order.save()

    yield order_id  # Retourne l'ID de la commande déjà payée