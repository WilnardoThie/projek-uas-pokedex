import streamlit as st
import random
from components import (
    set_page_config_and_style, 
    get_pokemon_detail, 
    get_generation_range_from_api, 
    pokemon_card_html,
    fetch, API_BASE,
    remove_evolutionary_duplicates
)
from login import show_login_page, handle_login_success 
from user_profile import show_user_account 
from encyclopedia import show_move_item_ability, show_catching_probability
from data_manager import get_user_data, save_user_profile 
from ai_manager import (
    generate_optimized_team, 
    generate_strategy_guide, 
    generate_synergy_combo, 
    generate_pokemon_build
)

set_page_config_and_style()

@st.cache_data(ttl=86400)
def get_all_pokemon_names():
    
    data = fetch(f"{API_BASE}/pokemon?limit=1500") 
    if data and 'results' in data:
        return [item['name'].title() for item in data['results']]
    return []

def clear_user_state():
    
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.username = ""
    st.session_state.profile = {}
    st.session_state.saved_deck = []
    st.session_state.saved_teams = {}
    st.session_state.undo_stack = []
    st.session_state.search_history = [] 
    
    st.session_state.team_result = None
    st.session_state.owned_pokemon_input = []
    st.session_state.loading_team = False
    st.session_state.strategy_result = None    
    st.session_state.synergy_result = None 
    
    st.session_state.loading_build = False
    st.session_state.build_pokemon_input = ""
    st.session_state.build_result = None
    
    st.session_state.loading_location = False 
    st.session_state.location_pokemon_input = ""
    st.session_state.location_result = None 
    
    st.session_state.page = "login"
    st.session_state.feature_page = None

def init_session_state():
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        
    if "page" not in st.session_state:
        st.session_state.page = "login" if not st.session_state.logged_in else "main"
        
    for var in ["email", "username", "profile", "feature_page", 
                "loaded_ids", "batch", "current_gen", "saved_deck", 
                "saved_teams", "undo_stack", "search_history", "loading_team", 
                "team_result", "owned_pokemon_input", "loading_strategy", "strategy_result",
                "synergy_result", "loading_build", "build_pokemon_input", "build_result",
                "loading_location", "location_pokemon_input", "location_result",
                "team_builder_theme"]: 
        if var not in st.session_state:
            default_value = [] if var in ["loaded_ids", "saved_deck", "undo_stack", "search_history", "owned_pokemon_input"] else \
                            {} if var == "saved_teams" or var == "profile" else \
                            0 if var == "batch" else \
                            "All Generations" if var == "current_gen" else \
                            False if var in ["loading_team", "loading_strategy", "loading_build", "loading_location"] else \
                            None if var in ["feature_page", "team_result", "strategy_result", "synergy_result", "build_result", "location_result"] else \
                            ""
            st.session_state[var] = default_value

    if st.session_state.email and not st.session_state.profile and st.session_state.logged_in:
        user_data = get_user_data(st.session_state.email)
        if user_data:
            st.session_state.username = user_data.get("username", st.session_state.email.split('@')[0])
            st.session_state.profile = user_data.get("profile", {})
            st.session_state.saved_deck = user_data.get('saved_deck', [])
            st.session_state.saved_teams = user_data.get('saved_teams', {})
            st.session_state.search_history = user_data.get('search_history', []) 
        else:
            clear_user_state()

def save_deck_to_db():
    if st.session_state.get("logged_in") and st.session_state.get("email"):
        deck_to_save = list(set(st.session_state.saved_deck)) 
        
        data_to_save = {}
        data_to_save['saved_deck'] = deck_to_save
        data_to_save['profile'] = st.session_state.profile.copy() 

        success = save_user_profile(st.session_state.email, data_to_save)
        if success:
            st.session_state.saved_deck = deck_to_save
            st.toast("Deck berhasil disimpan ke akun Anda!")
        else:
            st.error("Gagal menyimpan deck. Silakan coba lagi.")

def save_teams_to_db():
    
    if st.session_state.get("logged_in") and st.session_state.get("email"):
        data_to_save = {}
        data_to_save['saved_teams'] = st.session_state.saved_teams.copy()
        
        success = save_user_profile(st.session_state.email, data_to_save)
        if success:
            st.toast("Tim berhasil disimpan ke akun Anda!")
        else:
            st.error("Gagal menyimpan tim. Silakan coba lagi.")

def save_history_to_db():
    
    if st.session_state.get("logged_in") and st.session_state.get("email"):
        
        history_to_save = st.session_state.search_history[-50:] 
        data_to_save = {}
        data_to_save['search_history'] = history_to_save
        
        success = save_user_profile(st.session_state.email, data_to_save)
        if success:
             st.session_state.search_history = history_to_save
             
             pass

def show_auto_team_builder():
    
    st.title("🤖 Auto Team Builder (AI Powered)")
    st.info("AI akan menyarankan tim 6 Pokémon terbaik dari Gen 1-9. Anda bisa memasukkan Pokémon yang sudah Anda miliki untuk dilengkapi.")
    
    all_pokemon_names = get_all_pokemon_names()
    
    owned_pokemon_input = st.multiselect(
        "Pilih Pokémon yang Sudah Anda Miliki (Maksimal 5)",
        options=all_pokemon_names,
        max_selections=5,
        default=st.session_state.owned_pokemon_input,
        key="owned_pokemon_selector"
    )
    st.session_state.owned_pokemon_input = owned_pokemon_input

  
    if st.button("Generate Team Terbaik", type="primary", use_container_width=True):
        st.session_state.loading_team = True
        st.session_state.team_result = None
        st.rerun() 
        
    if st.session_state.get("loading_team"):
        theme_to_use = st.session_state.get("team_builder_theme", "")
        with st.spinner(f"🧠 AI sedang membangun tim terbaik untuk Anda..."):
            team_result_raw = generate_optimized_team(
                theme_to_use, 
                st.session_state.owned_pokemon_input
            )
            
            if team_result_raw:
                final_team = remove_evolutionary_duplicates(team_result_raw['team']) 
            
                if len(final_team) < len(team_result_raw['team']):
                    st.warning("⚠️ Perhatian: Beberapa Pokémon (evolusi dan pra-evolusi) telah difilter untuk memastikan hanya ada satu per garis evolusi. Hanya **evolusi tertinggi** yang dipertahankan.")

                team_result_raw['team'] = final_team 
                st.session_state.team_result = team_result_raw
            else:
                st.error("Gagal mendapatkan saran tim dari AI.")

            st.session_state.loading_team = False
            st.rerun()

    if st.session_state.get("team_result"):
        result = st.session_state.team_result
        st.subheader("🎉 Tim Rekomendasi AI")
        
        st.markdown(f"**Alasan Rekomendasi:** *{result['reason']}*")
        
        cols = st.columns(3)
        ai_team_names = [name.title() for name in result['team']] 
        
        for i, name in enumerate(ai_team_names):
            detail = get_pokemon_detail(name.lower().strip())
            if not detail:
                st.warning(f"Detail untuk Pokémon **{name}** tidak ditemukan. Pastikan nama Pokémon benar.")
                continue
            
            with cols[i % 3]:
                st.markdown(pokemon_card_html(detail), unsafe_allow_html=True)
                
                if st.session_state.get("logged_in"):
                    name_to_save = detail['name'].title()
                    
                    if st.button(f"Add to Deck", key=f"save_ai_{detail['id']}_deck", use_container_width=True):
                        if name_to_save not in st.session_state.saved_deck:
                            st.session_state.saved_deck.append(name_to_save)
                            st.session_state.undo_stack.append(name_to_save)
                            save_deck_to_db() 
                        else:
                            st.toast(f"{name_to_save} sudah ada di deck Anda.", icon='⚠️')

        if st.session_state.get("logged_in"):
            st.markdown("---")
            st.subheader("Simpan Tim Lengkap (6 Pokémon)")
            
            team_name = st.text_input("Beri nama tim ini:", key="team_save_name")
            
            if st.button("Simpan Tim Ini ke Saved Teams", type="secondary"):
                if not team_name:
                    st.error("Nama tim harus diisi.")
                elif team_name in st.session_state.saved_teams:
                    st.error(f"Tim dengan nama '{team_name}' sudah ada. Pilih nama lain.")
                else:
                    st.session_state.saved_teams[team_name] = ai_team_names
                    save_teams_to_db()
                    st.success(f"Tim '{team_name}' berhasil disimpan!")
        else:
            st.info("Login untuk menyimpan hasil tim ini ke deck atau saved teams Anda.")
                          
    st.markdown("---")
    st.caption("Kembali ke Home untuk melanjutkan pencarian Pokémon.")

def show_strategy_guides():
    
    st.title("📚 Strategy Guides & Tutorials (AI Powered)")
    st.info("Pilih topik atau masukkan topik spesifik, lalu AI akan membuat panduan strategi khusus untuk Anda.")

    curated_topics = [
        "Pilih Topik Terkurasi...",
        "Dasar-Dasar Tipe (Type Matchups)",
        "Memahami Statistik dan EV/IV",
        "Strategi Tim Balanced (Seimbang)",
        "Membuat Tier List Sederhana",
        "Weather Teams (Tim Cuaca)",
        "Trick Room Strategy (Strategi Ruangan Trik)",
        "Hyper Offense (Serangan Agresif)",
    ]

    col_topic_select, col_level = st.columns([3, 1])

    with col_topic_select:
        selected_topic = st.selectbox(
            "Pilih Topik Strategi Cepat:",
            options=curated_topics
        )

        custom_topic = st.text_input(
            "Atau masukkan Topik Spesifik Anda:",
            placeholder="Contoh: Counter untuk Garchomp, Set Up Sweeper Terbaik..."
        )
    
    with col_level:
        level = st.selectbox(
            "Level Pemain",
            options=["Pemula (Beginner)", "Menengah (Intermediate)", "Kompetitif (Expert)"]
        )

    topic_to_generate = custom_topic if custom_topic else selected_topic

    if st.button("Generate Guide", type="primary", use_container_width=True):
        if topic_to_generate == "Pilih Topik Terkurasi...":
            st.error("Silakan pilih topik dari daftar atau masukkan topik spesifik.")
        else:
            st.session_state.loading_strategy = True
            st.session_state.strategy_result = None
            st.rerun()
            
    if st.session_state.get("loading_strategy"):
        with st.spinner(f"🧠 AI sedang menyusun panduan {topic_to_generate} untuk pemain {level}..."):
            guide_content = generate_strategy_guide(topic_to_generate, level)
            st.session_state.strategy_result = guide_content
            st.session_state.loading_strategy = False
            st.rerun()

    if st.session_state.get("strategy_result"):
        st.markdown("---")
        st.markdown(st.session_state.strategy_result) 
        st.markdown("---")
        st.caption("Panduan ini dibuat oleh AI Gemini. Informasi mungkin tidak 100% akurat dan harus digunakan sebagai referensi strategis.")

def show_synergy_highlighter():
    
    st.title("✨ Synergy / Combo Highlighter (AI)")
    st.markdown("Fitur ini menganalisis tim Anda (dari **Deck Tersimpan**) dan menyarankan kombinasi sinergi Pokémon, Ability, atau Move untuk meningkatkan efektivitas tim.")

    if not st.session_state.get("logged_in") or not st.session_state.get("saved_deck"):
        st.warning("Silakan **Login** dan simpan minimal satu Pokémon ke **Deck Tersimpan** di halaman utama untuk menggunakan fitur ini.")
        return

    team_list = st.session_state.saved_deck
    
    st.subheader(f"Tim yang Akan Dianalisis ({len(team_list)} Pokémon):")
    
    if team_list:
        cols = st.columns(min(len(team_list), 6))
        for i, pokemon_name in enumerate(team_list):
            with cols[i % 6]:
                
                detail = get_pokemon_detail(pokemon_name.lower())
                if detail:
                    
                    st.markdown(f"""
                        <div style="text-align:center; padding:10px; border:1px solid #ddd; border-radius:8px; margin-bottom:10px;">
                            <strong>{detail['name'].title()}</strong>
                            <img src='{detail['sprites'].get('front_default') or detail['sprites'].get('other', {}).get('official-artwork', {}).get('front_default')}' width='50'/>
                            <span class='type-badge'>{detail['types'][0]['type']['name'].title()}</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                     st.write(pokemon_name.title())

    st.markdown("---")

    if st.button("Analisis Sinergi Tim dengan AI", type="primary", use_container_width=True):
        if not team_list:
             st.error("Deck Tersimpan Anda kosong. Harap tambahkan Pokémon terlebih dahulu.")
             return
             
        with st.spinner("AI sedang menganalisis kombinasi sinergi tim..."):
            
            synergy_report = generate_synergy_combo(team_list)
            st.session_state.synergy_result = synergy_report

    if st.session_state.get("synergy_result"):
        st.markdown(st.session_state.synergy_result, unsafe_allow_html=True)
        st.markdown("---")
        st.caption("Analisis ini disimulasikan oleh AI. Kombo dan saran mungkin memerlukan penyesuaian Move/Ability.")

def show_build_template_library():
    
    st.title("🧱 Build / Template Library (AI Powered)")
    st.markdown("Cari nama Pokémon dan AI akan menyajikan **moveset, item, EV spread, dan strategi** kompetitif yang populer untuk referensi Anda.")

    all_pokemon_names = get_all_pokemon_names()
    
    if 'build_pokemon_input' not in st.session_state:
        st.session_state.build_pokemon_input = ""
    if 'build_result' not in st.session_state:
        st.session_state.build_result = None
    if 'loading_build' not in st.session_state:
        st.session_state.loading_build = False

    selected_pokemon = st.selectbox(
        "Pilih atau Cari Nama Pokémon:",
        options=[""] + all_pokemon_names,
        key="build_pokemon_selector"
    )
    
    if selected_pokemon:
        st.session_state.build_pokemon_input = selected_pokemon.title()
    else:
        st.session_state.build_pokemon_input = ""


    if st.button("Generate Build Template", type="primary", use_container_width=True):
        if not st.session_state.build_pokemon_input:
            st.error("Harap pilih nama Pokémon terlebih dahulu.")
            return
            
        st.session_state.loading_build = True
        st.session_state.build_result = None
        st.rerun() 
        
    if st.session_state.get("loading_build"):
        with st.spinner(f"🧠 AI sedang menganalisis dan menyusun build populer untuk {st.session_state.build_pokemon_input}..."):
            
            build_content = generate_pokemon_build(st.session_state.build_pokemon_input)
            st.session_state.build_result = build_content
            st.session_state.loading_build = False
            st.rerun()

    if st.session_state.get("build_result"):
        result = st.session_state.build_result
        st.divider() 
        
        pokemon_name = result['name'].lower()
        detail = get_pokemon_detail(pokemon_name)
        image_url = detail['sprites'].get('other', {}).get('official-artwork', {}).get('front_default') or detail['sprites'].get('front_default')

        
        col_header, col_img = st.columns([4, 1])
        with col_header:
            st.markdown(f"## 🏆 Build Kompetitif untuk {result['name']} #{detail['id']:04d}")
        with col_img:
            if image_url:
                 st.image(image_url, width=120)

        st.markdown("---")
        st.subheader("Statistik Inti & Fokus")
        
        col_core_stats_1, col_core_stats_2 = st.columns(2)
        
        with col_core_stats_1:
            st.markdown("### Role & EV")
            
            st.info(
                f"**Peran / Role:**\n\n**{result['Role']}**",
            )
            st.info(
                f"**EV Spread:**\n\n**{result['EV_Spread']}**",
            )

        with col_core_stats_2:
            st.markdown("### Item & Ability")
            
            st.info(
                f"**Item Kunci:**\n\n**{result['Item']}**",
            )
            st.info(
                f"**Ability Wajib:**\n\n**{result['Ability']}**",
            )
            
        st.markdown("---")
        
        if detail:
             type_name = detail['types'][0]['type']['name'].title()
             st.markdown(f"**Nature Terbaik:** **{result['Nature']}** | **Tipe Utama:** **{type_name}**")
        else:
             st.markdown(f"**Nature Terbaik:** **{result['Nature']}**")

        st.divider()

        col_moveset, col_strategy = st.columns([1.5, 2.5])
        
        with col_moveset:
            st.markdown("### Moveset (4 Jurusan)")
            moveset_list_md = ""
            for move in result['Moveset']:
                 moveset_list_md += f"* **{move}**\n"
            st.markdown(moveset_list_md)
            
        with col_strategy:
            st.markdown("### Strategi & Penggunaan")
            st.info(result['Strategy'])
            
        st.divider()
        st.caption("Saran ini didasarkan pada data metagame kompetitif populer (simulasi AI).")

def show_map_location_display():
    
    st.title("🗺️ Map / Location Display")
    st.info("Cari nama Pokémon untuk melihat di area atau lokasi mana ia dapat ditemukan.")

    all_pokemon_names = get_all_pokemon_names()
    
    
    if 'location_pokemon_input' not in st.session_state:
        st.session_state.location_pokemon_input = ""
    if 'location_result' not in st.session_state:
        st.session_state.location_result = None
    if 'loading_location' not in st.session_state:
        st.session_state.loading_location = False

    selected_pokemon = st.selectbox(
        "Pilih atau Cari Nama Pokémon:",
        options=[""] + all_pokemon_names,
        key="location_pokemon_selector"
    )
    
    if selected_pokemon:
        st.session_state.location_pokemon_input = selected_pokemon.title()
    else:
        st.session_state.location_pokemon_input = ""

    if st.button("Cari Lokasi Kemunculan", type="primary", use_container_width=True):
        if not st.session_state.location_pokemon_input:
            st.error("Harap pilih nama Pokémon terlebih dahulu.")
            return
            
        st.session_state.loading_location = True
        st.session_state.location_result = None
        st.rerun() 
        
    if st.session_state.get("loading_location"):
        pokemon_name = st.session_state.location_pokemon_input.lower()
        with st.spinner(f"🔍 Mencari lokasi kemunculan untuk {st.session_state.location_pokemon_input}..."):
            
            url = f"{API_BASE}/pokemon/{pokemon_name}/encounters"
            location_data = fetch(url)
            
            locations = []
            if location_data:
                
                locations = [item['location_area']['name'].replace('-', ' ').title() for item in location_data]
            
            st.session_state.location_result = locations
            st.session_state.loading_location = False
            st.rerun()

    if st.session_state.get("location_result") is not None:
        locations = st.session_state.location_result
        st.markdown("---")
        st.subheader(f"📍 Lokasi Kemunculan {st.session_state.location_pokemon_input}")
        
        if locations:
            st.success(f"Ditemukan **{len(locations)}** area lokasi kemunculan.")
               
            cols_per_row = 3
            cols = st.columns(cols_per_row)
            for i, location in enumerate(locations):
                with cols[i % cols_per_row]:
                    st.markdown(f"**{i+1}.** {location}")
                    
        else:
            st.warning("Data lokasi kemunculan untuk Pokémon ini tidak tersedia (atau tidak muncul di alam liar).")

    st.markdown("---")
    st.caption("Data lokasi diambil dari API PokeAPI. Mungkin tidak mencakup semua game atau metode penangkapan.")

def show_default_home_content(search_query, GEN_START, GEN_END, selected_gen_label): 
    
    if search_query:
        normalized_query = search_query.lower().strip()
        st.subheader(f"Hasil Pencarian: {search_query}")

        detail = get_pokemon_detail(normalized_query)
        
        if detail and search_query not in st.session_state.search_history:
               st.session_state.search_history.append(search_query)
               if st.session_state.get("logged_in"):
                   save_history_to_db()

        if not detail:
            st.error("Pokémon tidak ditemukan.")
            return

        st.markdown(pokemon_card_html(detail), unsafe_allow_html=True)
        
        if st.session_state.get("logged_in"):
             name = detail['name'].title()
             if st.button(f"Save {name} to Deck"):
                 if name not in st.session_state.saved_deck:
                    st.session_state.saved_deck.append(name)
                    st.session_state.undo_stack.append(name)
                    save_deck_to_db() 
                 else:
                     st.warning(f"{name} sudah ada di deck Anda.")
        else:
             st.info("Login untuk menyimpan Pokémon ke deck Anda.")
  
    else:
        st.markdown("<div class='header-title'>Featured Pokémon</div>", unsafe_allow_html=True)
        st.write(f"Menampilkan Pokémon acak dari **{selected_gen_label}**. Tekan **Load More**.")

        batch_size = 12
        all_ids = list(range(GEN_START, GEN_END + 1))
        
        available_ids = [x for x in all_ids if x not in st.session_state.loaded_ids]

        batch_needed = False
        
        if not st.session_state.loaded_ids:
            batch_needed = True
      
        if st.session_state.batch > 0:
            batch_needed = True
            st.session_state.batch = 0
            
        if batch_needed and available_ids:
            n_to_pick = min(batch_size, len(available_ids))
            
            try:
                new_ids = random.sample(available_ids, n_to_pick)
            except ValueError:
                new_ids = available_ids[:n_to_pick] 

            st.session_state.loaded_ids.extend(new_ids)

        if st.session_state.loaded_ids:
            cols = st.columns(3)
            for idx, pid in enumerate(st.session_state.loaded_ids):
                detail = get_pokemon_detail(pid)
                if not detail:
                    continue

                with cols[idx % 3]:
                    st.markdown(pokemon_card_html(detail), unsafe_allow_html=True)
                    
                    if st.session_state.get("logged_in"):
                          name = detail['name'].title()
                          if st.button(f"Save #{detail['id']}", key=f"save_{detail['id']}", use_container_width=True):
                              if name not in st.session_state.saved_deck:
                                st.session_state.saved_deck.append(name)
                                st.session_state.undo_stack.append(name)
                                save_deck_to_db() 
                              else:
                                 st.toast(f"{name} sudah ada di deck Anda.", icon='⚠️')
        
        st.markdown("---")
        total_featured = len(st.session_state.loaded_ids)
        total_available = len(all_ids)

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if total_featured < total_available:
                if st.button("Load More Pokémon"):
                    st.session_state.batch = 1 
                    st.rerun()
            else:
                 st.info("Semua Pokémon telah ditampilkan.")

        with c2:
            st.markdown(f"<div style='text-align:center; padding: 10px 0;'>Menampilkan {total_featured} / {total_available} Pokémon</div>", unsafe_allow_html=True)
            
        with c3:
            if st.button("Reset Featured"):
                st.session_state.loaded_ids = []
                st.session_state.batch = 0
                st.rerun()

def show_main_app():
    search_query = ""
    if not st.session_state.feature_page:
        with st.container():
            col1, col3 = st.columns([4, 0.6])
            with col1:
                search_query = st.text_input("Search Pokémon...", 
                                              placeholder="Search Pokémon by Name or ID...", 
                                              label_visibility="collapsed", 
                                              key='search_query_input')
            with col3:
                if st.session_state.get("logged_in"):
                    display_name = st.session_state.profile.get("Nama", st.session_state.get('username','user'))
                    if st.button(f"User: {display_name}"):
                        st.session_state.page = "profile"
                        st.session_state.feature_page = None 
                        st.rerun()
                else:
                    if st.button("Login"):
                        st.session_state.page = "login"
                        st.rerun()
    else:
        with st.container():
            _, col3 = st.columns([4, 0.6])
            with col3:
                if st.session_state.get("logged_in"):
                    display_name = st.session_state.profile.get("Nama", st.session_state.get('username','user'))
                    if st.button(f"User: {display_name}"):
                        st.session_state.page = "profile"
                        st.session_state.feature_page = None 
                        st.rerun()
                else:
                    if st.button("Login"):
                        st.session_state.page = "login"
                        st.rerun()
    
    st.sidebar.title("Pokédex")
    st.sidebar.markdown("### Fitur Utama")

    menu_items = [
        "Move / Item / Ability",
        "Auto Team Builder", 
        "Synergy / Combo Highlighter", 
        "Build / Template Library", 
        "Catching Probability",
        "Map / Location Display",
        "Strategy Guides & Tutorials"
    ]

    for m in menu_items:
        is_active = st.session_state.feature_page == m
        button_type = "primary" if is_active else "secondary"
        
        if st.sidebar.button(m, use_container_width=True, type=button_type):
            
            if is_active:
                 st.session_state.feature_page = None 
            else:
                 st.session_state.feature_page = m
            
            st.session_state.loaded_ids = []
            st.session_state.batch = 0
            st.rerun()
    
    
    st.sidebar.markdown("### Filter by Generation")
    gen_static = {
        "All Generations": (1, 1025), 
        "Generation 1": (1, 151),
        "Generation 2": (152, 251),
        "Generation 3": (252, 386),
        "Generation 4": (387, 493),
        "Generation 5": (494, 649),
        "Generation 6": (650, 721),
        "Generation 7": (722, 809),
        "Generation 8": (810, 898),
    }

    gen_options = gen_static.copy()
    gen9_label = "Generation 9"
    
    try:
        gen9_info = get_generation_range_from_api(9)
        if gen9_info:
            gen9_start, gen9_end, _, _ = gen9_info
            gen_options[gen9_label] = (gen9_start, gen9_end)
        else:
            gen_options[gen9_label] = (899, 1025)
    except Exception:
        gen_options[gen9_label] = (899, 1025)

    selected_gen_label = st.sidebar.selectbox("Select Generation", list(gen_options.keys()))
    GEN_START, GEN_END = gen_options[selected_gen_label]

    if st.session_state.current_gen != selected_gen_label:
        st.session_state.current_gen = selected_gen_label
        st.session_state.loaded_ids = []
        st.session_state.batch = 0
        st.rerun() 
    
    if st.session_state.feature_page:
        
        if st.session_state.feature_page == "Move / Item / Ability":
            show_move_item_ability()
        elif st.session_state.feature_page == "Catching Probability":
            show_catching_probability()
        elif st.session_state.feature_page == "Auto Team Builder":
            show_auto_team_builder()
        elif st.session_state.feature_page == "Strategy Guides & Tutorials":
            show_strategy_guides()
        elif st.session_state.feature_page == "Synergy / Combo Highlighter":
            show_synergy_highlighter()
        elif st.session_state.feature_page == "Build / Template Library":
            show_build_template_library()
        elif st.session_state.feature_page == "Map / Location Display":
            show_map_location_display()
        elif st.session_state.feature_page:
            st.title(st.session_state.feature_page)
            st.warning("Fitur ini belum diimplementasikan.")
    else:
        
        show_default_home_content(search_query, GEN_START, GEN_END, selected_gen_label)

def main():
    init_session_state()

    nav_col1, nav_col2, nav_col3 = st.columns([1, 6, 1])
    with nav_col1:
        
        if st.button("🏠 Home"):
            st.session_state.page = "main"
            st.session_state.feature_page = None
            st.rerun()

    
    if st.session_state.page == "login":
        show_login_page(login_success_callback=handle_login_success) 
    elif st.session_state.page == "profile":
        if not st.session_state.get("logged_in"):
            st.info("Please login to view profile.")
            show_login_page()
        else:
            show_user_account()
    else: 
        if not st.session_state.get("logged_in"):
            st.info("You can browse featured Pokémon without logging in. Login for account features.")
        show_main_app()

if __name__ == "__main__":
    main()
