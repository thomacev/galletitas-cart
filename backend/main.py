from flask import Flask
from flask_cors import CORS
from backend.routes.carrito import carrito_blueprint
from backend.database import inicializar_db
from flasgger import Swagger


def create_app():
    app = Flask(__name__)
    CORS(app)
    swagger = Swagger(app)

    app.register_blueprint(carrito_blueprint)

    with app.app_context():
        inicializar_db()

    return app

if __name__ == '__main__':
    app = create_app()
    port = 5000
    app.run(host='0.0.0.0', port=port, debug=True)