from flask import jsonify, request
from flask_restful import Resource
from models import Products, db
from playhouse.shortcuts import model_to_dict

class ProductResource(Resource):

    def get(self, product_id=None):
        if product_id:
            product = Products.get_or_none(Products.id == product_id)
            if product:
                return jsonify(model_to_dict(product))
            return {"error": "Product not found"}, 404
        else:
            all_products = Products.select()
            return jsonify([model_to_dict(product) for product in all_products])
  
        
    def post(self):
        if not request.is_json:
            return {"error": "Invalid input, JSON required"}, 400

        try:
            new_product_data = request.get_json()

            if "name" not in new_product_data or "price" not in new_product_data:
                return {"error": "Missing fields: 'name' and 'price' are required"}, 400

            try:
                price = float(new_product_data['price'])
                if price <= 0:
                    return {"error": "Invalid 'price', must be a positive number"}, 400
            except ValueError:
                return {"error": "Invalid 'price', must be a number"}, 400

            new_product = Products.create(
                name=new_product_data['name'],
                price=price,
                description=new_product_data.get('description', ''),
                in_stock=new_product_data.get('in_stock', True),
                weight=new_product_data.get('weight', 0.0),
                image=new_product_data.get('image', '')
            )

            return model_to_dict(new_product), 201

        except Exception as e:
            print(f"Erreur lors de l'ajout du produit : {e}")
            return {"error": str(e)}, 500
        
        
    def put(self, product_id):
        if not request.is_json:
            return {"error": "Invalid input, JSON required"}, 400

        try:
            product = Products.get_or_none(Products.id == product_id)
            if not product:
                return {"error": "Product not found"}, 404

            update_data = request.get_json()

            if 'name' in update_data:
                product.name = update_data['name']
            if 'price' in update_data:
                try:
                    price = float(update_data['price'])
                    if price <= 0:
                        return {"error": "Invalid 'price', must be a positive number"}, 400
                    product.price = price
                except ValueError:
                    return {"error": "Invalid 'price', must be a number"}, 400
            if 'description' in update_data:
                product.description = update_data['description']
            if 'in_stock' in update_data:
                product.in_stock = update_data['in_stock']
            if 'weight' in update_data:
                product.weight = update_data['weight']
            if 'image' in update_data:
                product.image = update_data['image']

            product.save()
            return jsonify(model_to_dict(product))

        except Exception as e:
            return {"error": str(e)}, 500
        
    def delete(self, product_id):
        product = Products.get_or_none(Products.id == product_id)
        if not product:
            return {"error": "Product not found"}, 404

        product.delete_instance()
        return '', 204
