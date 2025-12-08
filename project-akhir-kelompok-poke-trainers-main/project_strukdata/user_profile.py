import streamlit as st
from data_manager import save_user_profile, get_user_data
from components import pokemon_card_html, get_pokemon_detail
import time

def logout_user():
    """Merupakan state pengguna dan kembali ke halaman login (main page)."""
    st.session_state.clear()
    st.session_state.logged_in = False
    st.session_state.page = "login"
    st.rerun()

def save_deck_only():
    """Menyimpan daftar Pokémon individual ke DB."""
    if st.session_state.get("logged_in") and st.session_state.get("email"):
        data_to_save = {'saved_deck': st.session_state.saved_deck}
        data_to_save['profile'] = st.session_state.profile.copy()
        save_user_profile(st.session_state.email, data_to_save)
        st.toast("Deck berhasil disimpan!")

def remove_from_deck(pokemon_name):
    """Menghapus Pokémon dari deck dan menyimpan ke DB."""
    if pokemon_name in st.session_state.saved_deck:
        st.session_state.saved_deck.remove(pokemon_name)
        save_deck_only()
        st.rerun()

def delete_team(team_name):
    """Menghapus tim lengkap dari saved_teams dan menyimpan ke DB."""
    if team_name in st.session_state.saved_teams:
        del st.session_state.saved_teams[team_name]
        data_to_save = {'saved_teams': st.session_state.saved_teams}
        save_user_profile(st.session_state.email, data_to_save)
        st.toast(f"Tim '{team_name}' berhasil dihapus!")
        st.rerun()

def clear_search_history():
    """Menghapus seluruh riwayat pencarian dan menyimpan ke DB."""
    st.session_state.search_history = []
    data_to_save = {'search_history': st.session_state.search_history}
    save_user_profile(st.session_state.email, data_to_save)
    st.toast("Riwayat pencarian berhasil dihapus!")
    time.sleep(0.5)
    st.rerun()

def show_user_account():
    st.title("👤 Profil Pengguna")
    
    st.header("Informasi Akun")
    
    with st.form(key='profile_form'):
        current_profile = st.session_state.profile
        
        new_nama = st.text_input("Nama Pengguna", value=current_profile.get("Nama", st.session_state.username))
        st.text_input("Email (Tidak Dapat Diubah)", value=current_profile.get("Email", st.session_state.email), disabled=True)
        new_deskripsi = st.text_area("Deskripsi Diri/Motto", value=current_profile.get("Deskripsi", ""), height=100)
        
        col_save, col_cancel = st.columns(2)
        with col_save:
            submit_button = st.form_submit_button(label='Simpan Perubahan', type="primary")

        if submit_button:
            updated_profile = {
                "Nama": new_nama,
                "Email": current_profile.get("Email", st.session_state.email),
                "Deskripsi": new_deskripsi
            }
            
            data_to_save = {'profile': updated_profile}
            success = save_user_profile(st.session_state.email, data_to_save)
            
            if success:
                st.session_state.profile = updated_profile
                st.session_state.username = new_nama
                st.success("Profil berhasil diperbarui!")
            else:
                st.error("Gagal menyimpan perubahan profil.")

    st.markdown("---")
    
    st.header("🛡️ Tim Pokémon Tersimpan (Saved Teams)")
    
    if st.session_state.saved_teams:
        for team_name, team_list in st.session_state.saved_teams.items():
            st.subheader(f"Tim: {team_name}")
            
            cols = st.columns(len(team_list))
            
            for i, pokemon_name in enumerate(team_list):
                detail = get_pokemon_detail(pokemon_name.lower().strip())
                if detail:
                    with cols[i]:
                        st.markdown(pokemon_card_html(detail, include_id=False), unsafe_allow_html=True)
                        
            st.button("Hapus Tim", key=f"del_team_{team_name}", on_click=delete_team, args=(team_name,), type="secondary")
            st.markdown("---")
    else:
        st.info("Anda belum menyimpan tim lengkap (6 Pokémon). Simpan tim dari Auto Team Builder.")
        
    st.markdown("---")

    st.header("🌟 Dek Pokémon Anda (Individual Saved Pokémon)")

    if st.session_state.undo_stack:
        last_added = st.session_state.undo_stack[-1]
        if st.button(f"Undo Last Addition ({last_added})"):
            st.session_state.undo_stack.pop()
            if last_added in st.session_state.saved_deck:
                st.session_state.saved_deck.remove(last_added)
                save_deck_only()
                st.toast(f"{last_added} dihapus dari deck.")
            st.rerun()
            
    if st.session_state.saved_deck:
        st.subheader("Daftar Pokémon:")
    
        for idx, name in enumerate(st.session_state.saved_deck):
            col_idx, col_name, col_btn = st.columns([0.5, 4, 1])
            with col_idx:
                st.write(f"{idx+1}.")
            with col_name:
                 st.markdown(f"**{name}**")
            with col_btn:
                 st.button("Hapus", key=f"del_deck_{name}", on_click=remove_from_deck, args=(name,), use_container_width=True, type="secondary")

    else:
        st.info("Anda belum menyimpan Pokémon individual ke deck.")

    st.markdown("---")

    st.header("🔍 Riwayat Pencarian (Search History)")
    
    if st.session_state.search_history:
        history_display = st.session_state.search_history[::-1] 
        
        st.button("Hapus Semua Riwayat", on_click=clear_search_history, type="secondary")
            
        st.subheader("Pencarian Terbaru:")
        
        num_history = len(history_display)
        cols = st.columns(5) 
        
        for i, search_term in enumerate(history_display):
            with cols[i % 5]:
                st.markdown(
                    f"""
                    <span style='
                        display:inline-block; 
                        border: 1px solid #2b6cb0; 
                        padding: 6px 10px; 
                        margin-bottom: 8px; 
                        border-radius: 999px; 
                        background-color: #e6f2ff;
                        font-size: 14px;
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        cursor: default;
                    '>
                        {search_term}
                    </span>
                    """, 
                    unsafe_allow_html=True
                )


        st.caption("Maksimal 50 riwayat terakhir disimpan. Tekan tombol Home dan gunakan kotak pencarian untuk mencari ulang.")
    else:
        st.info("Anda belum melakukan pencarian Pokémon.")
        
    st.markdown("---")

    if st.button("🚪Logout", use_container_width=True):
        logout_user()
