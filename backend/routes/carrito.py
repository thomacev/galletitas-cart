from flask import Blueprint, jsonify
from backend.database import conectar_db

carrito_blueprint = Blueprint('carrito', __name__)

@carrito_blueprint.get("/productos")
def listar_productos():
    """
    Lista todos los productos disponibles en la base de datos.
    ---
    tags:
      - Productos
    responses:
      200:
        description: Lista de productos del catálogo de la DB
      500:
        description: Error interno del servidor
    """
    try:
        conexion = conectar_db()
        db = conexion.cursor()
        
        db.execute("SELECT id, nombre, precio FROM productos")
        filas = db.fetchall()
        conexion.close()

        lista_productos = [dict(fila) for fila in filas]
        return jsonify({"productos": lista_productos}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@carrito_blueprint.get("/carrito")
def ver_carrito():
    """
    Muestra los productos en el carrito haciendo un JOIN con productos.
    ---
    tags:
      - Carrito
    responses:
      200:
        description: Contenido detallado del carrito actual
    """
    try:
        conexion = conectar_db()
        db = conexion.cursor()
        
        # Unimos las dos tablas mediante INNER JOIN para traer los datos reales de una sola pasada
        # Calculamos el subtotal directamente en la consulta SQL
        query = """
            SELECT p.id, p.nombre, p.precio, c.cantidad, (p.precio * c.cantidad) AS subtotal
            FROM carrito c
            INNER JOIN productos p ON c.producto_id = p.id
        """
        db.execute(query)
        filas = db.fetchall()
        conexion.close()

        items_carrito = [dict(fila) for fila in filas]
        return jsonify({"carrito": items_carrito}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@carrito_blueprint.get("/carrito/total")
def total_carrito():
    """
    Calcula el total general y la cantidad de items usando funciones de agregación SQL.
    ---
    tags:
      - Carrito
    responses:
      200:
        description: Sumarización del total de la compra
    """
    try:
        conexion = conectar_db()
        db = conexion.cursor()
        
        query = """
            SELECT 
                SUM(p.precio * c.cantidad) AS total,
                SUM(c.cantidad) AS cantidad_items
            FROM carrito c
            INNER JOIN productos p ON c.producto_id = p.id
        """
        db.execute(query)
        resultado = db.fetchone()
        conexion.close()

        # Si el carrito está vacío, las funciones SUM devuelven None; lo controlamos con un OR
        total = resultado["total"] if resultado["total"] is not None else 0
        cantidad_items = resultado["cantidad_items"] if resultado["cantidad_items"] is not None else 0

        return jsonify({
            "total": total,
            "cantidad_items": cantidad_items
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@carrito_blueprint.post("/carrito/<int:producto_id>")
def agregar_producto(producto_id):
    """
    Agrega una unidad de un producto al carrito (INSERT o UPDATE si ya existe).
    ---
    tags:
      - Carrito
    parameters:
      - name: producto_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Producto añadido o incrementado con éxito
      404:
        description: El producto no existe en el catálogo de la DB
    """
    try:
        conexion = conectar_db()
        db = conexion.cursor()

        # 1. Verificar si el producto existe de verdad en el catálogo
        db.execute("SELECT nombre FROM productos WHERE id = ?", (producto_id,))
        producto = db.fetchone()
        
        if not producto:
            conexion.close()
            return jsonify({"error": "Producto no encontrado en el catálogo"}), 404

        nombre_producto = producto["nombre"]

        # 2. Verificar si ya está en el carrito
        db.execute("SELECT cantidad FROM carrito WHERE producto_id = ?", (producto_id,))
        item_carrito = db.fetchone()

        if item_carrito:
            # Si ya está, sumamos 1 a la cantidad existente
            nueva_cantidad = item_carrito["cantidad"] + 1
            db.execute("UPDATE carrito SET cantidad = ? WHERE producto_id = ?", (nueva_cantidad, producto_id))
        else:
            # Si no está, hacemos el registro inicial
            db.execute("INSERT INTO carrito (producto_id, cantidad) VALUES (?, ?)", (producto_id, 1))

        conexion.commit()
        conexion.close()

        return jsonify({"mensaje": f"'{nombre_producto}' agregado al carrito."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@carrito_blueprint.delete("/carrito/<int:producto_id>")
def quitar_producto(producto_id):
    """
    Resta una unidad del producto del carrito (DELETE si llega a 0).
    ---
    tags:
      - Carrito
    parameters:
      - name: producto_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Unidad restada o fila eliminada
      404:
        description: El producto no se encuentra en el carrito
    """
    try:
        conexion = conectar_db()
        db = conexion.cursor()

        # Traemos la cantidad actual y el nombre vinculando con productos
        query = """
            SELECT c.cantidad, p.nombre 
            FROM carrito c
            INNER JOIN productos p ON c.producto_id = p.id
            WHERE c.producto_id = ?
        """
        db.execute(query, (producto_id,))
        resultado = db.fetchone()

        if not resultado:
            conexion.close()
            return jsonify({"error": "El producto no está en el carrito"}), 404

        cantidad_actual = resultado["cantidad"]
        nombre_producto = resultado["nombre"]

        if cantidad_actual > 1:
            # Reducimos en uno la cantidad
            nueva_cantidad = cantidad_actual - 1
            db.execute("UPDATE carrito SET cantidad = ? WHERE producto_id = ?", (nueva_cantidad, producto_id))
            mensaje = f"Una unidad de '{nombre_producto}' quitada del carrito."
        else:
            # Si era la última unidad, limpiamos el registro de la tabla
            db.execute("DELETE FROM carrito WHERE producto_id = ?", (producto_id,))
            mensaje = f"'{nombre_producto}' eliminado por completo del carrito."

        conexion.commit()
        conexion.close()

        return jsonify({"mensaje": mensaje}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500