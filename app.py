from flask import Flask, render_template
from flask_restful import Api
from models import db, Product
from ressources import ProductResource

app = Flask(__name__)

# Initialisation de l'API REST
api = Api(app)
api.add_resource(ProductResource, '/products', '/products/<int:product_id>')

@app.route('/')
def hello_world():
    return render_template('hello.html')

# Création de la base de données
with app.app_context():
    db.connect()
    db.create_tables([Product])

    # Ajout de données de test
    if not Product.select().exists():
        Product.create(name="Banane", price=1.5, description="Fruit jaune", weight=0.2, image="banane.jpg")
        Product.create(name="Pomme", price=2.0, description="Fruit rouge", weight=0.3, image="pomme.jpg")
        Product.create(name="Poire", price=1.8, description="Fruit vert", weight=0.25, image="poire.jpg")

    # Affichage des produits pour vérifier
    for product in Product.select():
        print(f"{product.id}: {product.name} - {product.price} - {product.description}")

if __name__ == '__main__':
    app.run(debug=True)
