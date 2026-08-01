import os

import pymysql
# Kubernetes nos va a inyectar estas variables por red
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "peronperon")
DB_NAME = os.getenv("DB_NAME", "tienda_db")


def get_db():
    # Nos conectamos a MySQL usando las variables de arriba
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        # DictCursor hace exactamente lo mismo que row_factory (mantiene tus queries intactas)
        cursorclass=pymysql.cursors.DictCursor 
    )
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Tabla productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            imagen VARCHAR(255),
            stock INT DEFAULT 0
        )
    """)

    # Tabla pedidos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            nombre_cliente VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            total REAL NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabla pedido_items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedido_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pedido_id INT,
            producto_id INT,
            cantidad INT,
            precio_unitario REAL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    # Tabla usuarios (NUEVA)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre  VARCHAR(255) NOT NULL,
            email  VARCHAR(255) NOT NULL,
            password  VARCHAR(255) NOT NULL
        )
    """)

    conn.commit()
    conn.close()
