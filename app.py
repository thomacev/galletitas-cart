#Mercado de galletitas
from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

products = [
    {"id": 1, "name": "Don Satur","price": 1200},
    {"id": 2, "name": "Surtidas Bagley","price": 3200},
    {"id": 3, "name": "Oreo","price": 2200},
    {"id": 4, "name": "Chocolinas","price": 2000},
    {"id": 5, "name": "Marmoladas Fantoche","price": 1700},
    {"id": 6, "name": "Merengadas","price": 2200},
    {"id": 7, "name": "Pitusas","price": 1200},
    {"id": 8, "name": "9 de oro","price": 1500},
    {"id": 9, "name": "Surtidas diversion","price": 2800},
    {"id": 10, "name": "Obleas","price": 900},
]

cart = []  


def find_product(product_id):
    return next((p for p in products if p["id"] == product_id), None)


def find_cart_item(product_id):
    return next((p for p in cart if p["id"] == product_id), None)


@app.get("/productos")
def listar_productos():
    """
    Lista todos los productos disponibles.
    ---
    tags:
      - Productos
    responses:
      200:
        description: Lista de productos del catálogo
        schema:
          type: object
          properties:
            productos:
              type: array
              items:
                type: object
                properties:
                  id:    { type: integer, example: 1 }
                  name:  { type: string,  example: "Oreo" }
                  price: { type: integer, example: 2200 }
    """
    return jsonify({"productos": products})


@app.get("/carrito")
def ver_carrito():
    """
    Muestra los productos que hay en el carrito.
    ---
    tags:
      - Carrito
    responses:
      200:
        description: Contenido actual del carrito
        schema:
          type: object
          properties:
            carrito:
              type: array
              items:
                type: object
                properties:
                  id:       { type: integer }
                  name:     { type: string }
                  price:    { type: integer }
                  quantity: { type: integer }
                  subtotal: { type: integer }
    """
    
    items = [
        {**item, "subtotal": item["price"] * item["quantity"]}
        for item in cart
    ]
    return jsonify({"carrito": items})


@app.get("/carrito/total")
def total_carrito():
    """
    Calcula el total a pagar del carrito.
    ---
    tags:
      - Carrito
    responses:
      200:
        description: Total de la compra
        schema:
          type: object
          properties:
            total:          { type: integer, example: 5400 }
            cantidad_items: { type: integer, example: 3 }
    """
    total = sum(item["price"] * item["quantity"] for item in cart)
    cantidad = sum(item["quantity"] for item in cart)
    return jsonify({"total": total, "cantidad_items": cantidad})


@app.post("/carrito/<int:product_id>")
def agregar_producto(product_id):
    """
    Agrega una unidad de un producto al carrito.
    ---
    tags:
      - Carrito
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID del producto a agregar
    responses:
      200:
        description: Producto agregado correctamente
      404:
        description: Producto no encontrado en el catálogo
    """
    product = find_product(product_id)
    if not product:
        return jsonify({"error": "Producto no encontrado"}), 404

    cart_item = find_cart_item(product_id)
    if cart_item:
        cart_item["quantity"] += 1
    else:
        # el operador ** es para no tener que escribir cada campo del producto manualmente
        cart.append({**product, "quantity": 1})

    return jsonify({"mensaje": f"'{product['name']}' agregado al carrito."})


@app.delete("/carrito/<int:product_id>")
def quitar_producto(product_id):
    """
    Quita una unidad de un producto del carrito.
    Si la cantidad llega a 0, se elimina del carrito.
    ---
    tags:
      - Carrito
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID del producto a quitar
    responses:
      200:
        description: Unidad eliminada o producto removido del carrito
      404:
        description: Producto no encontrado en el carrito
    """
    cart_item = find_cart_item(product_id)
    if not cart_item:
        return jsonify({"error": "El producto no está en el carrito"}), 404

    cart_item["quantity"] -= 1
    nombre = cart_item["name"]

    if cart_item["quantity"] == 0:
        cart.remove(cart_item)
        return jsonify({"mensaje": f"'{nombre}' eliminado del carrito."})

    return jsonify({"mensaje": f"Una unidad de '{nombre}' quitada del carrito."})


if __name__ == "__main__":
    app.run(debug=True)