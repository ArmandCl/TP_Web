from flask import Flask, render_template
from flask_restful import Api
from models import Orders, db, Products
from ressources import OrderResource, ProductResource
from functions import fetch_and_store_products

app = Flask(__name__)

        
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
    db.drop_tables([Orders])
    db.create_tables([Products])
    db.create_tables([Orders])

    # Récupération et stockage des produits de l'API externe
    fetch_and_store_products()

    # Affichage des produits stockés
    #for product in Products.select():
    #    print(f"{product.id}: {product.name} - {product.price} - {product.description}")

if __name__ == '__main__':
    app.run(debug=True)
    
