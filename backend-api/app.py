from flask import Flask, request, redirect, url_for, session, jsonify  # 💚 Modificado: agregamos jsonify, sacamos render_template
import pymysql  # 💚 Modificado: usamos pymysql en vez de sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import os

# 💚 Modificado: Importamos desde el nuevo db.py dinámico compatible con MySQL
from models.db import get_db, init_db
from auth_utils import es_admin, obtener_pregunta_seguridad, validar_respuesta_y_cambiar_clave

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_cambiame")

# ──────────────────────────────────────────────
# NOTIFICACIONES (EMAIL + WHATSAPP) - Mantenemos tus funciones intactas
# ──────────────────────────────────────────────

def enviar_email(destinatario, asunto, mensaje):
    remitente = "tuemail@gmail.com"
    password = "tu_password_app"  
    msg = MIMEText(mensaje, "plain", "utf-8")
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(remitente, password)
            server.sendmail(remitente, [destinatario], msg.as_string())
    except Exception as e:
        print(f"Error enviando email: {e}")

def enviar_whatsapp(destinatario, mensaje):
    account_sid = "TU_ACCOUNT_SID"
    auth_token = "TU_AUTH_TOKEN"
    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            from_="whatsapp:+14155238886",
            body=mensaje,
            to=f"whatsapp:{destinatario}"
        )
    except Exception as e:
        print(f"Error enviando WhatsApp: {e}")

# ──────────────────────────────────────────────
# HELPERS DEL CARRITO (Lógica con MySQL)
# ──────────────────────────────────────────────

def get_carrito():
    return session.get("carrito", {})

def guardar_carrito(carrito):
    session["carrito"] = carrito

def total_carrito():
    carrito = get_carrito()
    if not carrito:
        return 0
    conn = get_db()
    cursor = conn.cursor() # 💚 Modificado: En PyMySQL se necesita declarar el cursor para ejecutar
    total = 0
    for pid, cantidad in carrito.items():
        # 💚 Modificado: Cambiamos "?" por "%s" (Sintaxis estándar de MySQL para consultas parametrizadas)
        cursor.execute("SELECT precio FROM productos WHERE id = %s", (int(pid),))
        row = cursor.fetchone()
        if row:
            total += row["precio"] * cantidad
    conn.close()
    return total

# ──────────────────────────────────────────────
# API ENDPOINTS (RUTAS REFACTORIZADAS A JSON)
# ──────────────────────────────────────────────

# 1. Catálogo / Home
@app.route("/api/productos")  # 💚 Modificado: ahora es un endpoint de la API
def api_productos():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE stock > 0")
    productos = cursor.fetchall()
    conn.close()
    return jsonify(productos)  # 💚 Modificado: retornamos los productos en formato JSON directo

# 2. Detalle de Producto
@app.route("/api/productos/<int:id>")
def api_producto_detalle(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,)) # 💚 Modificado: usando "%s"
    p = cursor.fetchone()
    conn.close()
    if not p:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify(p)

# 3. Datos del Carrito actual
@app.route("/api/carrito")
def api_carrito():
    carrito = get_carrito()
    items = []
    conn = get_db()
    cursor = conn.cursor()
    for pid, cantidad in carrito.items():
        cursor.execute("SELECT * FROM productos WHERE id = %s", (int(pid),))
        p = cursor.fetchone()
        if p:
            items.append({
                "id": p["id"],
                "nombre": p["nombre"],
                "precio": p["precio"],
                "cantidad": cantidad,
                "subtotal": p["precio"] * cantidad,
            })
    conn.close()
    return jsonify({"items": items, "total": total_carrito()})

# 4. Agregar ítem al Carrito
@app.route("/api/carrito/agregar/<int:id>", methods=["POST"])
def api_agregar_al_carrito(id):
    carrito = get_carrito()
    cantidad = int(request.json.get("cantidad", 1)) # 💚 Modificado: leemos JSON en vez de un form HTML tradicional
    clave = str(id)
    carrito[clave] = carrito.get(clave, 0) + cantidad
    guardar_carrito(carrito)
    return jsonify({"mensaje": "Producto agregado", "carrito": carrito})

# 5. Quitar ítem del Carrito
@app.route("/api/carrito/quitar/<int:id>", methods=["DELETE"]) # 💚 Modificado: usamos verbo DELETE apropiado para APIs
def api_quitar_del_carrito(id):
    carrito = get_carrito()
    carrito.pop(str(id), None)
    guardar_carrito(carrito)
    return jsonify({"mensaje": "Producto removido", "carrito": carrito})

# 6. Vaciar Carrito
@app.route("/api/carrito/vaciar", methods=["POST"])
def api_vaciar_carrito():
    session.pop("carrito", None)
    return jsonify({"mensaje": "Carrito vaciado con éxito"})

# 7. Procesar la Compra (Checkout)
@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    carrito = get_carrito()
    if not carrito:
        return jsonify({"error": "El carrito está vacío"}), 400

    # 💚 Modificado: Obtenemos los datos desde el request JSON enviado por el frontend
    data = request.get_json() or {}
    nombre = data.get("nombre", "").strip()
    email = data.get("email", "").strip()

    if not nombre or not email:
        return jsonify({"error": "Completá todos los campos."}), 400

    total = total_carrito()
    conn = get_db()
    cursor = conn.cursor()
    
    # 💚 Modificado: Ajustamos a la sintaxis parametrizada con %s de PyMySQL
    cursor.execute(
        "INSERT INTO pedidos (nombre_cliente, email, total) VALUES (%s, %s, %s)",
        (nombre, email, total)
    )
    pedido_id = cursor.lastrowid

    for pid, cantidad in carrito.items():
        cursor.execute("SELECT precio FROM productos WHERE id = %s", (int(pid),))
        p = cursor.fetchone()
        if p:
            cursor.execute(
                "INSERT INTO pedido_items (pedido_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
                (pedido_id, int(pid), cantidad, p["precio"])
            )
            cursor.execute(
                "UPDATE productos SET stock = stock - %s WHERE id = %s",
                (cantidad, int(pid))
            )

    conn.commit()
    conn.close()
    session.pop("carrito", None)

    # 💚 Opcional: enviamos notificación si lo tenés habilitado
    # mensaje = f"Hola {nombre}, gracias por tu compra.\nTu pedido #{pedido_id} fue confirmado por ${total:.2f}."
    # enviar_email(email, "Confirmación de compra - MiTienda", mensaje)
    
    return jsonify({"confirmado": True, "pedido_id": pedido_id, "nombre": nombre, "total": total})

# 8. Registro de Usuarios
@app.route("/api/registro", methods=["POST"])
def api_registro():
    data = request.get_json() or {}
    nombre = data.get("nombre")
    email = data.get("email")
    password = generate_password_hash(data.get("password"))
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
                     (nombre, email, password))
        conn.commit()
    except pymysql.err.IntegrityError: # 💚 Modificado: Capturamos la excepción de MySQL
        return jsonify({"error": "El email ya está registrado."}), 400
    finally:
        conn.close()
    return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201

# 9. Login de Usuarios
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user["password"], password):
        session["usuario"] = user["nombre"]
        return jsonify({"mensaje": f"Bienvenido {user['nombre']}", "usuario": user["nombre"]})
    else:
        return jsonify({"error": "Email o contraseña incorrectos."}), 401


# 10. Admin Dashboard
@app.route("/api/admin/dashboard")
def api_admin_dashboard():
    if not es_admin(session.get("user_id")):
        return jsonify({"error": "Acceso denegado. No sos admin, gato."}), 403
        
    return jsonify({"mensaje": "Acceso permitido al panel de administración"})

# ──────────────────────────────────────────────
# BLOQUE DE ARRANQUE
# ──────────────────────────────────────────────

init_db() 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) # 💚 Agregamos host="0.0.0.0" para que escuche fuera del contenedor