import requests
import re
import streamlit as st 

API_BASE = "https://pokeapi.co/api/v2"

def set_page_config_and_style():
    """Mengatur konfigurasi halaman Streamlit dan injeksi CSS kustom."""
    st.set_page_config(page_title="Pokédex", layout="wide", page_icon="🧭")

    st.markdown("""
<style>
/* Header & Kartu */
.header-title {font-size:36px; font-weight:800; color:#2b6cb0;}
.card {border:2px solid #2b6cb0; border-radius:12px; padding:14px; background:white;}
.type-badge {
    display:inline-block; padding:6px 10px; 
    border-radius:999px; margin-right:6px;
    font-weight:600; background:#e6f2ff;
}
.small {font-size:15px}

/* Sidebar fix: mencegah sidebar terlalu sempit pada layout */
section[data-testid="stSidebar"] {
    min-width: 300px !important;
    max-width: 320px !important;
}

/* Styling khusus halaman login (container, judul, subtitle) */
.login-container { text-align:center; padding:5px 50px; }
.title { color: #3B4CCA; font-weight: 800; font-size: 50px; margin-bottom: 5px; }
.subtitle { color: #333; font-size: 20px; margin-bottom: 5px; }

/* Gambar Pokémon dekoratif kiri/kanan pada halaman login */
.pokemon-left, .pokemon-right {
    position: fixed;
    top: 50%;
    transform: translateY(70%);
    z-index: 1;
}
.pokemon-left { left: 20%; width: 220px; }
.pokemon-right { right: 20%; width: 240px; }

/* Sembunyikan gambar dekoratif pada layar sempit (responsif) */
@media (max-width: 900px) {
    .pokemon-left, .pokemon-right { display: none; }
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600) 
def fetch(url):
    """Melakukan GET request ke URL yang diberikan."""
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

@st.cache_data(ttl=3600) 
def get_pokemon_detail(name_or_id):
    """Mengambil detail Pokémon dari endpoint /pokemon/{id or name}."""
    return fetch(f"{API_BASE}/pokemon/{name_or_id}")

@st.cache_data(ttl=3600)
def get_pokemon_species_data(name_or_id):
    """Mengambil data species untuk menemukan rantai evolusi."""
    return fetch(f"{API_BASE}/pokemon-species/{name_or_id}")

@st.cache_data(ttl=3600)
def get_evolution_chain_names(chain_url):
    """Mengambil semua nama Pokémon dalam satu rantai evolusi."""
    data = fetch(chain_url)
    if not data:
        return []
    
    names = []
    def extract_names_recursive(chain):
        species_name = chain['species']['name']
        names.append(species_name.title())
        for evolution in chain['evolves_to']:
            extract_names_recursive(evolution)

    if data.get('chain'):
        extract_names_recursive(data['chain'])
        
    return names

@st.cache_data(ttl=3600)
def get_type_damage_relations(type_name):
    """Mengambil hubungan damage dari tipe tertentu."""
    data = fetch(f"{API_BASE}/type/{type_name}")
    return data.get("damage_relations", {}) if data else {}

def _extract_id_from_species_url(url):
    """Mengambil ID numerik Pokémon dari URL species."""
    try:
        m = re.search(r"/pokemon-species/(\d+)/?$", url)
        if m:
            return int(m.group(1))
    except Exception:
        pass
    return None

@st.cache_data(ttl=3600)
def get_generation_range_from_api(gen_number):
    """Mengambil rentang ID Pokémon untuk sebuah generasi."""
    data = fetch(f"{API_BASE}/generation/{gen_number}")
    if not data:
        return None
    species = data.get("pokemon_species", [])
    ids = []
    for s in species:
        sid = _extract_id_from_species_url(s.get("url", ""))
        if sid:
            ids.append(sid)
    if not ids:
        return None
    return (min(ids), max(ids), len(ids), None)

@st.cache_data(ttl=3600)
def compute_weaknesses(types_list):

    multiplier = {}
    for t in types_list:
        rel = get_type_damage_relations(t)
        if not rel:
            continue
        for a in rel.get('double_damage_from', []):
            multiplier[a['name']] = multiplier.get(a['name'], 1) * 2
        for a in rel.get('half_damage_from', []):
            multiplier[a['name']] = multiplier.get(a['name'], 1) * 0.5
        for a in rel.get('no_damage_from', []):
            multiplier[a['name']] = 0
    return [k for k, v in multiplier.items() if v > 1]

def is_gmail(email: str) -> bool:
    """Validasi sederhana untuk memastikan email memakai domain @gmail.com."""
    return re.fullmatch(r'[a-zA-Z0-9._%+-]+@gmail\.com', email) is not None

def pokemon_card_html(detail, include_id=True):
    """Membangun potongan HTML untuk menampilkan kartu Pokémon."""
    name = detail['name'].title()
    num = detail['id']
    types = [t['type']['name'] for t in detail['types']]
    abilities = [a['ability']['name'] for a in detail['abilities']]
    artwork = detail['sprites'].get('other', {}).get('official-artwork', {}).get('front_default') \
              or detail['sprites'].get('front_default')
    weakness = compute_weaknesses(tuple(types)) 

    id_tag = f"<span class='small'>#{num:04d}</span>" if include_id else ""

    html = f"<div class='card'>"
    if artwork:
        html += f"<img src='{artwork}' width='220' style='display:block;margin:auto'/>"
    html += f"<div style='text-align:center;margin-top:8px'><strong>{name}</strong> {id_tag}</div>"
    html += "".join([f"<span class='type-badge'>{t.title()}</span>" for t in types])
    html += f"<div class='small' style='margin-top:8px'>Abilities: {', '.join(abilities)}</div>"
    html += f"<div class='small'>Weaknesses: {', '.join(weakness) if weakness else 'None'}</div>"
    html += "</div>"
    return html


@st.cache_data(ttl=86400)
def _get_evolution_chain_names(chain_data, names):
    """Menganalisis struktur rantai evolusi secara rekursif."""
    names.append(chain_data['species']['name'].title())
    
    for evo in chain_data['evolves_to']:
        _get_evolution_chain_names(evo, names)
    return names

@st.cache_data(ttl=86400)
def get_evolution_line_from_pokemon(pokemon_name):
    """Mengambil seluruh garis evolusi (semua nama) untuk nama Pokémon yang diberikan."""

    name_lower = pokemon_name.lower().split('-')[0]
    
    species_url = f"{API_BASE}/pokemon-species/{name_lower}"
    species_data = fetch(species_url)

    if not species_data or 'evolution_chain' not in species_data or not species_data.get('evolution_chain'):
        return [pokemon_name.title()] 
    
    chain_url = species_data['evolution_chain']['url']
    chain_data = fetch(chain_url)
    
    if not chain_data or 'chain' not in chain_data:
        return [pokemon_name.title()]
    
    names = []
    return _get_evolution_chain_names(chain_data['chain'], names)

def remove_evolutionary_duplicates(team_list):
    """
    Memfilter daftar Pokémon untuk memastikan hanya ada satu Pokémon per garis evolusi.
    Prioritas: Memilih evolusi tertinggi yang ada dalam daftar.
    """
    if not team_list:
        return []
    
    evo_groups = {}
    
    for pokemon_name in team_list:
        clean_name = pokemon_name.split('-')[0]

        ordered_evo_line = get_evolution_line_from_pokemon(clean_name)

        evo_line_identifier = tuple(ordered_evo_line) if ordered_evo_line else (pokemon_name,)
        
        if evo_line_identifier not in evo_groups:
            evo_groups[evo_line_identifier] = []

        if pokemon_name not in evo_groups[evo_line_identifier]:
            evo_groups[evo_line_identifier].append(pokemon_name)

    final_team = []
    
    for ordered_evo_line, pokemon_names_in_group in evo_groups.items():
        best_pokemon = None

        for evo_name_in_line in reversed(ordered_evo_line):

            matching_pokemon = [
                name 
                for name in pokemon_names_in_group 
                if name.split('-')[0].title() == evo_name_in_line 
            ]

            if matching_pokemon: 
                best_pokemon = matching_pokemon[0] 
                final_team.append(best_pokemon)
                break
        
    return final_team
