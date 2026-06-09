import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="MLB DataPick", layout="wide", initial_sidebar_state="expanded")

# 2. Estilo CSS Deportivo Oscuro
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #ffffff; }
    .price-card {
        background-color: #161f32; padding: 20px; border-radius: 15px;
        border: 2px solid #233554; text-align: center; margin-bottom: 15px;
    }
    .price-title { color: #00df89; font-size: 22px; font-weight: bold; }
    .price-value { font-size: 32px; font-weight: bold; margin: 5px 0; color: #ffffff; }
    .main-title { color: #00b4d8; font-size: 50px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- SCRIPT PARA BUSCAR LOS PARTIDOS REALES DE HOY ---
@st.cache_data(ttl=3600)  # Guarda los datos por 1 hora para no saturar la API
def obtener_partidos_mlb():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={fecha_hoy}"
    
    try:
        response = requests.get(url)
        data = response.json()
        partidos = []
        
        if "dates" in data and len(data["dates"]) > 0:
            for juego in data["dates"][0]["games"]:
                home_team = juego["teams"]["home"]["team"]["name"]
                away_team = juego["teams"]["away"]["team"]["name"]
                status = juego["status"]["detailedState"]
                
                # Simulamos las probabilidades usando un cálculo basado en el ID del juego
                # Esto es temporal hasta que metas tu modelo matemático de predicciones
                prob_home = 50 + (juego["gamePk"] % 20)
                prob_away = 100 - prob_home
                
                prediccion = f"{home_team} ML" if prob_home > prob_away else f"{away_team} ML"
                
                partidos.append({
                    "Partido (Visitante vs Local)": f"{away_team} @ {home_team}",
                    "Estado": status,
                    "Probabilidad": f"{home_team} ({prob_home}%) vs {away_team} ({prob_away}%)",
                    "Sugerencia VIP": prediccion
                })
        return pd.DataFrame(partidos)
    except Exception as e:
        return pd.DataFrame(columns=["Partido (Visitante vs Local)", "Estado", "Probabilidad", "Sugerencia VIP"])

# --- BARRA LATERAL: SISTEMA DE LOGIN (SIMULACIÓN DE CLIENTE VIP) ---
with st.sidebar:
    st.markdown("## 🔐 Acceso VIP")
    st.write("Si ya compraste tu suscripción, ingresa tus credenciales aquí:")
    
    usuario = st.text_input("Usuario (Correo)")
    contrasena = st.text_input("Contraseña", type="password")
    
    # Creamos un usuario de prueba para nosotros
    if st.button("Iniciar Sesión", use_container_width=True):
        if usuario == "admin@mlb.com" and contrasena == "1234":
            st.session_state["vip_activo"] = True
            st.success("¡Acceso concedido, Bienvenido!")
        else:
            st.error("Credenciales incorrectas o membresía vencida.")
            st.session_state["vip_activo"] = False

    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state["vip_activo"] = False
        st.rerun()

# --- CUERPO PRINCIPAL DE LA PÁGINA ---
st.markdown('<div class="main-title">MLB DataPick</div>', unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #8892b0;'>Sistema Inteligente de Predicciones Basado en Datos</h3>", unsafe_allow_html=True)
st.write("---")

col_izquierda, col_derecha = st.columns([1, 1.3], gap="large")

with col_izquierda:
    st.markdown("## 📊 El Algoritmo")
    st.write("Nuestro sistema procesa estadísticas históricas, rendimiento de pitchers y rachas en tiempo real.")
    
    st.markdown("### 💳 Suscripciones VIP")
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        st.markdown('<div class="price-card"><div class="price-title">Pase Semanal</div><div class="price-value">$9.99</div><p>• 7 días VIP</p></div>', unsafe_allow_html=True)
    with col_sub2:
        st.markdown('<div class="price-card" style="border: 2px solid #00b4d8;"><div class="price-title" style="color: #00b4d8;">Plan Mensual</div><div class="price-value">$29.99</div><p>• 30 días VIP</p></div>', unsafe_allow_html=True)

with col_derecha:
    st.markdown("## 🔮 Predicciones del Día")
    
    # Descargamos los partidos reales usando tu función
    df_juegos = obtener_partidos_mlb()
    
    # Verificamos si el usuario está logueado como VIP
    if st.session_state.get("vip_activo", False):
        st.balloons() # ¡Efecto de celebración!
        st.success("🔓 ¡Acceso VIP Activo! Viendo los datos reales y predicciones en vivo del sistema:")
        
        # Mostramos la tabla COMPLETA con las predicciones del algoritmo
        st.dataframe(df_juegos, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Contenido Protegido. Inicia sesión en la barra lateral para desbloquear las sugerencias del algoritmo.")
        
        # Mostramos los partidos reales pero OCULTAMOS las predicciones y probabilidades
        if not df_juegos.empty:
            st.write("### Partidos programados para hoy (Bloqueados):")
            df_bloqueado = df_juegos[["Partido (Visitante vs Local)", "Estado"]].copy()
            df_bloqueado["Probabilidad"] = "🔒 Solo para Miembros VIP"
            df_bloqueado["Sugerencia VIP"] = "🔒 Solo para Miembros VIP"
            st.dataframe(df_bloqueado, use_container_width=True, hide_index=True)
        else:
            st.info("No hay partidos programados para el día de hoy.")