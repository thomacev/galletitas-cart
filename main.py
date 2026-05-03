from flask import Flask, jsonify
from flasgger import Swagger
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
swagger = Swagger(app)

#peso argentino
products = [{"id": 1, "name": "Don satur", "price": 1200, "quantity": 0},
            {"id": 2, "name": "Surtidas Bagley", "price": 3200, "quantity": 0},
            {"id": 3, "name": "Oreo", "price": 2200, "quantity": 0},
            {"id": 4, "name": "Chocolinas", "price": 2000, "quantity": 0},
            {"id": 5, "name": "Marmoladas fantoche", "price": 1700, "quantity": 0}]
cart = []

@app.route("/")
def show_products():
    """
    Lista de productos disponibles
    ---
    tags:
      - Productos
    responses:
      200:
        description: Lista de productos
        schema:
          type: object
          properties:
            menu:
              type: array
              items:
                type: object
                properties:
                  name:
                    type: string
                  price:
                    type: integer
        examples:
          application/json:
            menu:
              - name: Don satur
                price: 1200
    """
    result = {"menu":[{"name": product["name"], "price": product["price"]} for product in products]}
    return result

@app.get("/total")
def cart_total():
    """
    Calcula el total del carrito
    ---
    tags:
      - Carrito
    responses:
      200:
        description: Total de la compra
        examples:
          application/json:
            total: 5400
    """
    total = sum(product["price"] * product["quantity"] for product in cart)
    return {"total": total}

@app.get("/carrito")
def show_cart():
    """
    Muestra el carrito actual
    ---
    tags:
      - Carrito
    responses:
      200:
        description: Productos en el carrito
    """
    result = {"cart":[{"name": product["name"], "price": product["price"], "id": product["id"], "quantity": product["quantity"]} for product in cart]}
    return result

@app.post("/producto/<int:product_id>")
def add_to_cart(product_id):
    """
    Agrega un producto al carrito
    ---
    tags:
      - Carrito
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID del producto
    responses:
      200:
        description: Producto agregado
      404:
        description: Producto no encontrado
    """
    #encuentra el primer producto segun el id dado, si no entonces None
    product = next((p for p in products if p["id"] == product_id), None)
    if product:
        if product in cart:
            cart[cart.index(product)]["quantity"] += 1
        else:
            product["quantity"] = 1
            cart.append(product)
        return {"message": f"{product['name']} agregado al carrito"}
    return {"error": "Producto no encontrado"}, 404

#los id se pueden repetir, por lo que se elimina el primero que se encuentra
@app.delete("/producto/<int:product_id>")
def remove_from_cart(product_id):
    """
    Elimina un producto del carrito
    ---
    tags:
      - Carrito
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID del producto
    responses:
      200:
        description: Producto eliminado
      404:
        description: Producto no encontrado
    """
    product = next((p for p in cart if p["id"] == product_id), None)
    if product:
        if product["quantity"] > 1:
            cart[cart.index(product)]["quantity"] -= 1
        else:
            cart.remove(product)
        return {"message": f"{product['name']} eliminado del carrito"}
    return {"error": "Producto no encontrado"}, 404

if __name__ == "__main__":
    app.run(debug=True)