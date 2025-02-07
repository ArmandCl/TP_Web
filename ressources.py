from flask import jsonify, request
from flask_restful import Resource
from models import Products, Orders
from playhouse.shortcuts import model_to_dict
import json

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


class OrderResource(Resource):
    def post(self):
        data = request.get_json()

        # Vérification que le champ "product" est présent
        if "product" not in data or "id" not in data["product"] or "quantity" not in data["product"]:
            return {
                "errors": {
                    "product": {
                        "code": "missing-fields",
                        "name": "La création d'une commande nécessite un produit"
                    }
                }
            }, 422

        product_id = data["product"]["id"]
        quantity = data["product"]["quantity"]

        # Vérification que la quantité est valide
        if quantity < 1:
            return {
                "errors": {
                    "product": {
                        "code": "missing-fields",
                        "name": "La quantité doit être supérieure ou égale à 1"
                    }
                }
            }, 422

        # Vérifier si le produit existe
        product = Products.get_or_none(Products.id == product_id)
        if not product:
            return {"error": "Product not found"}, 404

        # Vérifier si le produit est en stock
        if not product.in_stock:
            return {
                "errors": {
                    "product": {
                        "code": "out-of-inventory",
                        "name": "Le produit demandé n'est pas en inventaire"
                    }
                }
            }, 422

        # Création de la commande
        new_order = Orders.create(product=product, quantity=quantity)

        # Retourner un 201 avec l'URL de la commande
        return {
            "order_id": new_order.id,
            "location": f"/order/{new_order.id}"
        }, 201

    def get(self, order_id=None):
        if order_id:
            order = Orders.get_or_none(Orders.id == order_id)
            if not order:
                return {"error": "Order not found"}, 404

            # Calcul du prix total et des taxes
            total_price = order.product.price * order.quantity

            # Récupérer la province depuis shipping_information (si disponible)
            shipping_info = json.loads(order.shipping_information) if order.shipping_information else {}
            province = shipping_info.get("province", "")
            tax_rate = self.get_tax_rate(province)
            total_price_tax = total_price * (1 + tax_rate)

            # Construction de la réponse
            order_data = {
                "id": order.id,
                "total_price": total_price,
                "total_price_tax": total_price_tax,
                "email": order.email,
                "credit_card": json.loads(order.credit_card) if order.credit_card else {},
                "shipping_information": shipping_info,
                "paid": order.paid,
                "transaction": json.loads(order.transaction) if order.transaction else {},
                "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price,
                    "quantity": order.quantity
                },
                "shipping_price": self.calculate_shipping_price(order.product.weight * order.quantity)
            }

            return jsonify(order_data)
        else:
            # Récupérer toutes les commandes
            all_orders = Orders.select()
            orders_list = []
            for order in all_orders:
                total_price = order.product.price * order.quantity

                # Récupérer la province depuis shipping_information (si disponible)
                shipping_info = json.loads(order.shipping_information) if order.shipping_information else {}
                province = shipping_info.get("province", "")
                tax_rate = self.get_tax_rate(province)
                total_price_tax = total_price * (1 + tax_rate)

                orders_list.append({
                    "id": order.id,
                    "total_price": total_price,
                    "total_price_tax": total_price_tax,
                    "email": order.email,
                    "paid": order.paid,
                    "product": {
                        "id": order.product.id,
                        "name": order.product.name,
                        "price": order.product.price,
                        "quantity": order.quantity
                    },
                    "shipping_price": self.calculate_shipping_price(order.product.weight * order.quantity)
                })

            return jsonify(orders_list)

    def get_tax_rate(self, province):
        tax_rates = {
            "QC": 0.15,
            "ON": 0.13,
            "AB": 0.05,
            "BC": 0.12,
            "NS": 0.14
        }
        return tax_rates.get(province, 0)

    def calculate_shipping_price(self, total_weight):
        if total_weight <= 500:
            return 5
        elif total_weight <= 2000:
            return 10
        else:
            return 25