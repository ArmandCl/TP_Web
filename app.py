from flask import Flask, render_template
from flask_restful import Api
import urllib.request
import json
from models import Orders, db, Products
from ressources import OrderResource, ProductResource

app = Flask(__name__)

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

# Initialisation de l'API REST
api = Api(app)
api.add_resource(ProductResource, '/products', '/products/<int:product_id>')
api.add_resource(OrderResource, '/order', '/order/<int:order_id>')

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/products_table')
def products():
    products = Products.select()
    return render_template('products.html', products=products)

# Création de la base de données et récupération des produits
with app.app_context():
    db.connect()
    #db.drop_tables([Products, Orders])
    db.create_tables([Products])
    db.create_tables([Orders])

    # Récupération et stockage des produits de l'API externe
    fetch_and_store_products()

    # Affichage des produits stockés
    #for product in Products.select():
    #    print(f"{product.id}: {product.name} - {product.price} - {product.description}")

if __name__ == '__main__':
    app.run(debug=True)
    
