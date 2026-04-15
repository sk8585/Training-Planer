import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
import json

st.set_page_config(
    page_title="Fußball Training Planer",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Schönes dunkles Design
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stButton>button { background-color: #00CC96; color: black; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Fußball Training Planer")
st.markdown("**Mobil optimiert für Trainer – mit Pausen & Vorlagen**")

# Session State
if "exercises" not in st.session_state:
    st.session_state.exercises = pd.DataFrame(columns=["Übung", "Dauer (min)", "Sets", "Reps", "Beschreibung", "Fokus"])

# ==================== EINSTELLUNGEN ====================
st.sidebar.header("Einstellungen")
pause_min = st.sidebar.slider("Automatische Pause zwischen Übungen (Minuten)", 0, 5, 2)

# ==================== FUSSBALL-VORLAGEN ====================
st.sidebar.header("📚 Fußball-Vorlagen")
template = st.sidebar.selectbox("Vorlage laden", [
    "Keine",
    "✅ Komplettes Training (U12–U15)",
    "🔥 Aufwärmen & Activation",
    "🎯 Technik & Ballgefühl",
    "⚡ Koordination & Agilität",
    "🏟️ Taktik & Spielformen",
    "💪 Kondition / Schnelligkeit",
    "🧊 Abschluss + Cool-down"
])

if st.sidebar.button("Vorlage laden", type="primary"):
    templates = {
        "🔥 Aufwärmen & Activation": [
            ["Joggen mit Ball", 5, 1, "", "Leichtes Einlaufen", "Aufwärmen"],
            ["Dynamisches Dehnen", 6, 1, "", "Beine, Hüfte, Schultern", "Aufwärmen"],
            ["Einrennen mit Ball", 4, 1, "", "Kurze Pässe im Gehen", "Technik"],
            ["Koordinationsleiter", 8, 2, "6 Durchgänge", "", "Koordination"],
        ],
        "🎯 Technik & Ballgefühl": [
            ["Balljonglage", 6, 1, "Max. Versuche", "Rechts / Links / Wechsel", "Technik"],
            ["Passspiel in Gruppen", 10, 1, "", "2er oder 3er Gruppen", "Technik"],
            ["Dribbelparcours", 8, 3, "", "Slalom + Tempowechsel", "Technik"],
            ["Torschuss nach Pass", 12, 4, "8 Schüsse", "Von verschiedenen Positionen", "Abschluss"],
        ],
        "⚡ Koordination & Agilität": [
            ["Leiterübungen", 10, 4, "", "Verschiedene Varianten", "Koordination"],
            ["Hürden & Slalom", 8, 3, "", "Schnelle Füße", "Agilität"],
            ["Reaktionsübungen mit Ball", 7, 3, "", "Partner wirft Ball", "Koordination"],
        ],
        "🏟️ Taktik & Spielformen": [
            ["4 gegen 4 + 2 Neutrale", 15, 1, "", "Auf engem Raum", "Taktik"],
            ["Überzahlspiel 5 vs 3", 12, 2, "", "Kombinationsspiel", "Taktik"],
            ["Positionsspiel 6 vs 6", 18, 1, "", "Mit Torhütern", "Spielform"],
        ],
        "💪 Kondition / Schnelligkeit": [
            ["Sprintübungen", 10, 6, "20-30m", "Mit Ball zurückjoggen", "Schnelligkeit"],
            ["Intervall-Läufe", 12, 1, "8 Runden", "30 Sek. hoch / 30 Sek. locker", "Kondition"],
            ["Shuttle Runs", 8, 4, "", "Mit Richtungswechsel", "Schnelligkeit"],
        ],
        "🧊 Abschluss + Cool-down": [
            ["Abschlussspiel 5 vs 5", 15, 1, "", "Kleinfeld", "Spiel"],
            ["Locker auslaufen", 5, 1, "", "", "Regeneration"],
            ["Statisches Dehnen", 8, 1, "", "Team zusammen", "Cool-down"],
        ],
        "✅ Komplettes Training (U12–U15)": [
            ["Joggen mit Ball", 5, 1, "", "", "Aufwärmen"],
            ["Dynamisches Dehnen", 6, 1, "", "", "Aufwärmen"],
            ["Koordinationsleiter", 8, 2, "", "", "Koordination"],
            ["Dribbelparcours", 10, 3, "", "", "Technik"],
            ["Passspiel + Torschuss", 12, 1, "", "", "Technik"],
            ["4 vs 4 + 2", 15, 1, "", "", "Taktik"],
            ["Abschlussspiel 6 vs 6", 18, 1, "", "", "Spiel"],
            ["Locker auslaufen + Dehnen", 8, 1, "", "", "Cool-down"],
        ]
    }
    
    if template != "Keine":
        data = templates.get(template, [])
        new_df = pd.DataFrame(data, columns=["Übung", "Dauer (min)", "Sets", "Reps", "Beschreibung", "Fokus"])
        st.session_state.exercises = pd.concat([st.session_state.exercises, new_df], ignore_index=True)
        st.success(f"✅ Vorlage '{template}' geladen!")
        st.rerun()

# ====================== TABS ======================
tab1, tab2, tab3 = st.tabs(["➕ Übung hinzufügen", "📋 Plan bearbeiten", "📊 Zeitstrahl"])

with tab1:
    st.subheader("Neue Übung hinzufügen")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Übungsname *", placeholder="z.B. Dribbelparcours")
        duration = st.number_input("Dauer (Minuten)", min_value=1, value=8)
        sets = st.number_input("Durchgänge / Sätze", min_value=1, value=3)
    with col2:
        reps = st.text_input("Reps / Details", "z.B. 6 Durchgänge")
        focus = st.selectbox("Fokus", ["Aufwärmen", "Technik", "Koordination", "Taktik", "Kondition", "Spiel", "Cool-down"])
        desc = st.text_area("Beschreibung / Organisation", height=80)
    
    if st.button("➕ Hinzufügen", type="primary", use_container_width=True):
        if name:
            new_row = pd.DataFrame([{
                "Übung": name, 
                "Dauer (min)": duration, 
                "Sets": sets,
                "Reps": reps, 
                "Beschreibung": desc, 
                "Fokus": focus
            }])
            st.session_state.exercises = pd.concat([st.session_state.exercises, new_row], ignore_index=True)
            st.success("✅ Übung hinzugefügt!")
            st.rerun()

with tab2:
    if len(st.session_state.exercises) == 0:
        st.info("Noch keine Übungen. Lade eine Vorlage oder füge eigene hinzu.")
    else:
        edited = st.data_editor(
            st.session_state.exercises,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True
        )
        st.session_state.exercises = edited

        if st.button("🗑️ Gesamten Plan löschen"):
            st.session_state.exercises = pd.DataFrame(columns=["Übung", "Dauer (min)", "Sets", "Reps", "Beschreibung", "Fokus"])
            st.rerun()

with tab3:
    if len(st.session_state.exercises) > 0:
        df = st.session_state.exercises.copy()
        
        # Pausen automatisch einfügen
        if pause_min > 0 and len(df) > 1:
            pauses = []
            for i in range(len(df)-1):
                pauses.append({
                    "Übung": f"Pause ({pause_min} min)",
                    "Dauer (min)": pause_min,
                    "Sets": 0,
                    "Reps": "",
                    "Beschreibung": "",
                    "Fokus": "Pause"
                })
            pause_df = pd.DataFrame(pauses)
            df = pd.concat([df, pause_df]).sort_index(kind='merge')
        
        df["Start (min)"] = df["Dauer (min)"].cumsum().shift(1).fillna(0).astype(int)
        df["Ende (min)"] = df["Start (min)"] + df["Dauer (min)"]
        
        df["Von"] = df["Start (min)"].apply(lambda x: str(timedelta(minutes=x))[:-3])
        df["Bis"] = df["Ende (min)"].apply(lambda x: str(timedelta(minutes=x))[:-3])
        
        total = int(df["Dauer (min)"].sum())
        st.success(f"**Gesamtdauer inkl. Pausen: {str(timedelta(minutes=total))[:-3]}**")
        
        st.dataframe(
            df[["Übung", "Von", "Bis", "Dauer (min)", "Sets", "Fokus"]],
            use_container_width=True,
            hide_index=True
        )
        
        fig = px.timeline(
            df,
            x_start="Start (min)",
            x_end="Ende (min)",
            y="Übung",
            color="Fokus",
            title="⚽ Trainingszeitstrahl",
            color_discrete_sequence=["#00CC96", "#FF9F1C", "#4287f5", "#f54242", "#9f42f5", "#42f5b0", "#666666"]
        )
        fig.update_layout(height=520)
        st.plotly