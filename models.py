from peewee import Model, CharField, FloatField, SqliteDatabase, BooleanField, ForeignKeyField, IntegerField, TextField

# Connexion à SQLite
db = SqliteDatabase("products.db")

class BaseModel(Model):
    class Meta:
        database = db

class Products(BaseModel):
    name = CharField()
    price = FloatField()
    description = CharField()
    in_stock = BooleanField(default=True)
    weight = FloatField()
    image = CharField()

class Orders(BaseModel):
    product = ForeignKeyField(Products, backref='orders', on_delete='CASCADE')
    quantity = IntegerField()
    email = CharField(null=True)  # Champ pour l'email du client
    shipping_information = TextField(null=True)  # Champ pour les informations de livraison (JSON)
    credit_card = TextField(null=True)  # Champ pour les informations de carte de crédit (JSON)
    paid = BooleanField(default=False)  # Champ pour indiquer si la commande est payée
    transaction = TextField(null=True)  # Champ pour les informations de transaction (JSON)