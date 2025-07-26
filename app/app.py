import streamlit as st
import requests
import os
import datetime
import json
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(page_title="URL Shortener & QR Generator", layout="centered")

COOKIES_SECRET_KEY = "MOJ_BARDZO_TAJNY_I_BEZPIECZNY_KLUCZ"
cookies = EncryptedCookieManager(password=COOKIES_SECRET_KEY, prefix="url_shortener/auth/")
if not cookies.ready():
    st.stop()

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def create_user(username, password):
    password_hash = generate_password_hash(password)
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)"),
                     {"username": username, "password_hash": password_hash})
        conn.commit()

def get_user(username):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username}).fetchone()
        return result

def shorten_url(long_url, user_id):
    api_url = "https://cleanuri.com/api/v1/shorten"
    payload = {'url': long_url}
    response = requests.post(api_url, data=payload)
    response.raise_for_status()
    short_url = response.json().get('result_url')
    if short_url:
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO links (original_url, short_url, user_id) VALUES (:orig, :short, :uid)"),
                         {"orig": long_url, "short": short_url, "uid": user_id})
            conn.commit()
    return short_url

def get_user_history(user_id):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT original_url, short_url FROM links WHERE user_id = :uid ORDER BY created_at DESC LIMIT 10"),
                              {"uid": user_id}).fetchall()
        return result

def generate_qr_code_image(url_to_encode, color, bg_color):
    color_hex = color.lstrip('#')
    bg_color_hex = bg_color.lstrip('#')
    api_base_url = "https://api.qrserver.com/v1/create-qr-code/"
    qr_code_url = f"{api_base_url}?size=250x250&data={url_to_encode}&color={color_hex}&bgcolor={bg_color_hex}"
    response = requests.get(qr_code_url)
    response.raise_for_status()
    return response.content

def check_session():
    if 'logged_in' not in st.session_state:
        user_info_str = cookies.get('user_info')
        if user_info_str:
            user_cookie = json.loads(user_info_str)
            st.session_state.logged_in = True
            st.session_state.username = user_cookie.get('username')
            st.session_state.user_id = user_cookie.get('user_id')
        else:
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
    if 'active_history_index' not in st.session_state:
        st.session_state.active_history_index = None

check_session()

if st.session_state.get('logged_in'):
    st.sidebar.success(f"Zalogowano jako: **{st.session_state.username}**")
    if st.sidebar.button("Wyloguj"):
        if 'user_info' in cookies: del cookies['user_info']
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.rerun()

    st.title("🔗 Skracacz linków i Generator kodów QR")
    with st.sidebar:
        st.header("🎨 Opcje Kodu QR")
        qr_color = st.color_picker("Wybierz kolor kodu", "#000000")
        qr_bg_color = st.color_picker("Wybierz kolor tła", "#FFFFFF")
    
    long_url_input = st.text_input("Wprowadź długi URL:", "https://github.com/Zejcha/url-qr-shortener")

    if st.button("Generuj!", type="primary"):
        if long_url_input:
            try:
                with st.spinner("Przetwarzam..."):
                    short_url = shorten_url(long_url_input, st.session_state.user_id)
                    qr_code_image_bytes = generate_qr_code_image(short_url, qr_color, qr_bg_color)
                st.session_state.newly_generated_short_url = short_url
                st.session_state.newly_generated_qr_image = qr_code_image_bytes
                st.session_state.active_history_index = None
            except Exception as e:
                st.error(f"Wystąpił błąd: {e}")

    if 'newly_generated_qr_image' in st.session_state and st.session_state.active_history_index is None:
        st.success("Oto Twój skrócony link i spersonalizowany kod QR:")
        col1, col2 = st.columns([1.5, 1])
        with col1: st.code(st.session_state.newly_generated_short_url)
        with col2:
            st.image(st.session_state.newly_generated_qr_image)
            st.download_button("Pobierz kod QR", st.session_state.newly_generated_qr_image, f"qr_{st.session_state.newly_generated_short_url.split('/')[-1]}.png", "image/png")

    st.write("---")
    st.subheader("📜 Twoja historia ostatnich 10 linków")
    history = get_user_history(st.session_state.user_id)
    if history:
        for i, (orig, short) in enumerate(history):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**Oryginał:** `{orig}`")
                st.write(f"**Skrócony:** `{short}`")
            with col2:
                button_label = "Ukryj QR" if st.session_state.active_history_index == i else "Pokaż QR"
                if st.button(button_label, key=f"history_qr_{i}"):
                    if st.session_state.active_history_index == i:
                        st.session_state.active_history_index = None
                    else:
                        st.session_state.active_history_index = i
                        if 'newly_generated_qr_image' in st.session_state:
                            del st.session_state['newly_generated_qr_image']
                    st.rerun()

            if st.session_state.active_history_index == i:
                with st.spinner("Generuję kod QR..."):
                    qr_code_image_bytes = generate_qr_code_image(short, qr_color, qr_bg_color)
                st.image(qr_code_image_bytes, width=250)
                st.download_button("Pobierz ten kod QR", qr_code_image_bytes, f"qr_{short.split('/')[-1]}.png", "image/png", key=f"download_{i}")
            
            st.write("---")
    else:
        st.info("Nie masz jeszcze żadnych skróconych linków.")

else:
    st.title("Witaj w Skracaczu Linków!")
    login_tab, register_tab = st.tabs(["Logowanie", "Rejestracja"])
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Nazwa użytkownika")
            password = st.text_input("Hasło", type="password")
            submitted = st.form_submit_button("Zaloguj")
            if submitted:
                user = get_user(username)
                if user and check_password_hash(user.password_hash, password):
                    user_info = {'username': user.username, 'user_id': user.id}
                    cookies['user_info'] = json.dumps(user_info)
                    st.session_state.logged_in = True
                    st.session_state.username = user.username
                    st.session_state.user_id = user.id
                    st.rerun()
                else:
                    st.error("Niepoprawna nazwa użytkownika lub hasło.")
    with register_tab:
        with st.form("register_form"):
            new_username = st.text_input("Wybierz nazwę użytkownika")
            new_password = st.text_input("Wybierz hasło", type="password")
            submitted = st.form_submit_button("Zarejestruj")
            if submitted:
                if get_user(new_username):
                    st.error("Ta nazwa użytkownika jest już zajęta.")
                else:
                    create_user(new_username, new_password)
                    st.success("Konto zostało utworzone! Możesz się teraz zalogować.")
