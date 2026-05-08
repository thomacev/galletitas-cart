import pytest
import main


@pytest.fixture(autouse=True)
def reset_estado():
    main.carrito.clear()
    yield
    main.carrito.clear()


@pytest.fixture
def cliente():
    main.app.config["TESTING"] = True
    with main.app.test_client() as c:
        yield c


# GET /productos
class TestListarProductos:
    def test_retorna_200(self, cliente):
        res = cliente.get("/productos")
        assert res.status_code == 200

    def test_productos_tienen_precio_positivo(self, cliente):
        data = cliente.get("/productos").get_json()
        for p in data["productos"]:
            assert p["precio"] > 0


# GET /carrito
class TestVerCarrito:
    def test_carrito_vacio_al_inicio(self, cliente):
        data = cliente.get("/carrito").get_json()
        assert data["carrito"] == []

    def test_retorna_200(self, cliente):
        res = cliente.get("/carrito")
        assert res.status_code == 200

    def test_item_tiene_subtotal(self, cliente):
        cliente.post("/carrito/1")
        cliente.post("/carrito/1")
        data = cliente.get("/carrito").get_json()
        item = data["carrito"][0]
        # Verificamos usando las nuevas claves en español
        assert item["subtotal"] == item["precio"] * item["cantidad"]

# GET /carrito/total
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


# POST /carrito/<id>
class TestAgregarProducto:
    def test_agregar_producto_existente(self, cliente):
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

# DELETE /carrito/<id>
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