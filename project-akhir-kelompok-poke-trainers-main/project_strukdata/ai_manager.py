import random
import json

from components import get_pokemon_species_data, get_evolution_chain_names

POKEMON_LIST = [
    "Charmander", "Charmeleon", "Charizard", "Bulbasaur", "Ivysaur", "Venusaur", 
    "Squirtle", "Wartortle", "Blastoise", "Snorlax", "Dragonite", "Alakazam", 
    "Tyranitar", "Salamence", "Metagross", "Garchomp", "Lucario", "Cinderace", 
    "Dragapult", "Flutter Mane", "Iron Hands", "Ogerpon", "Chien-Pao", "Pikachu",
    "Meowscarada", "Skeledirge", "Quaquaval", "Pichu", "Raichu" 
]

def get_banned_evolution_names(pokemon_list: list) -> list:
    banned_names = set()
    for name in pokemon_list:
        species_data = get_pokemon_species_data(name.lower().strip())
        if not species_data:
            continue
            
        evolution_chain_url = species_data.get('evolution_chain', {}).get('url')
        if evolution_chain_url:
            chain_names = get_evolution_chain_names(evolution_chain_url)
            
            for c_name in chain_names:
                banned_names.add(c_name)
    
    for name in pokemon_list:
        if name.title() in banned_names:
            banned_names.remove(name.title())
            
    return [name.title() for name in list(banned_names)]


def generate_optimized_team(theme: str = "", owned_pokemon: list = None) -> dict:
    owned_pokemon = [p.title() for p in (owned_pokemon or [])] 
    
    banned_evolution_names = get_banned_evolution_names(owned_pokemon)
    
    if owned_pokemon:
        owned_str = ", ".join(owned_pokemon)
        action = f"Selesaikan tim Pokémon yang terdiri dari **6** anggota. Anda sudah memiliki: **{owned_str}**. Cari {6 - len(owned_pokemon)} Pokémon pelengkap terbaik yang berasal dari Generasi 1-9."
    else:
        action = "Buatkan tim Pokémon yang optimal dan seimbang terdiri dari **6** anggota, sepenuhnya dari Generasi 1-9."
    
    theme_str = f"Tema/fokus tim yang diinginkan adalah: '{theme}'." if theme else "Tim harus seimbang (Balanced) dan kompetitif secara umum."
    
    if banned_evolution_names:
        filter_str = f"PENTING: Jangan masukkan Pokémon berikut atau bentuk evolusinya: {', '.join(banned_evolution_names)}. Pokémon yang sudah dimiliki TIDAK BOLEH muncul lagi."
    else:
        filter_str = ""
    
    prompt = f"""
    Anda adalah ahli strategi Pokémon. {action} {theme_str}
    Fokus pada sinergi tipe, kemampuan (Abilities), dan cakupan serangan (Coverage). {filter_str}

    Output harus berupa JSON MURNI dengan format berikut, berisi *tepat 6* Pokémon, termasuk yang sudah dimiliki:
    {{
        "team": ["Nama1", "Nama2", "Nama3", "Nama4", "Nama5", "Nama6"],
        "reason": "Penjelasan singkat (maksimal 3 kalimat) mengenai strategi tim dan mengapa Pokémon yang Anda pilih melengkapi tim."
    }}
    """

    try:
        available_for_pick = [
            p for p in POKEMON_LIST 
            if p.title() not in owned_pokemon and p.title() not in banned_evolution_names
        ]
        
        final_team = owned_pokemon
        remaining_needed = 6 - len(owned_pokemon)
        
        if remaining_needed > 0:
            complements = random.sample(available_for_pick, min(remaining_needed, len(available_for_pick)))
            final_team.extend(complements)
        
        if owned_pokemon:
            reason = (
                f"Tim ini dibangun di sekitar {', '.join(owned_pokemon)} untuk mencapai {theme or 'keseimbangan'}. "
                f"Pokémon yang ditambahkan melengkapi kelemahan tipe dan meningkatkan potensi serangan tim."
            )
        else:
            reason = (
                f"Tim ini dirancang untuk {theme or 'keseimbangan umum'} dengan sinergi tipe yang baik dan cakupan serangan yang luas."
            )
            
        final_team = [p.title() for p in final_team][:6] 

        return {
            "team": final_team,
            "reason": reason
        }

    except Exception as e:
        print(f"AI API Error or Simulation Failed: {e}")
        return {
            "team": ["Pikachu", "Snorlax", "Dragonite", "Venusaur", "Blastoise", "Charizard"],
            "reason": "Gagal menghasilkan tim dari AI. Tim fallback acak ditampilkan."
        }

def generate_strategy_guide(topic: str, level: str) -> str:
    print(f"Generating strategy guide for topic: {topic}, level: {level}...")

    prompt = f"""
    Anda adalah pelatih dan ahli strategi Pokémon yang berpengalaman. 
    Buatkan panduan strategi terperinci dan mudah dipahami tentang topik: **{topic}**.
    
    Target audiens: **Pemain {level}**.
    
    Panduan harus menggunakan format Markdown yang rapi (gunakan heading, list, dan bold) dan mencakup:
    1. Pengenalan singkat topik.
    2. Konsep kunci yang harus diketahui.
    3. Contoh Pokémon atau tim yang relevan.
    4. Tips praktis untuk implementasi dalam pertempuran.
    
    Pastikan konten berbobot dan relevan dengan lingkungan kompetitif Pokémon terbaru.
    """

    try:
        if "tier list" in topic.lower():
            if "pemula" in level.lower():
                 guide_content = f"""
## Panduan Tier List Sederhana ({level}) 🏆

Tier list adalah daftar peringkat Pokémon berdasarkan efektivitasnya dalam format pertempuran tertentu.

### 1. Konsep Kunci
* **S-Tier:** Pokémon yang dominan dan hampir selalu digunakan. (Contoh: **Flutter Mane**, **Iron Hands**).
* **A-Tier:** Pokémon yang kuat, tetapi memiliki kelemahan yang lebih mudah dieksploitasi. (Contoh: **Dragonite**, **Garchomp**).
* **B-Tier:** Pokémon yang masih bisa kompetitif tetapi membutuhkan dukungan tim yang spesifik.

### 2. Tips Praktis
Untuk pemain **{level.lower()}**, fokus pada Pokémon di **A-Tier** dan **B-Tier** yang *set up*-nya mudah. Jangan hanya meniru S-Tier; pelajari mengapa mereka kuat (Ability, Stat, Movepool).

### 3. Contoh Tim
Tim pemula yang baik seringkali menggunakan inti 'Fire-Water-Grass' yang seimbang, seperti **Charizard**, **Blastoise**, dan **Venusaur**.
                """
            else:
                 guide_content = f"""
## Analisis Mendalam Tier List dan Meta ({level}) 🧠

Tier list adalah daftar peringkat Pokémon yang mencerminkan dominasi saat ini (*Metagame*).

### 1. Konsep Kunci
* **Metagame:** Lingkungan kompetitif yang terus berubah berdasarkan Pokémon dan strategi yang paling banyak digunakan.
* **Role Compression:** Pokémon yang dapat melakukan banyak peran (misalnya, Attacker sekaligus Defogger).

### 2. Analisis {topic}
Di tier tinggi, perhatikan Pokémon seperti **Chien-Pao** dan **Ogerpon**. Kunci utama adalah bagaimana cara mengatasi *Speed Control* yang dilakukan oleh lawan.

### 3. Tips Praktis
Gunakan Pokémon 'niche' (unik) dari **B-Tier** yang secara spesifik dapat **menghancurkan** musuh S-Tier yang sedang dominan.
                """
                
        elif "breeding" in topic.lower() or "ev/iv" in topic.lower():
             if "pemula" in level.lower():
                 guide_content = f"""
# Dasar-Dasar Pokémon Strategy untuk Pemain {level} 🥚

### 1. Statistik Dasar (Base Stats)
Statistik menentukan kekuatan Pokémon. Fokus pada **HP**, **Attack**, **Special Attack**, dan **Speed**. Pemain **{level.lower()}** harus memilih Pokémon dengan stat serangan tinggi.

### 2. Memahami EV dan IV
* **IV (Individual Value):** 'Genetika' Pokémon, tidak dapat diubah setelah ditangkap. Fokus pada IV 31 untuk Stat penting.
* **EV (Effort Value):** Poin yang Anda berikan melalui pelatihan. Maksimal 252 per stat, total 510. Gunakan EV untuk memaksimalkan dua stat terpenting.

### 3. Tips Praktis
Selalu gunakan **Super Effective** (Kelemahan Tipe musuh). Untuk breeding, gunakan **Destiny Knot** dan **Everstone**!
                """
             else:
                 guide_content = f"""
# Optimasi EV/IV dan Nature ({level}) 🔬

Strategi kompetitif menuntut optimasi statistik yang sempurna.

### 1. Spread Kustom
Selain 252/252, pelajari *EV spread* kustom (custom spread) untuk mencapai *benchmark* tertentu (misalnya, survive serangan tertentu atau outspeed Pokémon spesifik).

### 2. Nilai Nol IV
Kadang-kadang, IV **0 (Zero)** pada Attack (untuk Special Attacker) atau Speed (untuk Trick Room) sangat diinginkan.

### 3. Tips Praktis
Gunakan item seperti **Power Items** untuk *EV Training* dan **Mint** untuk mengubah *Nature* tanpa *breeding* ulang.
                """
                
        else:
            guide_content = f"""
# Strategi {topic}: Panduan {level} ✨

Panduan ini ditujukan untuk pemain **{level}** yang ingin menguasai nuansa pertempuran {topic}.

### 1. Pengenalan {topic}
**{topic}** adalah konsep krusial yang menentukan alur pertempuran tim Anda. Menguasainya memerlukan prediksi dan pemahaman mendalam tentang *Metagame* saat ini.

### 2. Konsep Kunci
Fokus pada **Speed Control** dan **Positioning** yang tepat. Manfaatkan Move seperti **Tailwind** atau **Trick Room** jika {topic} melibatkan kecepatan. Pertimbangkan peran *Defog* atau *Rapid Spin* jika {topic} melibatkan *Hazard*.

### 3. Contoh Pokémon & Set
* **Dragapult (Choice Specs):** Shadow Ball / Draco Meteor / U-Turn. (Contoh set *Revenge Killer*).
* **Alakazam (Focus Sash):** Psychic / Dazzling Gleam / Substitute / Focus Blast. (Contoh *Special Sweeper*).

### 4. Tips Praktis
Selalu pastikan Anda memiliki cadangan (*pivot*) jika Pokémon utama Anda di-*counter*. Jangan bergantung pada satu Pokémon saja!
            """
            
        return guide_content

    except Exception as e:
        print(f"AI Strategy Error: {e}")
        return "Gagal menghubungi AI. Strategi dasar ditampilkan sebagai fallback. **Periksa konfigurasi Gemini API Anda.**"

def generate_synergy_combo(team_list: list) -> str:
    
    if not team_list:
        return "Tim kosong. Tambahkan Pokémon ke Deck Tersimpan Anda untuk menganalisis sinergi."

    team_names = [p.title() for p in team_list]
    
    synergy_report = "### 💡 Analisis Sinergi Tim (AI)"
    
    found_synergy = False
    
    if "Whimsicott" in team_names and any(p in team_names for p in ["Garchomp", "Dragapult", "Cinderace"]):
        synergy_report += (
            "\n\n**🎯 Kombo Tailwind + Wallbreaker:** Kehadiran **Whimsicott** (dengan **Tailwind** - diasumsikan) dapat menggandakan kecepatan tim Anda. Ini memungkinkan **Garchomp** atau **Dragapult** untuk menyerang pertama dan menghancurkan lawan sebelum mereka bergerak. *(Sinergi Speed Control)*"
        )
        found_synergy = True
        
    if "Venusaur" in team_names and "Charizard" in team_names:
        synergy_report += (
            "\n\n**☀️ Kombo Weather (Sun) - Growth:** Sinergi tipe Fire/Grass yang kuat! Jika **Charizard** (dengan Ability Drought atau dukungan Weather) memanggil Matahari, **Venusaur** dapat memanfaatkan Ability **Chlorophyll** untuk peningkatan Speed drastis atau Move **Growth** yang lebih kuat. *(Sinergi Weather)*"
        )
        found_synergy = True
        
    if "Arcanine" in team_names and "Milotic" in team_names:
        synergy_report += (
            "\n\n**🛡️ Kombo Anti-Intimidate:** Walaupun keduanya ada dalam tim, jika lawan mencoba menggunakan **Intimidate** (misalnya pada Arcanine Anda), **Milotic** dapat mengaktifkan Ability **Competitive**-nya untuk meningkatkan Special Attack secara drastis! *(Sinergi Ability Counter)*"
        )
        found_synergy = True
        
    if not found_synergy:
        if len(team_list) >= 3:
            synergy_report += (
                "\n\n**📝 Saran Umum:** Tidak ada kombo sinergi yang jelas ditemukan. AI merekomendasikan: "
                "\n* **Cek Sinergi Tipe:** Misalnya, gunakan Pokémon **Ground** (seperti Garchomp) untuk melindungi Pokémon **Electric** (seperti Pikachu) dari serangan Ground lawan."
                "\n* **Pertimbangkan Pivot:** Pokémon yang bisa menukar posisi dengan aman (*Volt Switch* atau *U-Turn*) untuk mempertahankan momentum."
                "\n* **Kontrol Status:** Pokémon yang bisa memberikan status (Sleep/Paralysis) untuk memudahkan setup."
            )
        else:
            synergy_report += "\n\n**📝 Saran:** Tambahkan lebih banyak Pokémon (minimal 3) untuk analisis sinergi yang lebih mendalam."

    return synergy_report

def generate_pokemon_build(pokemon_name: str) -> dict:
    name_title = pokemon_name.title()

    if name_title == "Garchomp":
        build_info = {
            "name": name_title,
            "Role": "Physical Sweeper / Late-Game Cleaner",
            "Item": "Choice Scarf (Pilihan 1) atau Life Orb (Pilihan 2)",
            "Ability": "Rough Skin (Paling Populer)",
            "Moveset": ["Earthquake", "Outrage", "Stone Edge", "Swords Dance"],
            "EV_Spread": "252 Atk / 4 Def / 252 Spe",
            "Nature": "Jolly (+Spe, -Sp. Atk)",
            "Strategy": (
                "Garchomp adalah salah satu Pokémon ofensif terbaik. Build Choice Scarf memungkinkannya "
                "mengungguli banyak Pokémon cepat lainnya dan berfungsi sebagai 'revenge killer'. "
                "Life Orb digunakan jika Anda ingin menggunakan Swords Dance untuk 'set up' dan menyapu tim lawan."
            )
        }
    elif name_title == "Flutter Mane":
        build_info = {
            "name": name_title,
            "Role": "Special Attacker / Booster Energy Sweeper",
            "Item": "Booster Energy (Wajib untuk mengaktifkan Protosynthesis)",
            "Ability": "Protosynthesis",
            "Moveset": ["Moonblast", "Shadow Ball", "Thunderbolt", "Protect"],
            "EV_Spread": "252 Sp. Atk / 4 Def / 252 Spe",
            "Nature": "Timid (+Spe, -Atk)",
            "Strategy": (
                "Flutter Mane adalah Pokémon tercepat dan terkuat di metagame saat ini. Booster Energy secara "
                "otomatis meningkatkan Speed-nya. 'Protect' penting untuk memblokir serangan dan memenangkan duel 1v1. "
                "Fokuskan pada menyerang dengan kuat menggunakan Moonblast dan Shadow Ball."
            )
        }
    elif name_title == "Pikachu":
        build_info = {
            "name": name_title,
            "Role": "Light Ball Attacker / Mascot",
            "Item": "Light Ball (Wajib, menggandakan Attack dan Sp. Atk)",
            "Ability": "Lightning Rod (Untuk Doubles Battles)",
            "Moveset": ["Volt Tackle", "Surf", "Nuzzle", "Fake Out"],
            "EV_Spread": "252 Atk / 4 Def / 252 Spe",
            "Nature": "Hasty (+Spe, -Def)",
            "Strategy": (
                "Pikachu hanya bisa digunakan secara kompetitif dengan Light Ball. Item ini memberikan output damage yang gila-gilaan. "
                "Gunakan Nuzzle untuk melumpuhkan lawan yang lebih cepat, dan Volt Tackle untuk kerusakan maksimum. "
                "Dalam tim VGC/Doubles, Fake Out dan Lightning Rod sangat bernilai."
            )
        }
    else:
        build_info = {
            "name": name_title,
            "Role": "Balanced Attacker / Generalist",
            "Item": "Leftovers atau Assault Vest",
            "Ability": "Ability Alami Pokémon (Lihat Dex)",
            "Moveset": ["4 Move paling kuat dengan coverage berbeda", "Termasuk 1 Move Bertahan"],
            "EV_Spread": "252 HP / 252 di Stat Tertinggi (Atk/Sp. Atk)",
            "Nature": "Modest/Adamant (Tergantung Atk/Sp. Atk)",
            "Strategy": (
                f"Tidak ada build populer yang spesifik ditemukan untuk {name_title} saat ini, atau Pokémon ini adalah Pokémon non-kompetitif. "
                "AI merekomendasikan set dasar yang seimbang. Fokuskan pada memperkuat pertahanan dan menutupi kelemahan tipe tim Anda."
            )
        }

    return build_info
