# Mercado de galletitas
from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

productos = [
    {"id": 1, "nombre": "Don Satur", "precio": 1200},
    {"id": 2, "nombre": "Surtidas Bagley", "precio": 3200},
    {"id": 3, "nombre": "Oreo", "precio": 2200},
    {"id": 4, "nombre": "Chocolinas", "precio": 2000},
    {"id": 5, "nombre": "Marmoladas Fantoche", "precio": 1700},
    {"id": 6, "nombre": "Merengadas", "precio": 2200},
    {"id": 7, "nombre": "Pitusas", "precio": 1200},
    {"id": 8, "nombre": "9 de oro", "precio": 1500},
    {"id": 9, "nombre": "Surtidas diversion", "precio": 2800},
    {"id": 10, "nombre": "Obleas", "precio": 900},
]

carrito = []  


def buscar_producto(producto_id):
    return next((p for p in productos if p["id"] == producto_id), None)


def buscar_item_carrito(producto_id):
    return next((p for p in carrito if p["id"] == producto_id), None)


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
                  id:     { type: integer, example: 1 }
                  nombre: { type: string,  example: "Oreo" }
                  precio: { type: integer, example: 2200 }
    """
    return jsonify({"productos": productos})


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
                  nombre:   { type: string }
                  precio:   { type: integer }
                  cantidad: { type: integer }
                  subtotal: { type: integer }
    """
    
    items = [
        {**item, "subtotal": item["precio"] * item["cantidad"]}
        for item in carrito
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
    total = sum(item["precio"] * item["cantidad"] for item in carrito)
    cantidad = sum(item["cantidad"] for item in carrito)
    return jsonify({"total": total, "cantidad_items": cantidad})


@app.post("/carrito/<int:producto_id>")
def agregar_producto(producto_id):
    """
    Agrega una unidad de un producto al carrito.
    ---
    tags:
      - Carrito
    parameters:
      - name: producto_id
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
    producto = buscar_producto(producto_id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    item_carrito = buscar_item_carrito(producto_id)
    if item_carrito:
        item_carrito["cantidad"] += 1
    else:
        #El desempaquetado es para copiar los datos del producto y despues agregar la cantidad
        carrito.append({**producto, "cantidad": 1})

    return jsonify({"mensaje": f"'{producto['nombre']}' agregado al carrito."})


@app.delete("/carrito/<int:producto_id>")
def quitar_producto(producto_id):
    """
    Quita una unidad de un producto del carrito.
    Si la cantidad llega a 0, se elimina del carrito.
    ---
    tags:
      - Carrito
    parameters:
      - name: producto_id
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
    item_carrito = buscar_item_carrito(producto_id)
    if not item_carrito:
        return jsonify({"error": "El producto no está en el carrito"}), 404

    item_carrito["cantidad"] -= 1
    nombre = item_carrito["nombre"]

    if item_carrito["cantidad"] == 0:
        carrito.remove(item_carrito)
        return jsonify({"mensaje": f"'{nombre}' eliminado del carrito."})

    return jsonify({"mensaje": f"Una unidad de '{nombre}' quitada del carrito."})


if __name__ == "__main__":
    app.run(debug=True)