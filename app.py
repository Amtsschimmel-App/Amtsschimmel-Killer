import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
import shutil
import stripe
import gc 

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")
LOGO_DATEI = "icon_final_blau.png"

# 2. STYLING
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { 
        text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; 
        border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s;
    }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; }
    .legal-footer { font-size: 0.75em; color: #94a3b8; margin-top: 50px; padding: 20px; border-top: 1px solid #e2e8f0; }
    .result-box { background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
stripe.api_key = st.secrets["STRIPE_API_KEY"]

# --- 4. SESSION STATE ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "last_brief" not in st.session_state: st.session_state.last_brief = ""
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""

# --- 5. DER POWER-PROMPT (KI-ANWEISUNG) ---
def generate_killer_response(raw_text):
    sys_prompt = """Du bist der 'Amtsschimmel-Killer'. Deine Aufgabe: Analysiere Behördenbriefe und erstelle eine perfekte Antwort.
    
    SCHRITT 1: ANALYSE
    - Wer schreibt? (Behörde/Amt)
    - Was wird gefordert? (Kernanliegen)
    - Welche Fristen gelten? (DATUM hervorheben!)
    
    SCHRITT 2: DER ANTWORTBRIEF
    - Tonfall: Hochprofessionell, bestimmt, juristisch präzise, aber höflich.
    - Struktur: Korrekter Briefkopf-Platzhalter, Betreffzeile mit Aktenzeichen (falls im Text gefunden).
    - Inhalt: Gehe direkt auf die Forderungen ein. Nutze Formulierungen wie 'unter Bezugnahme auf Ihr Schreiben vom...', 'bitte ich um Fristverlängerung bis zum...', 'lege ich hiermit Widerspruch ein'.
    - WICHTIG: Erstelle Platzhalter für [Name], [Adresse], [Aktenzeichen], falls diese nicht eindeutig im Scan erkannt wurden.
    
    FORMATIERUNG: Nutze Markdown für die Analyse und einen klaren Textblock für den Brief."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Hier ist der gescannte Text des Briefes:\n\n{raw_text}"}
        ],
        temperature=0.3 # Niedrige Temperatur für hohe Präzision
    )
    return response.choices[0].message.content

# --- 6. SIDEBAR (Pakete mit Einmalzahlung) ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    st.subheader("Guthaben aufladen")
    pkgs = [
        ("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"),
        ("🚀 Spar-Paket", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"),
        ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")
    ]
    for name, link, count, price in pkgs:
        st.markdown(f'''
            <a href="{link}" target="_blank" class="buy-button">
                <b>{name}</b> ({count})<br>
                <span style="color: #16a34a;">{price} | Einmalzahlung</span><br>
                <small>Kein Abo • Sofort nutzbar</small>
            </a>''', unsafe_allow_html=True)

# --- 7. HAUPTBEREICH ---
st.title("Amtsschimmel-Killer 📄🚀")
uploaded_file = st.file_uploader("Brief hochladen (PDF oder Bild)", type=['pdf', 'png', 'jpg', 'jpeg'])

if uploaded_file:
    if st.session_state.credits > 0:
        if st.button("🚀 Analyse & Antwortbrief jetzt generieren"):
            with st.spinner("KI liest den Behörden-Code..."):
                # (Hier käme deine get_text_hybrid Funktion rein)
                # Simulierter Text für dieses Beispiel:
                raw_text = "Dummy Text vom Scan" 
                
                result = generate_killer_response(raw_text)
                st.session_state.last_analysis = result
                st.session_state.credits -= 1
                st.rerun()
    else:
        st.error("Guthaben leer. Bitte wähle ein Paket in der Seitenleiste (Einmalzahlung).")

if st.session_state.last_analysis:
    st.markdown("### 📋 Deine Analyse & Antwort")
    st.markdown(f'<div class="result-box">{st.session_state.last_analysis}</div>', unsafe_allow_html=True)
    st.download_button("Brief als Text speichern", st.session_state.last_analysis, "antwortbrief.txt")

# --- 8. DATENSCHUTZ (AUSFÜHRLICH) ---
st.markdown('<div class="legal-footer"></div>', unsafe_allow_html=True)
with st.expander("⚖️ Rechtliche Informationen & Datenschutz (DSGVO)"):
    st.write("""
    **Datenschutzerklärung**
    
    **1. Verantwortlichkeit:** Diese Anwendung verarbeitet Daten lokal im Browser und über gesicherte API-Schnittstellen (OpenAI & Stripe).
    
    **2. Datenverarbeitung (Dokumente):** Ihre hochgeladenen Dokumente werden ausschließlich zur Textextraktion und Analyse verwendet. 
    - Die Daten werden per SSL-Verschlüsselung an OpenAI übertragen.
    - Es erfolgt **keine dauerhafte Speicherung** Ihrer Dokumente auf unseren Servern.
    - Nach Schließen der Browsersitzung werden alle temporären Daten im Arbeitsspeicher gelöscht.
    
    **3. Zahlungsabwicklung:** 
    Alle Transaktionen werden durch **Stripe Payments Europe, Ltd.** abgewickelt. Wir speichern zu keinem Zeitpunkt Kreditkartendaten oder Bankinformationen auf unseren eigenen Systemen. Es handelt sich bei allen Paketen um **Einmalzahlungen (Prepaid)**. Es entstehen keine automatischen Folgekosten (Abonnements).
    
    **4. Ihre Rechte:** 
    Sie haben das Recht auf Auskunft, Berichtigung und Löschung Ihrer Daten. Da wir keine Nutzerkonten mit Klarnamen führen, werden Ihre Daten lediglich über eine anonyme Session-ID zugeordnet.
    
    **5. Haftungsausschluss:**
    Die durch die KI generierten Texte stellen **keine Rechtsberatung** dar. Bitte prüfen Sie alle Antwortbriefe vor dem Versand auf sachliche Richtigkeit. Die Nutzung erfolgt auf eigene Gefahr.
    """)
