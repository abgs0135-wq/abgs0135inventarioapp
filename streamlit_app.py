import streamlit as st
import pandas as pd
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets

# =========================
# Configuración básica
# =========================
st.set_page_config(page_title="Parque de zapadores IIScc", layout="wide")

DATA_DIR = "data"
INV_FILE = os.path.join(DATA_DIR, "inventario.csv")
LOG_FILE = os.path.join(DATA_DIR, "movimientos.csv")
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
SESSION_FILE = os.path.join(DATA_DIR, "session.csv")

EMAIL_ADDRESS = st.secrets.get("EMAIL_ADDRESS", "placeholder@example.com")
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "placeholderpassword")
BASE_URL = st.secrets.get("BASE_URL", "https://example.com")

DEFAULT_USERS = [
    {"usuario": "teniente", "password": "jefe1", "nombre": "Teniente", "correo": ""},
    {"usuario": "parquista", "password": "encargado1", "nombre": "Parquista", "correo": ""},
    # si quieres añadir "sargento" desde el inicio, puedes descomentar esto:
    {"usuario": "sargento", "password": "mando1", "nombre": "Sargento", "correo": ""},
]

# =========================
# INVENTARIO BASE AGRUPADO POR CATEGORÍA
# =========================
# Añade aquí los lotes/mochilas/ cajas con su material inicial.
# IMPORTANTE: cuando actualices esto y quieras regenerar el CSV limpio,
# borra data/inventario.csv en GitHub y reinicia la app.
INVENTARIO_BASE = [
       # LOTE 1 - CMAS
    {"categoria": "LOTE 1 - CMAS", "material": "Señales de pasillo", "cantidad_total": 18, "en_parque": 18, "fuera_parque": 0, "operativos": 18, "unidad": "uds"},
    {"categoria": "LOTE 1 - CMAS", "material": "Señales minas", "cantidad_total": 35, "en_parque": 35, "fuera_parque": 0, "operativos": 35, "unidad": "uds"},
    {"categoria": "LOTE 1 - CMAS", "material": "Puntos base", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 1 - CMAS", "material": "Perrillo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 1 - CMAS", "material": "Cuerda 6 m", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 1 - CMAS", "material": "Agujas de marcar", "cantidad_total": 8, "en_parque": 8, "fuera_parque": 0, "operativos": 8, "unidad": "uds"},
    {"categoria": "LOTE 1 - CMAS", "material": "Cartera topográfica", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 1 - CMAS", "material": "Señal caída granadas", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 1 - CMAS", "material": "Conos", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
        # LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Caja arrastraminas", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Garfio arrastraminas", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Bastones de sondeo", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Banderolas amarillas", "cantidad_total": 6, "en_parque": 6, "fuera_parque": 0, "operativos": 6, "unidad": "uds"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Banderolas rojas", "cantidad_total": 4, "en_parque": 4, "fuera_parque": 0, "operativos": 4, "unidad": "uds"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Redes de sondeo", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Banderola roja", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Banderola verde", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Sombreretes", "cantidad_total": 10, "en_parque": 10, "fuera_parque": 0, "operativos": 10, "unidad": "uds"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Cintas polidiamida", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Cuaderno de campo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Maceta", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Zapapicos", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Garfio levantaminas", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Piqueta larga", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Piqueta corta", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1", "material": "Cuerdas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
        # LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Caja arrastraminas", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Garfio arrastraminas", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Bastones de sondeo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Banderolas amarillas", "cantidad_total": 6, "en_parque": 6, "fuera_parque": 0, "operativos": 6, "unidad": "uds"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Banderolas rojas", "cantidad_total": 4, "en_parque": 4, "fuera_parque": 0, "operativos": 4, "unidad": "uds"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Redes de sondeo", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Sombreretes", "cantidad_total": 10, "en_parque": 10, "fuera_parque": 0, "operativos": 10, "unidad": "uds"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Cintas polidiamida", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Cuaderno de campo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Cuerdas arrastraminas", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Punto base", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Maceta", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Zapapicos", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Agujas de marcar", "cantidad_total": 9, "en_parque": 9, "fuera_parque": 0, "operativos": 9, "unidad": "uds"},
    {"categoria": "LOTE 3 - MOVILIDAD/CONTRAMOVILIDAD 2", "material": "Palas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
        # LOTE 4 - FORTIFICACIÓN 1
    {"categoria": "LOTE 4 - FORTIFICACIÓN 1", "material": "Zapapico", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 4 - FORTIFICACIÓN 1", "material": "Palas", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 4 - FORTIFICACIÓN 1", "material": "Pares de manoplas", "cantidad_total": 4, "en_parque": 4, "fuera_parque": 0, "operativos": 4, "unidad": "pares"},
    {"categoria": "LOTE 4 - FORTIFICACIÓN 1", "material": "Zapapicos ordinarios", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 4 - FORTIFICACIÓN 1", "material": "Hachas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 4 - FORTIFICACIÓN 1", "material": "Almádena", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 4 - FORTIFICACIÓN 1", "material": "Azadas", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
        # LOTE 5 - FORTIFICACIÓN 2
    {"categoria": "LOTE 5 - FORTIFICACIÓN 2", "material": "Zapapico", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 5 - FORTIFICACIÓN 2", "material": "Azada", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 5 - FORTIFICACIÓN 2", "material": "Pares de manoplas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "pares"},
    {"categoria": "LOTE 5 - FORTIFICACIÓN 2", "material": "Zapapicos ordinarios", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 5 - FORTIFICACIÓN 2", "material": "Hachas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 5 - FORTIFICACIÓN 2", "material": "Palas", "cantidad_total": 5, "en_parque": 5, "fuera_parque": 0, "operativos": 5, "unidad": "uds"},
    {"categoria": "LOTE 5 - FORTIFICACIÓN 2", "material": "Cuerdas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    # LOTE 6 - CONSTRUCCIÓN
    {"categoria": "LOTE 6 - CONSTRUCCIÓN", "material": "Corta fríos", "cantidad_total": 7, "en_parque": 7, "fuera_parque": 0, "operativos": 7, "unidad": "uds"},
    {"categoria": "LOTE 6 - CONSTRUCCIÓN", "material": "Mazos de madera", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 6 - CONSTRUCCIÓN", "material": "Tijeras de alambre", "cantidad_total": 8, "en_parque": 8, "fuera_parque": 0, "operativos": 8, "unidad": "uds"},
    {"categoria": "LOTE 6 - CONSTRUCCIÓN", "material": "Cizalla", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 6 - CONSTRUCCIÓN", "material": "Escalera enrollada", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 6 - CONSTRUCCIÓN", "material": "Carpeta de obra", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 6 - CONSTRUCCIÓN", "material": "Espátula", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    # LOTE 7 - CORTE
    {"categoria": "LOTE 7 - CORTE", "material": "Serrucho", "cantidad_total": 10, "en_parque": 10, "fuera_parque": 0, "operativos": 10, "unidad": "uds"},
    {"categoria": "LOTE 7 - CORTE", "material": "Sierra", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    # LOTE 8 - CHECK POINT
    {"categoria": "LOTE 8 - CHECK POINT", "material": "Conos", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 8 - CHECK POINT", "material": "Señales", "cantidad_total": 4, "en_parque": 4, "fuera_parque": 0, "operativos": 4, "unidad": "uds"},
    {"categoria": "LOTE 8 - CHECK POINT", "material": "Espejo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 8 - CHECK POINT", "material": "Piquetas", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 8 - CHECK POINT", "material": "Chalecos reflectantes", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 8 - CHECK POINT", "material": "Cruces de madera", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 8 - CHECK POINT", "material": "Conos pequeños", "cantidad_total": 27, "en_parque": 27, "fuera_parque": 0, "operativos": 27, "unidad": "uds"},
    # LOTE 9 - SIMULACIÓN
    {"categoria": "LOTE 9 - SIMULACIÓN", "material": "Tarjetas rojas", "cantidad_total": 8, "en_parque": 8, "fuera_parque": 0, "operativos": 8, "unidad": "uds"},
    {"categoria": "LOTE 9 - SIMULACIÓN", "material": "Rollo negro", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 9 - SIMULACIÓN", "material": "Spray", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 9 - SIMULACIÓN", "material": "Banderolas verdes", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 9 - SIMULACIÓN", "material": "Cuerda roja", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 9 - SIMULACIÓN", "material": "Cuerda amarilla", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 9 - SIMULACIÓN", "material": "Piquetas cortas", "cantidad_total": 9, "en_parque": 9, "fuera_parque": 0, "operativos": 9, "unidad": "uds"},
    {"categoria": "LOTE 9 - SIMULACIÓN", "material": "Piqueta larga", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 9 - SIMULACIÓN", "material": "Reenvío", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 9 - SIMULACIÓN", "material": "Material simulación variado", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    # LOTE 10 - TRACTEL
    {"categoria": "LOTE 10 - TRACTEL", "material": "Tractel", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 10 - TRACTEL", "material": "Cuerdas", "cantidad_total": 5, "en_parque": 5, "fuera_parque": 0, "operativos": 5, "unidad": "uds"},
    {"categoria": "LOTE 10 - TRACTEL", "material": "Poleas dobles", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 10 - TRACTEL", "material": "Polea individual", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 10 - TRACTEL", "material": "Piquetas", "cantidad_total": 9, "en_parque": 9, "fuera_parque": 0, "operativos": 9, "unidad": "uds"},
    {"categoria": "LOTE 10 - TRACTEL", "material": "Palanca tractel", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 10 - TRACTEL", "material": "Bastones hexagonales", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    # LOTE 11
    {"categoria": "LOTE 11 - SIN ESPECIFICAR", "material": "Pares de botas largas", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "pares"},
    {"categoria": "LOTE 11 - SIN ESPECIFICAR", "material": "Pares de botas cortas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "pares"},
    # LOTE 12
    {"categoria": "LOTE 12 - SIN ESPECIFICAR", "material": "Cubos", "cantidad_total": 4, "en_parque": 4, "fuera_parque": 0, "operativos": 4, "unidad": "uds"},
    {"categoria": "LOTE 12 - SIN ESPECIFICAR", "material": "Espuertas", "cantidad_total": 7, "en_parque": 7, "fuera_parque": 0, "operativos": 7, "unidad": "uds"},
    # LOTE 13 - HOLLMAN
    {"categoria": "LOTE 13 - HOLLMAN", "material": "Martillos largos", "cantidad_total": 12, "en_parque": 12, "fuera_parque": 0, "operativos": 12, "unidad": "uds"},
    {"categoria": "LOTE 13 - HOLLMAN", "material": "Martillos cortos", "cantidad_total": 9, "en_parque": 9, "fuera_parque": 0, "operativos": 9, "unidad": "uds"},
    {"categoria": "LOTE 13 - HOLLMAN", "material": "Palas", "cantidad_total": 5, "en_parque": 5, "fuera_parque": 0, "operativos": 5, "unidad": "uds"},
    {"categoria": "LOTE 13 - HOLLMAN", "material": "Aceite hollman", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    # LOTE 14 - PROTECCIÓN
    {"categoria": "LOTE 14 - PROTECCIÓN", "material": "Chalecos", "cantidad_total": 6, "en_parque": 6, "fuera_parque": 0, "operativos": 6, "unidad": "uds"},
    {"categoria": "LOTE 14 - PROTECCIÓN", "material": "Cascos blancos", "cantidad_total": 14, "en_parque": 14, "fuera_parque": 0, "operativos": 14, "unidad": "uds"},
    # LOTE 15 - RETALES
    {"categoria": "LOTE 15 - RETALES", "material": "Cabeza zapapico ordinario", "cantidad_total": 18, "en_parque": 18, "fuera_parque": 0, "operativos": 18, "unidad": "uds"},
    {"categoria": "LOTE 15 - RETALES", "material": "Cabeza de pala", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 15 - RETALES", "material": "Cabeza de zapapico", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 15 - RETALES", "material": "Cabeza de rastrillo", "cantidad_total": 6, "en_parque": 6, "fuera_parque": 0, "operativos": 6, "unidad": "uds"},
    {"categoria": "LOTE 15 - RETALES", "material": "Cabeza de guadaña", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 15 - RETALES", "material": "Palo de pisón", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 15 - RETALES", "material": "Azuela sin implemento", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    # LOTE 16
    {"categoria": "LOTE 16 - SIN ESPECIFICAR", "material": "Saco de grapas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 16 - SIN ESPECIFICAR", "material": "Cuerdas", "cantidad_total": 7, "en_parque": 7, "fuera_parque": 0, "operativos": 7, "unidad": "uds"},
    {"categoria": "LOTE 16 - SIN ESPECIFICAR", "material": "Saco de clavos", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 16 - SIN ESPECIFICAR", "material": "Pack conos", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "packs"},
    # LOTE 17
    {"categoria": "LOTE 17 - SIN ESPECIFICAR", "material": "Cajas arrastraminas", "cantidad_total": 4, "en_parque": 4, "fuera_parque": 0, "operativos": 4, "unidad": "uds"},
    {"categoria": "LOTE 17 - SIN ESPECIFICAR", "material": "Puntos base", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 17 - SIN ESPECIFICAR", "material": "Punto intermedio", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 17 - SIN ESPECIFICAR", "material": "Cintas polidiamida", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "LOTE 17 - SIN ESPECIFICAR", "material": "Cuerdas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 17 - SIN ESPECIFICAR", "material": "Piquetas de reenvío", "cantidad_total": 4, "en_parque": 4, "fuera_parque": 0, "operativos": 4, "unidad": "uds"},
    {"categoria": "LOTE 17 - SIN ESPECIFICAR", "material": "Saco clavos alambrada rápida", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "LOTE 17 - SIN ESPECIFICAR", "material": "Saco clavos", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    # LOTE 18
    {"categoria": "LOTE 18 - SIN ESPECIFICAR", "material": "Pala", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 18 - SIN ESPECIFICAR", "material": "Rastrillo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "LOTE 18 - SIN ESPECIFICAR", "material": "Marrazos", "cantidad_total": 7, "en_parque": 7, "fuera_parque": 0, "operativos": 7, "unidad": "uds"},
    {"categoria": "LOTE 18 - SIN ESPECIFICAR", "material": "Ahoyador", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "LOTE 18 - SIN ESPECIFICAR", "material": "Hacha", "cantidad_total": 5, "en_parque": 5, "fuera_parque": 0, "operativos": 5, "unidad": "uds"},
    {"categoria": "LOTE 18 - SIN ESPECIFICAR", "material": "Serrucho", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    # LOTE 19
    {"categoria": "LOTE 19 - SIN ESPECIFICAR", "material": "Simulación pértigas", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "LOTE 19 - SIN ESPECIFICAR", "material": "Palos red mimética", "cantidad_total": 10, "en_parque": 10, "fuera_parque": 0, "operativos": 10, "unidad": "uds"},
    # MINAS
    {"categoria": "MINAS", "material": "CC", "cantidad_total": 200, "en_parque": 200, "fuera_parque": 0, "operativos": 200, "unidad": "uds"},
    {"categoria": "MINAS", "material": "CP", "cantidad_total": 120, "en_parque": 120, "fuera_parque": 0, "operativos": 120, "unidad": "uds"},
    # MANGUERA LIGERA
    {"categoria": "MANGUERA LIGERA", "material": "Mangueras ligeras", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    # MOCHILA BLAEX - COMBATE EN POBLACIÓN 1
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Piqueta", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Pala jardinero", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Rastrillo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Conos", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Sprays amarillos", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Pinzas", "cantidad_total": 4, "en_parque": 4, "fuera_parque": 0, "operativos": 4, "unidad": "uds"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Garfio", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Garfio levantaminas", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Cuerda", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Tarjeta señalización", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Machota", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Garret", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Sargentos", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Caja arrastraminas", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN 1", "material": "Cúter", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    # MOCHILA BLAEX - REMOCIÓN
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Rollo cuerda", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Cuerdas pequeñas", "cantidad_total": 3, "en_parque": 3, "fuera_parque": 0, "operativos": 3, "unidad": "uds"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Sargentos", "cantidad_total": 4, "en_parque": 4, "fuera_parque": 0, "operativos": 4, "unidad": "uds"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Garfio metálico", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Pinzas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Cinta coca cola", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Martillos", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Espejo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Prismáticos", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Spray", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Linterna", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Paquete bridas", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Cepillo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Rastrillo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - REMOCIÓN", "material": "Cúter", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    # MOCHILA BLAEX - COMBATE EN POBLACIÓN
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Pala jardinero", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Rastrillo", "cantidad_total": 1, "en_parque": 1, "fuera_parque": 0, "operativos": 1, "unidad": "ud"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Conos", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Spray amarillo", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Pinzas", "cantidad_total": 2, "en_parque": 2, "fuera_parque": 0, "operativos": 2, "unidad": "uds"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Garfio", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Garfio levantaminas", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Cuerda", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Tarjeta señalización", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Riñonera cosas varias", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - COMBATE EN POBLACIÓN", "material": "Cúter", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    # MOCHILA BLAEX - LIMPIEZA DE RUTA
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Martillo", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Conos azules BP", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Conos rojos/amarillos (caja)", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Primáticos", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Rastrillo", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Pala jardinero", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Brocha", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Spray verde/amarillo/rojo", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Carrete", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Garfio", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Cinta coca cola", "cantidad_total": 0, "en_parque": 0, "fuera_parque": 0, "operativos": 0, "unidad": "-"},
    {"categoria": "MOCHILA BLAEX - LIMPIEZA DE RUTA", "material": "Sargentos", "cantidad_total": 4, "en_parque": 4, "fuera_parque": 0, "operativos": 4, "unidad": "uds"},

]

INV_COLS = ["categoria", "material", "cantidad_total", "en_parque", "fuera_parque", "operativos", "unidad"]
LOG_COLS = ["usuario", "categoria", "material", "cantidad", "accion", "hora", "observacion"]
USER_COLS = ["usuario", "password", "nombre", "correo"]

# =========================
# Funciones de datos
# =========================
def init_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    # inventario.csv
    if not os.path.exists(INV_FILE):
        pd.DataFrame(INVENTARIO_BASE, columns=INV_COLS).to_csv(INV_FILE, index=False)
    else:
        # si ya existe pero le faltan columnas nuevas, podríamos parchear aquí si hiciera falta
        df_inv = pd.read_csv(INV_FILE)
        faltan_cols = [c for c in INV_COLS if c not in df_inv.columns]
        if faltan_cols:
            # caso extremo: si el inventario viejo no tiene formato nuevo, lo reescribimos
            pd.DataFrame(INVENTARIO_BASE, columns=INV_COLS).to_csv(INV_FILE, index=False)

    # movimientos.csv
    if not os.path.exists(LOG_FILE):
        pd.DataFrame(columns=LOG_COLS).to_csv(LOG_FILE, index=False)

    # users.csv
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(DEFAULT_USERS, columns=USER_COLS).to_csv(USERS_FILE, index=False)
    else:
        users_df = pd.read_csv(USERS_FILE)
        # asegurar columna correo
        if "correo" not in users_df.columns:
            users_df["correo"] = ""
        users_df = users_df[USER_COLS]
        users_df.to_csv(USERS_FILE, index=False)

    # session.csv
    if not os.path.exists(SESSION_FILE):
        pd.DataFrame(columns=["usuario", "token"]).to_csv(SESSION_FILE, index=False)

def load_inventory():
    return pd.read_csv(INV_FILE)

def save_inventory(df):
    df.to_csv(INV_FILE, index=False)

def load_log():
    return pd.read_csv(LOG_FILE)

def save_log(df):
    df.to_csv(LOG_FILE, index=False)

def load_users():
    return pd.read_csv(USERS_FILE)

def save_users(df):
    df.to_csv(USERS_FILE, index=False)

def load_session():
    if os.path.exists(SESSION_FILE):
        return pd.read_csv(SESSION_FILE)
    return pd.DataFrame(columns=["usuario", "token"])

def save_session(usuario, token):
    df = pd.DataFrame([[usuario, token]], columns=["usuario", "token"])
    df.to_csv(SESSION_FILE, index=False)

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

init_data()

# =========================
# Envío de correos
# =========================
def send_recovery_email(to_email, token):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = "Recuperación de contraseña - Parque de zapadores IIScc"

        reset_link = f"{BASE_URL}?reset={token}"
        body = f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n\n{reset_link}"
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        return True
    except Exception as e:
        st.error(f"Error enviando correo: {e}")
        return False

# =========================
# Estado de sesión
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.name = None

if "reset_tokens" not in st.session_state:
    st.session_state.reset_tokens = {}

# restaurar sesión persistente si existe
if not st.session_state.logged_in:
    sess = load_session()
    if not sess.empty:
        usuario_guardado = sess.loc[0, "usuario"]
        users_df = load_users()
        if usuario_guardado in users_df["usuario"].values:
            st.session_state.logged_in = True
            st.session_state.user = usuario_guardado
            st.session_state.name = users_df.loc[users_df["usuario"] == usuario_guardado, "nombre"].values[0]
            st.session_state.token = sess.loc[0, "token"]

# =========================
# Pantalla de acceso (login/registro/reset)
# =========================
if not st.session_state.logged_in:
    tab_login, tab_register, tab_reset = st.tabs(["🔑 Iniciar sesión", "📝 Registrarse", "🔄 Cambiar contraseña"])

    # ---- Login
    with tab_login:
        st.subheader("Inicia sesión")
        users_df = load_users()
        usuario_in = st.text_input("Usuario")
        password_in = st.text_input("Contraseña", type="password")
        if st.button("Entrar", use_container_width=True):
            coincide = (users_df["usuario"] == usuario_in) & (users_df["password"] == password_in)
            if coincide.any():
                st.session_state.logged_in = True
                st.session_state.user = usuario_in
                st.session_state.name = users_df.loc[users_df["usuario"] == usuario_in, "nombre"].values[0]
                token_nuevo = secrets.token_urlsafe(16)
                st.session_state.token = token_nuevo
                save_session(usuario_in, token_nuevo)
                st.success(f"Bienvenido {st.session_state.name}")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

    # ---- Registro
    with tab_register:
        st.subheader("Registro de nuevo usuario")
        new_user = st.text_input("Nuevo usuario")
        new_pass = st.text_input("Nueva contraseña", type="password")
        new_name = st.text_input("Nombre completo")
        new_email = st.text_input("Correo electrónico")

        if st.button("Registrar", use_container_width=True):
            users_df = load_users()
            if new_user in users_df["usuario"].values:
                st.error("Ese usuario ya existe")
            elif new_email in users_df["correo"].values:
                st.error("Ese correo ya está registrado")
            elif any(x.strip() == "" for x in [new_user, new_pass, new_name, new_email]):
                st.error("Todos los campos son obligatorios")
            else:
                nueva_fila_usuario = pd.DataFrame(
                    [[new_user, new_pass, new_name, new_email]],
                    columns=USER_COLS
                )
                users_df = pd.concat([users_df, nueva_fila_usuario], ignore_index=True)
                save_users(users_df)
                st.success("Usuario registrado con éxito. Ahora puedes iniciar sesión.")

    # ---- Recuperar contraseña
    with tab_reset:
        st.subheader("Recuperar contraseña")
        reset_user = st.text_input("Usuario para recuperar contraseña")
        if st.button("Enviar correo de recuperación"):
            users_df = load_users()
            if reset_user in users_df["usuario"].values:
                correo_dest = users_df.loc[users_df["usuario"] == reset_user, "correo"].values[0]
                if correo_dest.strip() == "":
                    st.error("Ese usuario no tiene correo configurado.")
                else:
                    token_reset = secrets.token_urlsafe(16)
                    st.session_state.reset_tokens[token_reset] = reset_user
                    if send_recovery_email(correo_dest, token_reset):
                        st.success("Se ha enviado un correo con el enlace de recuperación.")
            else:
                st.error("Usuario no encontrado")

    # soporte de ?reset=token
    params = st.query_params
    if "reset" in params:
        token_in_url = params["reset"]
        if token_in_url in st.session_state.reset_tokens:
            usuario_reset = st.session_state.reset_tokens[token_in_url]
            st.subheader("🔑 Restablecer contraseña")
            new_pass2 = st.text_input("Nueva contraseña", type="password")
            if st.button("Guardar nueva contraseña"):
                users_df = load_users()
                users_df.loc[users_df["usuario"] == usuario_reset, "password"] = new_pass2
                save_users(users_df)
                del st.session_state.reset_tokens[token_in_url]
                st.success("Contraseña cambiada con éxito. Ya puedes iniciar sesión.")
        st.stop()

    st.stop()

# =========================
# App principal
# =========================
st.sidebar.success(f"Conectado como {st.session_state.name} ({st.session_state.user})")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.name = None
    clear_session()
    st.rerun()

# Config correo personal (solo teniente / parquista / sargento)
if st.session_state.user in ["teniente", "parquista", "sargento"]:
    st.sidebar.subheader("📧 Configurar correo")
    users_df = load_users()
    correo_actual = users_df.loc[users_df["usuario"] == st.session_state.user, "correo"].values[0]
    nuevo_correo = st.sidebar.text_input("Tu correo electrónico", value=correo_actual)
    if st.sidebar.button("Guardar correo"):
        if nuevo_correo.strip() == "":
            st.sidebar.error("El correo no puede estar vacío")
        elif (
            nuevo_correo in users_df["correo"].values
            and nuevo_correo != correo_actual
        ):
            st.sidebar.error("Ese correo ya está registrado por otro usuario")
        else:
            users_df.loc[users_df["usuario"] == st.session_state.user, "correo"] = nuevo_correo
            save_users(users_df)
            st.sidebar.success("Correo actualizado con éxito ✅")

# =========================
# Vista por categorías
# =========================
inv_df = load_inventory()

if inv_df.empty:
    st.warning("No hay inventario cargado todavía. Rellena INVENTARIO_BASE en el código y borra data/inventario.csv para regenerar.")
    st.stop()

categorias = sorted(inv_df["categoria"].unique())

st.title("📦 Inventario por categorías")

selected_cat = st.selectbox("Selecciona lote, mochila o caja", categorias)

if selected_cat:
    st.header(f"{selected_cat}")
    cat_inv = inv_df[inv_df["categoria"] == selected_cat].copy()
    cat_inv["inoperativos"] = cat_inv["cantidad_total"] - cat_inv["operativos"]

    st.subheader("Material en esta categoría")

    # Filtros de estado
    with st.expander("🔍 Filtros de visualización"):
        colf1, colf2 = st.columns(2)
        with colf1:
            filtro_ubicacion = st.multiselect(
                "Ubicación",
                ["En parque", "Fuera de parque"],
                default=["En parque", "Fuera de parque"]
            )
        with colf2:
            filtro_operativo = st.multiselect(
                "Estado operativo",
                ["Operativo", "Inoperativo"],
                default=["Operativo", "Inoperativo"]
            )

    # Añadimos columna inoperativos
    cat_inv["inoperativos"] = cat_inv["cantidad_total"] - cat_inv["operativos"]

    # Aplicamos filtros
    mask = pd.Series(True, index=cat_inv.index)

    if "En parque" not in filtro_ubicacion:
        mask &= cat_inv["en_parque"] == 0
    if "Fuera de parque" not in filtro_ubicacion:
        mask &= cat_inv["fuera_parque"] == 0
    if "Operativo" not in filtro_operativo:
        mask &= cat_inv["operativos"] == 0
    if "Inoperativo" not in filtro_operativo:
        mask &= cat_inv["inoperativos"] == 0

    cat_inv_filtrado = cat_inv[mask]

    st.dataframe(cat_inv_filtrado, use_container_width=True)


    tab1, tab2 = st.tabs(["🔁 Registrar movimiento", "🕓 Ver historial"])

    # ========== TAB 1: Registrar movimiento ==========
    with tab1:
        st.subheader("Registrar movimiento")
        material_sel = st.selectbox("Material", cat_inv["material"])
        cant_mov = st.number_input("Cantidad", min_value=1, step=1, value=1)
        accion_mov = st.radio(
        "Acción",
        ["Sacar", "Devolver", "Marcar inoperativo", "Marcar operativo"],
        horizontal=True
    )
    observ_mov = st.text_input("Observación (opcional)", "")
    descontar = False
    if accion_mov == "Marcar inoperativo":
        descontar = st.checkbox("Descontar también del parque")

    if st.button("Confirmar movimiento", type="primary"):
        # localizar la fila en el DF general
        idx = inv_df.index[
            (inv_df["categoria"] == selected_cat) &
            (inv_df["material"] == material_sel)
        ][0]

        if accion_mov == "Sacar":
            if int(inv_df.loc[idx, "en_parque"]) >= cant_mov:
                inv_df.loc[idx, "en_parque"] -= cant_mov
                inv_df.loc[idx, "fuera_parque"] += cant_mov
                st.success(f"Sacaste {cant_mov} {material_sel}")
            else:
                st.error("No hay suficiente stock en parque")
                st.stop()

        elif accion_mov == "Devolver":
            if int(inv_df.loc[idx, "fuera_parque"]) >= cant_mov:
                inv_df.loc[idx, "fuera_parque"] -= cant_mov
                inv_df.loc[idx, "en_parque"] += cant_mov
                st.success(f"Devolviste {cant_mov} {material_sel}")
            else:
                st.error("No hay suficiente stock fuera del parque")
                st.stop()

        elif accion_mov == "Marcar inoperativo":
            if int(inv_df.loc[idx, "operativos"]) >= cant_mov:
                inv_df.loc[idx, "operativos"] -= cant_mov
                if descontar and int(inv_df.loc[idx, "en_parque"]) >= cant_mov:
                    inv_df.loc[idx, "en_parque"] -= cant_mov
                st.success(f"Marcaste {cant_mov} {material_sel} como inoperativo")
            else:
                st.error("No hay suficientes materiales operativos")
                st.stop()

        elif accion_mov == "Marcar operativo":
            inoperativos_actuales = int(inv_df.loc[idx, "cantidad_total"] - inv_df.loc[idx, "operativos"])
            if inoperativos_actuales >= cant_mov:
                inv_df.loc[idx, "operativos"] += cant_mov
                st.success(f"Marcaste {cant_mov} {material_sel} como operativo nuevamente")
            else:
                st.error("No hay suficientes materiales inoperativos para marcar como operativos")
                st.stop()

        save_inventory(inv_df)
        nuevo = pd.DataFrame([{
            "usuario": st.session_state.user,
            "categoria": selected_cat,
            "material": material_sel,
            "cantidad": cant_mov,
            "accion": accion_mov,
            "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "observacion": observ_mov
        }], columns=LOG_COLS)
        log_df = pd.concat([load_log(), nuevo], ignore_index=True)
        save_log(log_df)

   # ========== TAB 2: Historial ==========
with tab2:
    st.subheader("Historial de movimientos")

    log_df = load_log()

    # Filtrar los movimientos de la categoría actual
    log_cat = log_df[log_df["categoria"] == selected_cat].copy()

    # Aseguramos que aparezcan también los nuevos tipos de acción
    acciones_validas = [
        "Sacar", "Devolver", "Marcar inoperativo", "Marcar operativo"
    ]
    log_cat = log_cat[log_cat["accion"].isin(acciones_validas)]

    # Ordenar por hora (más reciente primero)
    log_cat = log_cat.sort_values("hora", ascending=False)

    # Mostrar la tabla
    st.dataframe(
        log_cat[["hora", "usuario", "material", "cantidad", "accion", "observacion"]],
        use_container_width=True
    )

    # Contador resumen
    total_acciones = log_cat["accion"].value_counts()
    st.markdown("### 📊 Resumen de acciones registradas")
    st.bar_chart(total_acciones)

# =========================
# Gestión de materiales (solo teniente / sargento)
# =========================
if st.session_state.user in ["teniente", "sargento"]:
    st.divider()
    st.subheader("⚙️ Gestión de materiales (solo mando)")
    st.markdown("Añadir material nuevo al inventario")

    nueva_categoria = st.text_input(
        "Categoría / Lote / Mochila / Caja (ej: 'LOTE 2 - MOVILIDAD/CONTRAMOVILIDAD 1', 'MOCHILA BLAEX LIMPIEZA DE RUTA')"
    )

    nuevo_material = st.text_input("Nombre del material (ej: 'Pala inglesa larga')")

    nueva_cantidad = st.number_input(
        "Cantidad total inicial",
        min_value=0,
        step=1,
        value=1
    )

    nueva_unidad = st.text_input("Unidad (ej: 'ud', 'uds', 'm', 'kg')", value="ud")

    if st.button("➕ Añadir material al inventario"):
        if nueva_categoria.strip() == "" or nuevo_material.strip() == "":
            st.error("Falta categoría o nombre del material.")
        else:
            inv_df = load_inventory()

            ya_existe = (
                (inv_df["categoria"] == nueva_categoria) &
                (inv_df["material"] == nuevo_material)
            ).any()

            if ya_existe:
                st.error("Ese material ya existe en esa categoría. Usa 'Registrar movimiento' para ajustar cantidades.")
            else:
                nueva_fila = pd.DataFrame([{
                    "categoria": nueva_categoria,
                    "material": nuevo_material,
                    "cantidad_total": nueva_cantidad,
                    "en_parque": nueva_cantidad,
                    "fuera_parque": 0,
                    "operativos": nueva_cantidad,
                    "unidad": nueva_unidad
                }], columns=INV_COLS)

                inv_df = pd.concat([inv_df, nueva_fila], ignore_index=True)
                save_inventory(inv_df)

                # registrar alta en el log
                log_df = load_log()
                nuevo_log = pd.DataFrame([{
                    "usuario": st.session_state.user,
                    "categoria": nueva_categoria,
                    "material": nuevo_material,
                    "cantidad": nueva_cantidad,
                    "accion": "Añadir material nuevo",
                    "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "observacion": "Alta de material en inventario"
                }], columns=LOG_COLS)
                log_df = pd.concat([log_df, nuevo_log], ignore_index=True)
                save_log(log_df)

                st.success(f"'{nuevo_material}' añadido en '{nueva_categoria}' con {nueva_cantidad} {nueva_unidad}. ✅")

                st.rerun()
