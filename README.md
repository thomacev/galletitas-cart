# Galletitas Cart

API REST para gestionar un carrito de compras de galletitas.

## Instalación

```bash
git clone https://github.com/thomacev/galletitas-cart.git
cd galletitas-cart
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Uso

```bash
python main.py
```

La documentación interactiva (Swagger) queda disponible en `http://localhost:5000/apidocs`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/productos` | Lista los productos disponibles |
| GET | `/carrito` | Muestra el carrito actual |
| GET | `/carrito/total` | Calcula el total a pagar |
| POST | `/carrito/<id>` | Agrega una unidad al carrito |
| DELETE | `/carrito/<id>` | Quita una unidad del carrito |

## Tests

```bash
pytest test_main.py -v
python -m pytest -vv --cov=main --cov-report=term-missing
```