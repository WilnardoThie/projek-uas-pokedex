import streamlit as st
from components import is_gmail
from data_manager import register_user, authenticate_user, get_user_email_by_username 

def handle_login_success(user_data, email):
    
    st.session_state.logged_in = True
    st.session_state.email = email
    st.session_state.username = user_data.get("username", email.split('@')[0])
    st.session_state.profile = user_data.get("profile", {})
    st.session_state.saved_deck = user_data.get("saved_deck", []) 
    st.session_state.saved_teams = user_data.get("saved_teams", {}) 
    st.session_state.page = "main"
    st.session_state.feature_page = None
    st.session_state.loaded_ids = [] 
    st.session_state.batch = 0
    st.session_state.search_history = user_data.get("search_history", []) 
    st.session_state.team_result = None
    st.session_state.owned_pokemon_input = []
    
    st.rerun()

def show_login_page(login_success_callback=handle_login_success):
    
    st.markdown("""
        <div class="login-container">
            <div class="title">Pokédex</div>
            <div class="subtitle">Masuk atau Daftar untuk akses penuh fitur Deck & Team Builder.</div>
        </div>
    """, unsafe_allow_html=True)

    login_tab, register_tab = st.tabs(["Masuk", "Daftar"])
    
    with login_tab:
        st.subheader("Masuk ke Akun Anda")
        
        login_input = st.text_input("Email / Username", key="login_input") 
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary", use_container_width=True):
            if not login_input or not login_password:
                st.error("Email/Username dan password harus diisi.")
            else:
                user_data = None
                login_key = None
                
                
                if "@" in login_input:
                    user_data = authenticate_user(login_input, login_password)
                    if user_data:
                        login_key = login_input
                
                else:
                    email_from_username = get_user_email_by_username(login_input)
                    if email_from_username:
                        user_data = authenticate_user(email_from_username, login_password)
                        if user_data:
                            login_key = email_from_username 
                
                if user_data and login_key:
                    st.success("Login berhasil!")
                    login_success_callback(user_data, login_key)
                else:
                    st.error("Email/Username atau password salah.")

    with register_tab:
        st.subheader("Daftar Akun Baru")
        reg_username = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email (Hanya @gmail.com)", key="reg_email")
        reg_password = st.text_input("Password Baru", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Konfirmasi Password", type="password", key="reg_password_confirm")

        if st.button("Daftar", use_container_width=True):
            if not reg_username or not reg_email or not reg_password or not reg_password_confirm:
                st.error("Semua kolom harus diisi.")
            elif not is_gmail(reg_email):
                st.error("Email harus menggunakan domain @gmail.com.")
            elif reg_password != reg_password_confirm:
                st.error("Konfirmasi password tidak cocok.")
            elif len(reg_password) < 6:
                st.error("Password minimal 6 karakter.")
            else:
                if register_user(reg_email, reg_password, reg_username):
                    user_data = authenticate_user(reg_email, reg_password)
                    if user_data:
                        st.success(f"Akun {reg_username} berhasil dibuat! Anda sekarang login.")
                        login_success_callback(user_data, reg_email)
                    else:
                         st.error("Pendaftaran berhasil, tetapi gagal login otomatis.")
                else:
                    st.error("Email ini sudah terdaftar. Coba login.")
