import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser la primera instrucción de Streamlit)
st.set_page_config(page_title="MLB DataPick", layout="wide", initial_sidebar_state="expanded")

# 2. CARGAR VARIABLES DE ENTORNO
load_dotenv()

# Intentar leer desde Streamlit Cloud (Secrets) o local (.env)
url: str = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key: str = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    st.error("Error: No se encontraron las credenciales de Supabase. Configura los Secrets en Streamlit.")
    st.stop()

# Inicializar cliente de Supabase
supabase: Client = create_client(url, key)

# 3. MANEJO DE SESIÓN EN STREAMLIT
if "user" not in st.session_state:
    st.session_state.user = None
if "is_vip" not in st.session_state:
    st.session_state.is_vip = False

# 4. FUNCIONES DE AUTENTICACIÓN
def registrar_usuario(email, password):
    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        if res.user:
            st.success("¡Registro exitoso! Ya puedes iniciar sesión en la pestaña correspondiente.")
        else:
            st.error("No se pudo completar el registro. Verifica los datos.")
    except Exception as e:
        st.error(f"Error al registrar: {str(e)}")

def iniciar_sesion(email, password):
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            st.session_state.user = res.user
            
            # Consultar en la tabla pública 'perfiles' si es VIP
            perfil = supabase.table("perfiles").select("is_vip").eq("id", res.user.id).execute()
            if perfil.data:
                st.session_state.is_vip = perfil.data[0].get("is_vip", False)
            else:
                st.session_state.is_vip = False
                
            st.toast("¡Inicio de sesión correcto!", icon="🔥")
            st.rerun()
        else:
            st.error("Credenciales incorrectas.")
    except Exception as e:
        st.error(f"Error de inicio de sesión: {str(e)}")

def cerrar_sesion():
    try:
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.is_vip = False
        st.rerun()
    except Exception as e:
        st.error(f"Error al cerrar sesión: {str(e)}")

# 5. BARRA LATERAL (AUTENTICACIÓN)
with st.sidebar:
    st.title("⚾ MLB DataPick")
    st.write("---")
    
    if st.session_state.user:
        st.write(f"**Usuario:** {st.session_state.user.email}")
        if st.session_state.is_vip:
            st.success("✨ Acceso VIP Activo")
        else:
            st.info("Plan: Usuario Estándar")
        
        if st.button("Cerrar Sesión", use_container_width=True):
            cerrar_sesion()
    else:
        tab_login, tab_registro = st.tabs(["Iniciar Sesión", "Registrarse"])
        
        with tab_login:
            login_email = st.text_input("Correo electrónico", key="login_email")
            login_pass = st.text_input("Contraseña", type="password", key="login_pass")
            if st.button("Entrar", use_container_width=True):
                if login_email and login_pass:
                    iniciar_sesion(login_email, login_pass)
                else:
                    st.warning("Por favor rellena todos los campos.")
                    
        with tab_registro:
            reg_email = st.text_input("Correo electrónico", key="reg_email")
            reg_pass = st.text_input("Contraseña (mínimo 6 caracteres)", type="password", key="reg_pass")
            if st.button("Crear Cuenta", use_container_width=True):
                if reg_email and reg_pass:
                    if len(reg_pass) >= 6:
                        registrar_usuario(reg_email, reg_pass)
                    else:
                        st.sidebar.error("La contraseña debe tener al menos 6 caracteres.")
                else:
                    st.warning("Por favor rellena todos los campos.")

# 6. CONTENIDO PRINCIPAL Y CONTROL DE CONTENIDO VIP
st.title("Predicciones del Día - MLB")
st.write("Analítica avanzada y Sabermetría para tus decisiones de mercado.")

# Simulación de partidos (Datos de prueba para la interfaz)
partidos = [
    {"equipos": "NY Yankees vs Boston Red Sox", "tipo": "Gratis", "prediccion": "Yankees a ganar (-140)", "analisis": "Merrit tiene un xFIP de 3.20 en sus últimas 3 salidas. Boston sufre contra lanzadores zurdos (wRC+ de 88)."},
    {"equipos": "LA Dodgers vs SF Giants", "tipo": "Gratis", "prediccion": "Alta de 8.5 carreras", "analisis": "El viento sopla hacia afuera a 12mph. Ambos abridores conceden un alto porcentaje de elevados (FB% > 42%)."},
    {"equipos": "Houston Astros vs NY Mets", "tipo": "VIP", "prediccion": "Astros -1.5 Run Line", "analisis": "Ventaja clara en el bullpen. El SIERA promedio de Houston es de 2.85 frente a un pen de los Mets muy desgastado."},
    {"equipos": "Atlanta Braves vs Philadelphia Phillies", "tipo": "VIP", "prediccion": "Phillies a ganar (+110)", "analisis": "Valor matemático detectado en las cuotas de apertura. Wheeler domina la alineación interna de Atlanta."}
]

# Mostrar los partidos en la interfaz
for p in partidos:
    with st.container():
        st.write("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(p["equipos"])
            
        with col2:
            if p["tipo"] == "VIP":
                st.markdown("🔴 **PARTIDO VIP**")
            else:
                st.markdown("🟢 **PARTIDO GRATUITO**")
        
        # Lógica de bloqueo
        if p["tipo"] == "VIP" and not st.session_state.is_vip:
            st.warning("🔒 Este análisis está reservado exclusivamente para miembros VIP. Inicia sesión o adquiere un plan para desbloquearlo.")
        else:
            if p["tipo"] == "VIP" and st.session_state.is_vip:
                # Efecto visual de celebración al desbloquear contenido premium
                st.balloons()
            st.info(f"**Predicción sugerida:** {p['prediccion']}")
            st.write(f"**Análisis Técnico:** {p['analisis']}")
