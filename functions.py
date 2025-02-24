import urllib.request
import json
from models import Products, db


PAIEMENT_URL = "http://dimensweb.uqac.ca/~jgnault/shops/pay/"
PRODUCTS_URL = "http://dimensweb.uqac.ca/~jgnault/shops/products/"

def fetch_and_store_products():
    """Récupère les produits de l'API externe et les stocke en base de données."""
    try:
        with urllib.request.urlopen(PRODUCTS_URL) as response:
            data = json.load(response)  # Charge directement en JSON

        products = data.get("products", [])

        with db.atomic():  # Optimisation des requêtes SQL
            for product in products:
                Products.get_or_create(
                    id=product["id"],
                    defaults={
                        "name": product["name"],
                        "description": product.get("description", ""),
                        "price": product["price"],
                        "in_stock": product["in_stock"],
                        "weight": product["weight"],
                        "image": product["image"]
                    }
                )

        print(" Produits récupérés et stockés avec succès !")

    except Exception as e:
        print(f" Erreur lors de la récupération des produits : {e}")


def process_payment(credit_card, amount_charged):
    payload = {
        "credit_card": credit_card,
        "amount_charged": amount_charged
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(PAIEMENT_URL, data=data, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)  # Toujours retourner un dictionnaire
    except urllib.error.HTTPError as e:
        error_response = {
            "errors": {
                "payment": {
                    "code": "payment-failed",
                    "name": f"Le paiement a échoué avec le code HTTP {e.code}"
                }
            }
        }
        return error_response  # Retourne seulement un dictionnaire
    except Exception as e:
        error_response = {
            "errors": {
                "payment": {
                    "code": "payment-failed",
                    "name": f"Le paiement a échoué : {str(e)}"
                }
            }
        }
        return error_response  # Retourne seulement un dictionnaire

def validate_credit_card(credit_card):
    required_fields = ["name", "number", "expiration_year", "expiration_month", "cvv"]
    for field in required_fields:
        if field not in credit_card or not credit_card[field]:
            return False
    return True