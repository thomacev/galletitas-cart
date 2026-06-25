import sqlite3
DATABASE = "mydatabase.db"

CATALOGO_INICIAL = [
    ("Don Satur", 1200),
    ("Surtidas Bagley", 3200),
    ("Oreo", 2200),
    ("Chocolinas", 2000),
    ("Marmoladas Fantoche", 1700),
    ("Merengadas", 2200),
    ("Pitusas", 1200),
    ("9 de oro", 1500),
    ("Surtidas diversion", 2800),
    ("Obleas", 900),
    ("Pepitos",2000),
    ("Cañoncitos",4000)
]

def conectar_db():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion

def inicializar_db():
    conexion = conectar_db()
    db = conexion.cursor()
    db.execute("PRAGMA foreign_keys = ON;")

    db.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio INTEGER NOT NULL
            )
        """)
    
    db.execute("""
            CREATE TABLE IF NOT EXISTS carrito (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
            )
        """)
    
    conexion.commit()
    """
    para cargar el catalogo de productos en la db
    db.execute("SELECT COUNT(*) as total FROM productos")
    if db.fetchone()["total"] == 0:
        db.executemany(
            "INSERT INTO productos (nombre, precio) VALUES (?, ?)", 
            CATALOGO_INICIAL
        )
        conexion.commit()
        print("-> Catálogo de galletitas cargado con éxito en la base de datos.")
    """

    conexion.close()


