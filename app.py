import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
import stripe
import pandas as pd
import re
from fpdf import FPDF
from datetime import datetime

# ==========================================
# 1. BASIS KONFIGURATION & DESIGN
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# CSS für Styling und UI-Elemente
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; font-size: 0.9em; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; transform: scale(1.02); }
    .legal-box { font-size: 0.85em; color: #334155; line-height: 1.5; background: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-top: 20px; }
    .faq-q { font-weight: bold; color: #1e3a8a; margin-top: 15px; display: block; }
    .faq-a { margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #cbd5e1; color: #475569; }
    .result-section { background-color: #ffffff; border-left: 5px solid #1e3a8a; padding: 15px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE & PARAMETER (Stripe/Admin)
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# Admin & Stripe Parameter Check
params = st.query_params
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        pack_val = int(params.get("pack", 0))
        st.session_state.credits += pack_val
        st.session_state.processed_sessions.append(params["session_id"])
        st.balloons()
        st.success(f"Erfolgreich geladen! +{pack_val} Scans.")
    except: pass

# ==========================================
# 3. FUNKTIONEN (OCR & KI)
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def extract_text(file):
    """Extrahiert Text aus PDF oder Bild."""
    text = ""
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            if len(text.strip()) < 20: # Falls PDF nur Bilder enthält
                images = convert_from_bytes(file.getvalue())
                for img in images:
                    text += pytesseract.image_to_string(img)
        else:
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
    except Exception as e:
        return f"Fehler bei der Texterkennung: {e}"
    return text

def analyze_letter(raw_text, lang, mode="Standard"):
    if len(raw_text.strip()) < 30: 
        return "FEHLER_UNSCHARF"
    
    intent = "Erstelle eine professionelle Antwort." if mode == "Standard" else "Erstelle einen rechtlich fundierten, harten WIDERSPRUCH gegen diesen Bescheid."
    
    sys_p = f"""Du bist Rechtsexperte. Sprache der Antwort: {lang}. 
    Analysiere das Dokument. Falls unleserlich, antworte NUR: FEHLER_UNSCHARF.
    Struktur:
    ### AMPEL ### (ROT, GELB oder GRÜN + kurze Begründung)
    ### GLOSSAR ### (3-4 Begriffe einfach erklärt)
    ### FRISTEN ### (Datum | Aktion | Dringlichkeit)
    ### ANTWORTBRIEF ### ({intent})
    ### CHECKLISTE ### (Versandhinweise)"""
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}]
        )
        return resp.choices[0].message.content
    except:
        return "KI-Fehler. Bitte erneut versuchen."

# ==========================================
# 4. SIDEBAR (LOGO, GUTHABEN, SPRACHE)
# ==========================================
with st.sidebar:
    # Logo Fix: Pfad muss im Root-Verzeichnis stimmen
    LOGO_PATH = "icon_final_blau.png"
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.title("🏛️ Amtsschimmel-Killer")

    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    st.divider()
    st.subheader("⚙️ Einstellungen")
    lang_choice = st.selectbox("Zielsprache der Analyse", [
        "🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", 
        "🇪🇸 Español", "🇫🇷 Français", "🇦🇱 Albanian", "🇮🇹 Italiano", 
        "🇳🇱 Nederlands", "🇸🇦 العربية", "🇺🇦 Українська"
    ])
    
    st.divider()
    st.subheader("💳 Guthaben aufladen")
    pkgs = [
        ("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"),
        ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"),
        ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")
    ]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small>✔ Einmalzahlung | KEIN ABO</small></a>', unsafe_allow_html=True)

# ==========================================
# 5. HAUPTBEREICH (TABS)
# ==========================================
t1, t2, t3, t4, t5 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ", "⚖️ Impressum", "🔒 Datenschutz"])

with t1:
    st.title("Brief hochladen & killen 🚀")
    
    u_col, a_col = st.columns([1, 1])
    
    with u_col:
        upload = st.file_uploader("Brief (PDF oder Foto) wählen:", type=['pdf', 'png', 'jpg', 'jpeg'])
        if upload:
            st.info("Dokument bereit zur Analyse.")

    with a_col:
        if upload and st.session_state.credits > 0:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🚀 ANALYSE STARTEN"):
                    with st.spinner("Lese Brief..."):
                        text_found = extract_text(upload)
                        res = analyze_letter(text_found, lang_choice, "Standard")
                        if "FEHLER_UNSCHARF" in res:
                            st.error("⚠️ Dokument unleserlich oder zu klein! Bitte lade ein schärferes Foto hoch. (Kein Abzug)")
                        else:
                            st.session_state.full_res = res
                            st.session_state.credits -= 1
                            st.rerun()
            with c2:
                if st.button("⚖️ WIDERSPRUCH"):
                    with st.spinner("Erstelle Widerspruch..."):
                        text_found = extract_text(upload)
                        res = analyze_letter(text_found, lang_choice, "Widerspruch")
                        if "FEHLER_UNSCHARF" in res:
                            st.error("⚠️ Dokument unleserlich! Bitte schärferes Foto nutzen. (Kein Abzug)")
                        else:
                            st.session_state.full_res = res
                            st.session_state.credits -= 1
                            st.rerun()
        elif upload and st.session_state.credits <= 0:
            st.warning("⚠️ Bitte lade zuerst Guthaben in der Sidebar auf.")

    if st.session_state.full_res:
        st.divider()
        st.subheader("Ergebnis der Analyse")
        st.markdown(st.session_state.full_res)
        if st.button("Neue Analyse"):
            st.session_state.full_res = ""
            st.rerun()

with t2:
    st.header("⚡ Schnell-Vorlagen")
    st.write("Hier findest du Standard-Vorlagen für häufige Fälle.")
    with st.expander("Antrag auf Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren, hiermit bitte ich um Fristverlängerung bis zum [Datum] für das Aktenzeichen [Nummer]...")
    with st.expander("Akteneinsicht beantragen"):
        st.code("Sehr geehrte Damen und Herren, hiermit beantrage ich gemäß § 25 SGB X Akteneinsicht...")

with t3:
    st.header("❓ FAQ - Hilfe")
    st.markdown('<span class="faq-q">Wie sicher sind meine Daten?</span>', unsafe_allow_html=True)
    st.markdown('<div class="faq-a">Ihre Daten werden nur temporär für die Analyse verarbeitet und nicht dauerhaft gespeichert.</div>', unsafe_allow_html=True)
    st.markdown('<span class="faq-q">Warum wurde mein Foto abgelehnt?</span>', unsafe_allow_html=True)
    st.markdown('<div class="faq-a">Achten Sie auf gute Beleuchtung und dass der Text plan liegt. Wenn die KI keinen Text erkennt, wird kein Credit abgezogen.</div>', unsafe_allow_html=True)

with t4:
    st.header("Impressum")
    st.markdown("""
    **Angaben gemäß § 5 TMG:**  
    Amtsschimmel-Killer  
    Musterstraße 1, 12345 Berlin  
    E-Mail: support@amtsschimmel-killer.de
    """)

with t5:
    st.header("Datenschutz")
    st.write("Wir nehmen den Schutz Ihrer Daten ernst. Alle hochgeladenen Dokumente werden nach der Sitzung gelöscht.")

# ==========================================
# 6. FOOTER
# ==========================================
st.sidebar.markdown(f"---")
st.sidebar.caption(f"© {datetime.now().year} Amtsschimmel-Killer")
