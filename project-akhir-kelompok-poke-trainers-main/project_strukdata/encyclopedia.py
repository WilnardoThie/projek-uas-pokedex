import streamlit as st
import pandas as pd
from components import fetch, API_BASE, get_pokemon_detail

def show_move_item_ability():
    st.title("📘 Move / Item / Ability Encyclopedia")

    mode = st.radio("Pilih kategori:", ["Move", "Item", "Ability"])
    query = st.text_input(f"Cari {mode}...", placeholder=f"Masukkan nama {mode.lower()}")

    if st.button("Cari"):
        if not query:
            st.error("Silakan masukkan nama yang ingin dicari.")
            return

        name = query.lower().replace(" ", "-") 
        data = fetch(f"{API_BASE}/{mode.lower()}/{name}")

        if not data:
            st.error(f"{mode} '{query}' tidak ditemukan.")
            return

        if mode == "Move":
            damage_class = data['damage_class']['name'].title()
            
            if damage_class == 'Physical':
                st.subheader(f"⚔️ {data['name'].title()} (Fisik)")
            elif damage_class == 'Special':
                st.subheader(f"✨ {data['name'].title()} (Spesial)")
            else: 
                st.subheader(f"🛡️ {data['name'].title()} (Status)")

            col_stat, col_chart = st.columns([1, 1])

            with col_stat:
                st.markdown("### Statistik Dasar")
                st.write(f"• **Type:** **{data['type']['name'].title()}**")
                st.write(f"• **Kategori:** {damage_class}")
                st.write(f"• **Power:** {data.get('power') or '—'}")
                st.write(f"• **Accuracy:** {data.get('accuracy') or '—'}%")
                st.write(f"• **Power Point:** {data.get('pp') or '—'}")
            
            with col_chart:
                st.markdown("### Visualisasi Statistik")
                chart_data = pd.DataFrame({
                    'Statistik': ['Power', 'PP', 'Accuracy'],
                    'Nilai': [
                        data.get('power') or 0,
                        data.get('pp') or 0,
                        data.get('accuracy') or 0
                    ]
                })
                st.bar_chart(
                    chart_data.set_index('Statistik'), 
                    height=250,
                    color="#f63366"
                )

            st.subheader("Efek/Deskripsi")
            effect_entries = data.get('effect_entries', [])
            
            description = next(
                (
                    entry['effect'] 
                    for entry in effect_entries 
                    if 'language' in entry and entry['language'].get('name') == 'en' and 'effect' in entry
                ), 
                "Tidak ada deskripsi tersedia."
            ).replace('\n', ' ')
            
            st.info(description)

        elif mode == "Item":
            st.subheader(f"🎒 Item: {data['name'].title()}")
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if data['sprites'].get('default'):
                    st.image(data['sprites']['default'], caption=data['name'].title(), width=100)
            with col2:
                st.markdown("### Detail Dasar")
                st.write(f"• **Kategori:** {data['category']['name'].title()}")
                st.write(f"• **Harga:** {data.get('cost', 0)}₽")

            st.subheader("Deskripsi & Efek")
            
            effect_entries = data.get('effect_entries', [])
            
            effect_text = next(
                (
                    entry['text'] 
                    for entry in effect_entries 
                    if 'language' in entry and entry['language'].get('name') == 'en' and 'text' in entry
                ), 
                "Tidak ada efek tersedia."
            ).replace('\n', ' ')
            
            st.info(effect_text)

        elif mode == "Ability":
            st.subheader(f"💡 Ability: {data['name'].title()}")

            st.subheader("Efek Ability")
            
            effect_entries = data.get('effect_entries', [])
            
            description_en = next(
                (
                    entry['effect'] 
                    for entry in effect_entries 
                    if 'language' in entry and entry['language'].get('name') == 'en' and 'effect' in entry
                ), 
                "Tidak ada efek tersedia."
            ).replace('\n', ' ')

            # Penyesuaian terjemahan (ditingkatkan dari versi sebelumnya)
            translated_desc = ""
            desc_lower = description_en.lower()
            
            if "not multiplied by 1.5, but by 2" in desc_lower:
                translated_desc = (
                    "Pokémon dengan **Ability** ini memberikan *damage* **2 kali lipat (2×)** ketika "
                    "menggunakan *Move* yang tipenya sama dengan Pokémon, alih-alih Bonus Serangan Tipe Sama (**STAB**) normal sebesar 1.5 kali lipat (1.5×)."
                )
            
            if translated_desc:
                st.markdown("#### Efek (Bahasa Indonesia yang Disesuaikan) 🇮🇩")
                st.success(translated_desc)
                st.markdown("---")

            st.markdown("#### Efek Asli (English) 🇺🇸")
            st.info(description_en)

            pokemon_list = data.get('pokemon', [])
            if pokemon_list:
                st.subheader(f"Pokémon dengan {data['name'].title()} ({len(pokemon_list)})")

                display_names = [p['pokemon']['name'].title() for p in pokemon_list[:10]]
                
                if len(pokemon_list) > 10:
                    st.write(f"**{', '.join(display_names)}**, dan {len(pokemon_list) - 10} lainnya.")
                else:
                    st.write(f"**{', '.join(display_names)}**")
            else:
                st.info("Tidak ada Pokémon yang diketahui memiliki Ability ini.")

def show_catching_probability():
    st.title("🎯 Catching Probability Encyclopedia")
    st.markdown("### Kalkulator Probabilitas Tangkapan")
    st.info("Masukkan detail Pokémon dan kondisi penangkapan untuk melihat perkiraan probabilitas.")

    col_poke, col_hp = st.columns([1.5, 1])
    
    with col_poke:
        pokemon_query = st.text_input("Nama/ID Pokémon Target", placeholder="Contoh: Pikachu atau 25")
        
    with col_hp:
        max_hp = st.number_input("Max HP Pokémon Target", min_value=1, value=50)
        current_hp = st.number_input("Current HP Pokémon Target", min_value=1, max_value=max_hp, value=min(25, max_hp))
        
    st.markdown("---")
    
    col_ball, col_status = st.columns(2)

    BALL_MULTIPLIERS = {
        "Poké Ball (x1.0)": 1.0,
        "Great Ball (x1.5)": 1.5,
        "Ultra Ball (x2.0)": 2.0,
        "Master Ball (x255)": 255.0, 
        "Quick Ball (x5.0 - Turn 1)": 5.0, 
        "Net Ball (x3.5 - Water/Bug)": 3.5, 
    }
    
    STATUS_MULTIPLIERS = {
        "None (x1.0)": 1.0,
        "Paralyzed, Poisoned, Burned (x1.5)": 1.5,
        "Asleep, Frozen (x2.5)": 2.5,
    }
    
    with col_ball:
        ball_selection = st.selectbox("Jenis PokéBall (B)", list(BALL_MULTIPLIERS.keys()))
        ball_multiplier = BALL_MULTIPLIERS[ball_selection]
        
    with col_status:
        status_selection = st.selectbox("Status Pokémon (S)", list(STATUS_MULTIPLIERS.keys()))
        status_multiplier = STATUS_MULTIPLIERS[status_selection]
        
    if st.button("Hitung Probabilitas Tangkapan", use_container_width=True):
        if not pokemon_query:
            st.error("Mohon masukkan Nama atau ID Pokémon.")
            return

        with st.spinner(f"Mencari data '{pokemon_query}'..."):
            pokemon_detail = get_pokemon_detail(pokemon_query.lower().strip())
            
            if not pokemon_detail:
                st.error(f"Pokémon '{pokemon_query}' tidak ditemukan di API.")
                return
            
            species_url = pokemon_detail['species']['url']
            species_data = fetch(species_url)

            if not species_data:
                st.error(f"Gagal memuat data spesies untuk {pokemon_detail['name'].title()}.")
                return
                
            base_catch_rate = species_data.get('capture_rate')

            if base_catch_rate is None:
                st.error(f"Base Catch Rate untuk {pokemon_detail['name'].title()} tidak tersedia.")
                return

            A = int(base_catch_rate) 
            H = current_hp
            M = max_hp
            B = ball_multiplier
            S = status_multiplier
            
            temp_a = ((3 * M - 2 * H) * A * B) / (3 * M)
            a = temp_a * S
            
            a = min(255.0, a) 
            catch_probability_simple = a / 255.0

            if a >= 255:
                final_chance_percent = 100.0
                st.success(f"🎉 **Tangkapan Dijamin Sukses!** (Catch Rate Modifikasi 'a' = {int(a)} ≥ 255)")
            else:
                final_chance_percent = catch_probability_simple * 100
                
                st.markdown(f"**Tingkat Tangkapan Modifikasi (a):** `{a:.2f}` (Maksimal 255)")
                st.markdown(f"**Probabilitas Tangkapan (Sederhana):** `{final_chance_percent:.2f}%`")
                
                if final_chance_percent >= 50:
                    st.success("Tingkat probabilitas yang tinggi!")
                elif final_chance_percent >= 20:
                    st.warning("Tingkat probabilitas sedang. Cobalah Ball yang lebih baik atau status!")
                else:
                    st.error("Tingkat probabilitas rendah. Coba kurangi HP atau gunakan Ball/Status yang lebih baik.")
            
            st.markdown("### Detail Analisis")
            st.write(f"• **Pokémon:** **{pokemon_detail['name'].title()}**")
            st.write(f"• **Base Catch Rate (A):** `{A}` (Skala 1-255)")
            st.write(f"• **Kondisi HP (H/M):** `{H}/{M}`")
            st.write(f"• **PokéBall Multiplier (B):** `{B}` ({ball_selection})")
            st.write(f"• **Status Multiplier (S):** `{S}` ({status_selection})")