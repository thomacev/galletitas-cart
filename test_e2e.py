"""
Tests E2E con Selenium — Chromium instalado via snap en Ubuntu.

Requisitos:
    snap install chromium          (ya instalado)
    pip install selenium           (NO necesita webdriver-manager)

Levantar antes de correr:
    - Backend:   flask run
    - Frontend:  python -m http.server 5500  (en la carpeta del index.html)

Correr:
    pytest test_e2e.py -v
"""
import pytest
from backend.database import conectar_db
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


FRONTEND_URL = "http://127.0.0.1:5500/frontend/index.html"
WAIT_TIMEOUT  = 8

# FIXTURES

def _limpiar_carrito():
    con = conectar_db()
    con.execute("DELETE FROM carrito")
    con.commit()
    con.close()


@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(4)

    yield driver

    driver.quit()


@pytest.fixture(autouse=True)
def reset_y_recargar(driver):
    """Limpia el carrito en DB y recarga la página antes de cada test."""
    _limpiar_carrito()
    driver.get(FRONTEND_URL)
    yield
    _limpiar_carrito()


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def esperar(driver, by, selector, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, selector))
    )


def click_agregar(driver, producto_id):
    btn = esperar(driver, By.ID, f"btn-agregar-{producto_id}")
    btn.click()
    esperar(driver, By.CSS_SELECTOR, "#toast.show")
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "#toast.show"))
    )


def click_sumar(driver, producto_id):
    btn = esperar(driver, By.ID, f"btn-sumar-{producto_id}")
    btn.click()
    esperar(driver, By.CSS_SELECTOR, "#toast.show")
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "#toast.show"))
    )


def click_quitar(driver, producto_id):
    btn = esperar(driver, By.ID, f"btn-quitar-{producto_id}")
    btn.click()
    esperar(driver, By.CSS_SELECTOR, "#toast.show")
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "#toast.show"))
    )


def leer_cantidad(driver, producto_id):
    el = esperar(driver, By.ID, f"qty-{producto_id}")
    return int(el.text)


def leer_total(driver):
    return esperar(driver, By.ID, "total-precio").text


# ─────────────────────────────────────────────────────────────────────────────
# TESTS: CARGA INICIAL
# ─────────────────────────────────────────────────────────────────────────────

class TestCargaInicial:
    def test_catalogo_muestra_productos(self, driver):
        esperar(driver, By.CSS_SELECTOR, ".producto-card")
        cards = driver.find_elements(By.CSS_SELECTOR, ".producto-card")
        assert len(cards) > 0

    def test_carrito_vacio_al_inicio(self, driver):
        esperar(driver, By.ID, "carrito-vacio")

    def test_boton_agregar_visible_en_cada_producto(self, driver):
        esperar(driver, By.CSS_SELECTOR, ".btn-agregar")
        botones = driver.find_elements(By.CSS_SELECTOR, ".btn-agregar")
        assert len(botones) > 0
        for btn in botones:
            assert btn.is_displayed()


# ─────────────────────────────────────────────────────────────────────────────
# TESTS: AGREGAR AL CARRITO
# ─────────────────────────────────────────────────────────────────────────────

class TestAgregarAlCarrito:
    def test_agregar_producto_aparece_en_carrito(self, driver):
        click_agregar(driver, 1)
        esperar(driver, By.ID, "carrito-item-1")

    def test_agregar_producto_cantidad_es_uno(self, driver):
        click_agregar(driver, 1)
        assert leer_cantidad(driver, 1) == 1

    def test_agregar_dos_veces_incrementa_cantidad(self, driver):
        click_agregar(driver, 1)
        click_sumar(driver, 1)
        assert leer_cantidad(driver, 1) == 2

    def test_agregar_no_crea_filas_duplicadas(self, driver):
        click_agregar(driver, 1)
        click_sumar(driver, 1)
        items = driver.find_elements(By.ID, "carrito-item-1")
        assert len(items) == 1

    def test_agregar_muestra_total(self, driver):
        click_agregar(driver, 1)
        esperar(driver, By.ID, "total-precio")
        total = driver.find_element(By.ID, "total-precio").text
        assert total != "" and total != "$0,00"

    def test_agregar_varios_productos_distintos(self, driver):
        click_agregar(driver, 1)
        click_agregar(driver, 2)
        esperar(driver, By.ID, "carrito-item-1")
        esperar(driver, By.ID, "carrito-item-2")
        items = driver.find_elements(By.CSS_SELECTOR, ".carrito-item")
        assert len(items) == 2


# ─────────────────────────────────────────────────────────────────────────────
# TESTS: QUITAR DEL CARRITO
# ─────────────────────────────────────────────────────────────────────────────

class TestQuitarDelCarrito:
    def test_quitar_decrementa_cantidad(self, driver):
        click_agregar(driver, 1)
        click_sumar(driver, 1)
        assert leer_cantidad(driver, 1) == 2
        click_quitar(driver, 1)
        assert leer_cantidad(driver, 1) == 1

    def test_quitar_ultima_unidad_elimina_item(self, driver):
        click_agregar(driver, 1)
        click_quitar(driver, 1)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.ID, "carrito-item-1"))
        )

    def test_quitar_ultima_unidad_muestra_carrito_vacio(self, driver):
        click_agregar(driver, 1)
        click_quitar(driver, 1)
        esperar(driver, By.ID, "carrito-vacio")


# ─────────────────────────────────────────────────────────────────────────────
# TESTS: FLUJO DE COMPRA COMPLETO
# ─────────────────────────────────────────────────────────────────────────────

class TestFlujoCompleto:
    def test_flujo_agregar_ajustar_y_quitar(self, driver):
        """
        Flujo completo:
        1. Agregar productos 1 y 2
        2. Sumar una unidad más de producto 1  →  cantidad = 2
        3. Quitar una unidad de producto 1     →  cantidad = 1
        4. Quitar completamente producto 2
        5. Verificar: solo producto 1 con cantidad 1
        """
        click_agregar(driver, 1)
        click_agregar(driver, 2)

        click_sumar(driver, 1)
        assert leer_cantidad(driver, 1) == 2

        click_quitar(driver, 1)
        assert leer_cantidad(driver, 1) == 1

        click_quitar(driver, 2)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.invisibility_of_element_located((By.ID, "carrito-item-2"))
        )

        items = driver.find_elements(By.CSS_SELECTOR, ".carrito-item")
        assert len(items) == 1
        assert leer_cantidad(driver, 1) == 1


# ─────────────────────────────────────────────────────────────────────────────
# TESTS: PERSISTENCIA
# ─────────────────────────────────────────────────────────────────────────────

class TestPersistencia:
    def test_carrito_persiste_tras_recargar_pagina(self, driver):
        """
        Agrega un producto, recarga la página sin limpiar la DB,
        y verifica que el item sigue visible con la cantidad correcta.
        Confirma que el estado viene de SQLite y no de memoria JS.
        """
        click_agregar(driver, 1)
        click_sumar(driver, 1)

        driver.refresh()

        esperar(driver, By.ID, "carrito-item-1")
        assert leer_cantidad(driver, 1) == 2

    def test_total_persiste_tras_recargar_pagina(self, driver):
        click_agregar(driver, 1)
        total_antes = leer_total(driver)

        driver.refresh()

        total_despues = leer_total(driver)
        assert total_antes == total_despues