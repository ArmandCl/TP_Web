from peewee import Model, CharField, FloatField, SqliteDatabase, BooleanField  
# Connexion à SQLite
db = SqliteDatabase("products.db")

class BaseModel(Model):
    class Meta:
        database = db

class Product(BaseModel):
    name = CharField()
    price = FloatField()
    description = CharField() 
    in_stock = BooleanField(default=True)  
    weight = FloatField()  
    image = CharField()
