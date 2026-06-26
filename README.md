# Galletitas Cart

E-commerce de galletitas con carrito de compras. Proyecto universitario fullstack con backend en Flask, frontend en HTML/CSS/JS vanilla y pruebas E2E con Selenium.

---

## Arquitectura

El proyecto sigue una arquitectura cliente-servidor clásica de tres capas:

```
frontend (HTML/CSS/JS)
        │  fetch() — JSON
        ▼
backend (Flask REST API)
        │  SQL
        ▼
base de datos (SQLite)
```

**Backend:** API REST construida con Flask y organizada en un Blueprint (`carrito_blueprint`). Cada endpoint delega la lógica de negocio directamente en consultas SQL, manteniendo el código simple y sin ORM. La base de datos se inicializa con un script separado (`database.py`) que maneja la conexión y el schema.

**Frontend:** SPA (Single Page Application) en HTML/CSS/JS vanilla sin frameworks. Consume la API mediante `fetch()` y actualiza el DOM con un sistema de patch: en lugar de re-renderizar el carrito completo ante cada acción, detecta qué cambió (items nuevos, eliminados, o con cantidad modificada) y actualiza solo esos nodos. Esto evita el parpadeo visual y mejora la experiencia de uso.

**Base de datos:** SQLite con dos tablas:
- `productos` — catálogo fijo con id, nombre y precio
- `carrito` — items activos con producto_id y cantidad; usa `INNER JOIN` para calcular subtotales y totales directamente en SQL

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12, Flask, Flasgger (Swagger) |
| Base de datos | SQLite (módulo `sqlite3` de la stdlib) |
| Frontend | HTML5, CSS3, JavaScript (ES2020+) |
| Tests de API | pytest, Flask test client |
| Tests E2E | Selenium 4, Chromium (snap) |

---

## Instalación y uso

```bash
git clone https://github.com/thomacev/galletitas-cart.git
cd galletitas-cart
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Abrir `index.html` con Live Server (VS Code) o con:

```bash
python -m http.server 5500
```

La documentación interactiva de la API queda disponible en `http://localhost:5000/apidocs`.

### Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/productos` | Lista los productos disponibles |
| GET | `/carrito` | Muestra el carrito actual |
| GET | `/carrito/total` | Calcula el total a pagar |
| POST | `/carrito/<id>` | Agrega una unidad al carrito |
| DELETE | `/carrito/<id>` | Quita una unidad del carrito |

---

## Tests

### Tests de API

Prueban los endpoints directamente contra Flask sin levantar un servidor real.

```bash
pytest test_main.py -v
pytest test_main.py -v --cov=main --cov-report=term-missing
```

### Tests E2E (Selenium)

Requieren tener el backend y el frontend corriendo antes de ejecutar.

```bash
# En una terminal: levantar backend
python -m backend.main

# En otra terminal: levantar frontend
python -m http.server 5500

# Correr los tests E2E
pytest test_e2e.py -v
```

---

## Dificultades encontradas

**Chromium instalado via snap no levantaba con Selenium**

Al intentar correr los tests E2E, Selenium fallaba con `session not created: Chrome instance exited`. El problema tenía dos causas: primero, `webdriver-manager` descargaba su propio chromedriver que no era compatible con el binario snap; segundo, el sandbox de snap requería flags adicionales que la configuración estándar no incluía. Se resolvió apuntando directamente al chromedriver empaquetado dentro del snap (`/snap/bin/chromium.chromedriver`), usando `options.binary_location` para indicar el binario correcto, y agregando los flags `--headless=new`, `--no-sandbox`, `--disable-dev-shm-usage` y `--disable-gpu`.

**Tests de API incompatibles con la migración a SQLite**

Los tests originales reseteaban el estado del carrito llamando a `main.carrito.clear()`, que borraba el diccionario en memoria que usaba la versión sin base de datos. Al migrar a SQLite, ese mecanismo dejó de funcionar. Se reemplazó el fixture `reset_estado` por uno que ejecuta `DELETE FROM carrito` directamente sobre la base de datos antes y después de cada test, manteniendo el aislamiento entre casos sin cambiar la lógica de los tests en sí.