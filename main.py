from flask import Flask

"""
Etapa 1: Backend con APIs
Descripción: Implementar un servidor backend que exponga una serie de APIs RESTful para gestionar un carrito de compras de galletitas
Requerimientos mínimos:
Endpoints para:
Listar productos disponibles
Agregar productos al carrito
Eliminar productos del carrito
Calcular el total de la compra
Persistencia inicial en memoria (sin base de datos)
Documentación de las APIs (por ejemplo, con Swagger/OpenAPI)
Tests unitarios de los endpoints principales
"""

app = Flask(__name__)

#peso argentino
products = [{"id": 1, "name": "Don satur", "price": 1200},
            {"id": 2, "name": "Surtidas Bagley", "price": 3200},
            {"id": 3, "name": "Oreo", "price": 2200},
            {"id": 4, "name": "Chocolinas", "price": 2000},
            {"id": 5, "name": "Marmoladas fantoche", "price": 1700}]

cart = []

@app.route("/")
def show_products():
    result = {"menu":[{"name": product["name"], "price": product["price"]} for product in products]}
    return result

@app.get("/total")
def cart_total():
    total = sum(product["price"] for product in cart)
    return {"total": total}

@app.get("/carrito")
def show_cart():
    result = {"cart":[{"name": product["name"], "price": product["price"], "id": product["id"]} for product in cart]}
    return result

@app.post("/producto/<int:product_id>")
def add_to_cart(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        cart.append(product)
        return {"message": f"{product['name']} agregado al carrito"}
    return {"error": "Producto no encontrado"}, 404

#los id se pueden repetir, por lo que se elimina el primero que se encuentra
@app.delete("/producto/<int:product_id>")
def remove_from_cart(product_id):
    product = next((p for p in cart if p["id"] == product_id), None)
    if product:
        cart.remove(product)
        return {"message": f"{product['name']} eliminado del carrito"}
    return {"error": "Producto no encontrado"}, 404

if __name__ == "__main__":
    app.run(debug=True)