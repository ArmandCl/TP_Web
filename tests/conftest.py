import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from app import app
from models import db

@pytest.fixture
def client():
    """Créer un client de test pour Flask"""
    app.config["TESTING"] = True
    app.config["DATABASE"] = "sqlite:///:memory:"  # Base de test temporaire
    with app.test_client() as client:
        with app.app_context():
            db.create_tables([])  # Ajouter les modèles ici
        yield client
