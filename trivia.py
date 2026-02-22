import streamlit as st
import pandas as pd
import random
import glob
import re
import os

st.set_page_config(page_title="Jeopardy! Pro Trainer", page_icon="🎓", layout="centered")

# --- 1. STUDY TAG ENGINE ---

# PASS 1: Match against the Jeopardy category string directly.
# These patterns are designed to catch explicit, unambiguous category names.
CATEGORY_MAP = {
    "U.S. Presidents":       r"president|oval office|commander.in.chief|first ladies|first lady",
    "American History":      r"american history|u\.s\. history|us history|civil war|revolutionary war|colonial|founding father|constitution|declaration of independence|westward|manifest destiny|reconstruction",
    "World History":         r"world history|ancient history|ancient rome|ancient greece|medieval|renaissance|french revolution|world war|wwi|wwii|cold war|ottoman|byzantine|ming|dynasty",
    "Geography":             r"capital|capitals|country|countries|nation|nations|continent|river|mountain|lake|ocean|sea|island|peninsula|border|flag|flags|map",
    "U.S. Geography":        r"u\.s\. state|state capital|american city|american state|U\.S\. city|U\.S\. geography",
    "Science & Nature":      r"science|biology|chemistry|physics|astronomy|space|planet|element|periodic|animal|mammal|bird|reptile|insect|plant|botany|ecology|geology|weather|climate|human body|anatomy|cell",
    "Mathematics":           r"math|algebra|geometry|calculus|equation|number|fraction|prime|theorem",
    "Literature":            r"literature|novel|author|poet|poetry|fiction|nonfiction|book|books|pulitzer|nobel.*literature|short story|play|playwright|shakespeare|dickens|twain|hemingway|fitzgerald|tolkien",
    "Shakespeare":           r"shakespeare|bard|hamlet|macbeth|othello|lear|midsummer|tempest|romeo|juliet",
    "Mythology":             r"myth|mythology|greek god|roman god|norse|olympus|zeus|thor|odin|hercules|legend|folklore",
    "Religion & Philosophy": r"religion|bible|biblical|church|christian|islam|muslim|hindu|buddhis|jewish|judaism|theology|philosophy|philosopher|ethics|plato|aristotle|socrates",
    "Art & Architecture":    r"art|artist|painting|sculpture|architect|architecture|museum|gallery|renaissance art|impressi|cubis|modernist|van gogh|picasso|monet|da vinci|michelangelo",
    "Music":                 r"music|composer|symphony|opera|jazz|blues|rock|classical music|beethoven|mozart|bach|pop music|song|singer|band|album|grammy",
    "Film & TV":             r"movie|film|oscar|cinema|actor|actress|director|television|tv show|sitcom|emmy|box office|hollywood|animated",
    "Pop Culture":           r"pop culture|celebrity|reality tv|viral|meme|internet|social media|fashion|trend",
    "Sports":                r"sport|football|basketball|baseball|soccer|tennis|golf|hockey|olympics|nfl|nba|mlb|nhl|athlete|championship|world series|super bowl|world cup",
    "Food & Drink":          r"food|cuisine|cooking|chef|recipe|ingredient|wine|beer|cocktail|beverage|dish|restaurant|gastron",
    "Business & Economics":  r"business|economy|economics|stock|market|finance|company|corporation|ceo|entrepreneur|trade|gdp|inflation|bank|currency",
    "Language & Words":      r"word|words|language|grammar|etymology|vocabulary|latin|french word|spanish word|prefix|suffix|anagram|rhyme|spelling",
    "Potpourri":             r"potpourri|hodgepodge|miscellan|grab bag",
}

# PASS 2: Fall back to matching against clue text + category string combined.
# Same tags, broader/looser patterns for content that slipped past pass 1.
CONTENT_MAP = {
    "U.S. Presidents":       r"\bpresident\b|white house|potus|lincoln|washington|jefferson|roosevelt|kennedy|reagan|obama|clinton|trump|biden",
    "American History":      r"civil war|revolutionary|declaration of independence|gettysburg|emancipation|constitution|pilgrims|manifest destiny|lewis and clark",
    "World History":         r"world war|napoleon|julius caesar|roman empire|greek empire|feudal|crusade|colonialism|slavery|holocaust|cold war",
    "Geography":             r"\bcapital\b|mountain range|river delta|archipelago|strait|peninsula|equator|hemisphere|longitude|latitude",
    "U.S. Geography":        r"\bstate\b.*\bu\.?s\.?\b|\bu\.?s\.?\b.*\bstate\b|appalachian|mississippi river|grand canyon|yellowstone|mount rushmore",
    "Science & Nature":      r"molecule|atom|nucleus|species|evolution|dna|rna|protein|enzyme|photosynthesis|orbit|galaxy|black hole|periodic table",
    "Mathematics":           r"\bequation\b|\btheorem\b|\bprime number\b|pythagorean|fibonacci|calculus|integer|polynomial",
    "Literature":            r"\bnovel\b|\bpoem\b|\bpoet\b|\bauthor\b|literary|prose|sonnet|stanza|narrative|protagonist|antagonist",
    "Shakespeare":           r"shakespeare|hamlet|macbeth|othello|falstaff|iago|prospero|oberon|titania",
    "Mythology":             r"\bmyth\b|\bgod\b|\bgoddess\b|zeus|hera|apollo|athena|poseidon|thor|loki|odin|hercules|medusa|minotaur",
    "Religion & Philosophy": r"\bbible\b|\bprayer\b|\bmonk\b|\btemple\b|\bmosque\b|\bcathedral\b|\bpope\b|buddha|allah|torah|quran|karma|nirvana",
    "Art & Architecture":    r"\bpainting\b|\bsculpture\b|\bcanvas\b|\bmural\b|\barchitect\b|louvre|sistine|fresco|baroque|gothic arch",
    "Music":                 r"\bsymphony\b|\bopera\b|\bchord\b|\bmelody\b|\brhythm\b|\blyric\b|\borchestra\b|beethoven|mozart|bach",
    "Film & TV":             r"\bfilm\b|\bmovie\b|\bdirector\b|\bactor\b|\bactress\b|\boscars?\b|\bcinema\b|\bscreenplay\b",
    "Pop Culture":           r"\bcelebrity\b|\bviral\b|\bfashion\b|\btrendz?\b|\binstagram\b|\bsocial media\b",
    "Sports":                r"\bcoach\b|\bchampionship\b|\bleague\b|\btournament\b|\bathletes?\b|\bplayoff\b|\bworld cup\b|\bsuper bowl\b",
    "Food & Drink":          r"\brecipe\b|\bingredient\b|\bcuisine\b|\bflavou?r\b|\bbaked\b|\bgrilled\b|\bwine\b|\bcocktail\b",
    "Business & Economics":  r"\bstock market\b|\bwallstreet\b|\bceo\b|\bcorporat\b|\bmerger\b|\bgdp\b|\btariff\b|\btrade deal\b",
    "Language & Words":      r"\betymology\b|\bsynonym\b|\bantonym\b|\bprefix\b|\bsuffix\b|\bgrammar\b|\bverb\b|\bnoun\b|\badjective\b",
}

ALL_TAGS = list(CATEGORY_MAP.keys()) + ["Other"]

def identify_universal_cat(row):
    category = str(row.get('category', '')).lower()
    clue_text = str(row.get('answer', '')).lower()
    combined = f"{category} {clue_text}"

    # Pass 1: category string only
    for label, pattern in CATEGORY_MAP.items():
        if re.search(pattern, category):
            return label

    # Pass 2: combined category + clue content
    for label, pattern in CONTENT_MAP.items():
        if re.search(pattern, combined):
            return label

    return "Other"

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .category-box {
        background-color: #060ce9;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
    }
    .category-text {
        font-family: 'Arial Black', sans-serif;
        font-weight: bold;
        font-size: 28px;
        text-transform: uppercase;
    }
    div.stButton > button:first-child {
        background-color: #475569 !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING (SEASON CAPTURE) ---
@st.cache_data
def load_all_seasons():
    files = glob.glob("*.tsv")
    if not files:
        return None
    
    all_chunks = []
    for f in files:
        try:
            temp_df = pd.read_csv(f, sep='\t', low_memory=False)
            s_match = re.search(r'\d+', f)
            temp_df['season'] = s_match.group() if s_match else "??"
            all_chunks.append(temp_df)
        except:
            continue
            
    if not all_chunks:
        return None
    
    df = pd.concat(all_chunks, ignore_index=True)
    return df.dropna(subset=['answer', 'question']).sample(frac=1).reset_index(drop=True)

df = load_all_seasons()

# --- 4. STATE MANAGEMENT ---
if 'stats' not in st.session_state:
    st.session_state.stats = {cat: {"correct": 0, "total": 0} for cat in ALL_TAGS}

if 'idx' not in st.session_state:
    st.session_state.idx = 0
    st.session_state.show = False
    st.session_state.current_tag = "Other"
    st.session_state.initialized = False

def get_next():
    if df is not None:
        st.session_state.idx = random.randint(0, len(df) - 1)
        st.session_state.show = False
        row = df.iloc[st.session_state.idx]
        st.session_state.current_tag = identify_universal_cat(row)
        st.session_state.initialized = True

# --- 5. MAIN UI ---
if df is None:
    st.error("No .tsv files found in the folder!")
else:
    if not st.session_state.initialized:
        get_next()

    clue = df.iloc[st.session_state.idx]
    u_cat = st.session_state.current_tag

    st.markdown(f'<div class="category-box"><div class="category-text">{clue["category"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f"### {clue['answer']}")
    st.caption(f"Tag: **{u_cat}** | Season {clue['season']} | ${clue.get('clue_value', 400)}")

    if not st.session_state.show:
        if st.button("REVEAL RESPONSE", use_container_width=True):
            st.session_state.show = True
            st.rerun()
    else:
        st.success(f"RESPONSE: {str(clue['question']).upper()}")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ I GOT IT", use_container_width=True):
                st.session_state.stats[u_cat]["correct"] += 1
                st.session_state.stats[u_cat]["total"] += 1
                get_next()
                st.rerun()
        with c2:
            if st.button("❌ I MISSED IT", use_container_width=True):
                st.session_state.stats[u_cat]["total"] += 1
                get_next()
                st.rerun()

# --- 6. SIDEBAR (WEAKNESS TRACKER & REFRESH) ---
st.sidebar.title("📊 Training Progress")

total_correct = sum(d["correct"] for d in st.session_state.stats.values())
total_seen = sum(d["total"] for d in st.session_state.stats.values())
st.sidebar.metric("Total Correct", f"{total_correct} / {total_seen}")

st.sidebar.divider()
st.sidebar.subheader("Weakness Tracker")
for cat, data in st.session_state.stats.items():
    if data["total"] > 0:
        acc = (data["correct"] / data["total"]) * 100
        st.sidebar.write(f"**{cat}**")
        st.sidebar.progress(acc / 100)
        st.sidebar.caption(f"{acc:.0f}% accuracy ({data['total']} clues)")

st.sidebar.divider()
if st.sidebar.button("🔄 REFRESH ALL STATS", use_container_width=True):
    st.session_state.stats = {cat: {"correct": 0, "total": 0} for cat in ALL_TAGS}
    st.rerun()
