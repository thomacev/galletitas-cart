"""
Tests de API (integración) — hablan directo con Flask vía test_client.
No necesitan navegador ni Selenium.
Reemplazan los tests viejos; el único cambio real es el fixture reset_estado,
que ahora limpia la tabla de SQLite en lugar de un dict en memoria.
"""
import pytest
from backend.main import create_app
from backend.database import conectar_db


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

def _limpiar_carrito():
    """Vacía la tabla carrito en la base de datos de test."""
    con = conectar_db()
    con.execute("DELETE FROM carrito")
    con.commit()
    con.close()


@pytest.fixture(autouse=True)
def reset_estado():
    """Limpia el carrito antes y después de cada test."""
    _limpiar_carrito()
    yield
    _limpiar_carrito()


@pytest.fixture
def cliente():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# ─────────────────────────────────────────────────────────────────────────────
# GET /productos
# ─────────────────────────────────────────────────────────────────────────────

class TestListarProductos:
    def test_retorna_200(self, cliente):
        res = cliente.get("/productos")
        assert res.status_code == 200

    def test_respuesta_tiene_clave_productos(self, cliente):
        data = cliente.get("/productos").get_json()
        assert "productos" in data

    def test_productos_tienen_precio_positivo(self, cliente):
        data = cliente.get("/productos").get_json()
        for p in data["productos"]:
            assert p["precio"] > 0

    def test_productos_tienen_id_y_nombre(self, cliente):
        data = cliente.get("/productos").get_json()
        for p in data["productos"]:
            assert "id" in p
            assert "nombre" in p


# ─────────────────────────────────────────────────────────────────────────────
# GET /carrito
# ─────────────────────────────────────────────────────────────────────────────

class TestVerCarrito:
    def test_retorna_200(self, cliente):
        res = cliente.get("/carrito")
        assert res.status_code == 200

    def test_carrito_vacio_al_inicio(self, cliente):
        data = cliente.get("/carrito").get_json()
        assert data["carrito"] == []

    def test_item_tiene_subtotal_correcto(self, cliente):
        cliente.post("/carrito/1")
        cliente.post("/carrito/1")
        data = cliente.get("/carrito").get_json()
        item = data["carrito"][0]
        assert item["subtotal"] == item["precio"] * item["cantidad"]


# ─────────────────────────────────────────────────────────────────────────────
# GET /carrito/total
# ─────────────────────────────────────────────────────────────────────────────

class TestTotalCarrito:
    def test_total_cero_con_carrito_vacio(self, cliente):
        data = cliente.get("/carrito/total").get_json()
        assert data["total"] == 0
        assert data["cantidad_items"] == 0

    def test_total_correcto_un_producto(self, cliente):
        cliente.post("/carrito/3")  # Oreo $2200
        data = cliente.get("/carrito/total").get_json()
        assert data["total"] == 2200
        assert data["cantidad_items"] == 1

    def test_total_correcto_multiples_unidades(self, cliente):
        cliente.post("/carrito/3")  # Oreo $2200
        cliente.post("/carrito/3")  # Oreo $2200
        cliente.post("/carrito/4")  # Chocolinas $2000
        data = cliente.get("/carrito/total").get_json()
        assert data["total"] == 2200 * 2 + 2000
        assert data["cantidad_items"] == 3


# ─────────────────────────────────────────────────────────────────────────────
# POST /carrito/<id>
# ─────────────────────────────────────────────────────────────────────────────

class TestAgregarProducto:
    def test_agregar_producto_existente_retorna_200(self, cliente):
        res = cliente.post("/carrito/1")
        assert res.status_code == 200

    def test_agregar_producto_inexistente_retorna_404(self, cliente):
        res = cliente.post("/carrito/999")
        assert res.status_code == 404

    def test_agregar_incrementa_cantidad(self, cliente):
        cliente.post("/carrito/2")
        cliente.post("/carrito/2")
        data = cliente.get("/carrito").get_json()
        assert data["carrito"][0]["cantidad"] == 2

    def test_agregar_no_duplica_entradas(self, cliente):
        cliente.post("/carrito/1")
        cliente.post("/carrito/1")
        data = cliente.get("/carrito").get_json()
        assert len(data["carrito"]) == 1

    def test_agregar_varios_productos_distintos(self, cliente):
        cliente.post("/carrito/1")
        cliente.post("/carrito/2")
        cliente.post("/carrito/3")
        data = cliente.get("/carrito").get_json()
        assert len(data["carrito"]) == 3

    def test_respuesta_incluye_mensaje(self, cliente):
        data = cliente.post("/carrito/1").get_json()
        assert "mensaje" in data


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /carrito/<id>
# ─────────────────────────────────────────────────────────────────────────────

class TestQuitarProducto:
    def test_quitar_producto_no_en_carrito_retorna_404(self, cliente):
        res = cliente.delete("/carrito/1")
        assert res.status_code == 404

    def test_quitar_decrementa_cantidad(self, cliente):
        cliente.post("/carrito/1")
        cliente.post("/carrito/1")
        cliente.delete("/carrito/1")
        data = cliente.get("/carrito").get_json()
        assert data["carrito"][0]["cantidad"] == 1

    def test_quitar_ultima_unidad_elimina_del_carrito(self, cliente):
        cliente.post("/carrito/1")
        cliente.delete("/carrito/1")
        data = cliente.get("/carrito").get_json()
        assert data["carrito"] == []

    def test_quitar_respuesta_incluye_mensaje(self, cliente):
        cliente.post("/carrito/1")
        data = cliente.delete("/carrito/1").get_json()
        assert "mensaje" in data


# ─────────────────────────────────────────────────────────────────────────────
# PERSISTENCIA (verifica que los datos sobreviven entre requests)
# ─────────────────────────────────────────────────────────────────────────────

class TestPersistencia:
    def test_cantidad_persiste_entre_requests(self, cliente):
        """Agregar en un request y leer en otro debe dar el mismo resultado."""
        cliente.post("/carrito/1")
        cliente.post("/carrito/1")
        cliente.post("/carrito/1")

        # Request independiente
        data = cliente.get("/carrito").get_json()
        item = next(i for i in data["carrito"] if i["id"] == 1)
        assert item["cantidad"] == 3

    def test_total_persiste_entre_requests(self, cliente):
        cliente.post("/carrito/1")
        cliente.post("/carrito/2")

        total_antes = cliente.get("/carrito/total").get_json()["total"]
        total_despues = cliente.get("/carrito/total").get_json()["total"]
        assert total_antes == total_despues