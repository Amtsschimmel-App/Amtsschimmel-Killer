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
from datetime import datetime
import gc 

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")
LOGO_DATEI = "icon_final_blau.png"

# 2. DESIGN & STYLING
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { 
        text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; 
        border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s;
    }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; scale: 1.02; }
    .step-box { background: #eff6ff; padding: 15px; border-radius: 10px; border: 1px solid #bfdbfe; text-align: center; }
    .legal-box { font-size: 0.85em; color: #475569; line-height: 1.5; background: #f8fafc; padding: 15px; border-radius: 8px; }
    .result-box { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 10px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 4. SESSION STATE ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""

# --- 5. SIDEBAR (Guthaben & Pakete) ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    st.divider()
    st.subheader("Guthaben aufladen")
    pkgs = [
        ("📄 Basis-Paket", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"),
        ("🚀 Spar-Paket", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"),
        ("💎 Profi-Paket", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")
    ]
    for name, link, count, price in pkgs:
        st.markdown(f'''
            <a href="{link}" target="_blank" class="buy-button">
                <b>{name}</b><br>
                <span style="color: #16a34a;">{price} | {count}</span><br>
                <small>✔ Einmalzahlung | Kein Abo</small>
            </a>''', unsafe_allow_html=True)

# --- 6. HAUPTBEREICH ---
tab1, tab2, tab3 = st.tabs(["🚀 Brief-Killer", "⚡ Sofort-Antworten", "❓ FAQ & Hilfe"])

with tab1:
    st.title("Amtsschimmel-Killer 📄🚀")
    
    # SCHRITT-ANLEITUNG
    s1, s2, s3 = st.columns(3)
    with s1: st.markdown('<div class="step-box"><b>1. Guthaben wählen</b><br><small>Paket links in der Sidebar buchen (Einmalzahlung).</small></div>', unsafe_allow_html=True)
    with s2: st.markdown('<div class="step-box"><b>2. Brief hochladen</b><br><small>Foto oder PDF deines Behördenbriefs auswählen.</small></div>', unsafe_allow_html=True)
    with s3: st.markdown('<div class="step-box"><b>3. Antwort kopieren</b><br><small>KI-Vorschlag prüfen, kopieren & abschicken.</small></div>', unsafe_allow_html=True)
    
    st.divider()

    # Reset-Funktion
    if st.session_state.last_analysis:
        if st.button("🔄 Nächsten Brief bearbeiten"):
            st.session_state.last_analysis = ""
            st.rerun()

    # Upload-Bereich
    if not st.session_state.last_analysis:
        st.subheader("Hier Brief hochladen:")
        upload = st.file_uploader("", type=['pdf', 'png', 'jpg', 'jpeg'])
        
        if upload:
            if st.session_state.credits > 0:
                if st.button("🚀 Analyse starten"):
                    with st.spinner("Amtsschimmel wird vertrieben..."):
                        # Hier die reale KI-Logik (generate_killer_response) aufrufen
                        st.session_state.last_analysis = "Hier stünde der KI-Antwortbrief basierend auf deinem Scan..." 
                        st.session_state.credits -= 1
                        st.rerun()
            else:
                st.error("Guthaben leer. Bitte wähle zuerst ein Paket in der Seitenleiste (Einmalzahlung).")

    # Ergebnis-Anzeige
    if st.session_state.last_analysis:
        st.success("Analyse abgeschlossen!")
        st.markdown(f'<div class="result-box">{st.session_state.last_analysis}</div>', unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📲 Text kopieren & speichern")
        st.info("Klicke rechts oben im grauen Feld auf das Klemmbrett-Symbol, um den Text zu kopieren.")
        st.code(st.session_state.last_analysis, language="text")
        
        st.download_button(
            label="💾 Als .txt Datei herunterladen",
            data=st.session_state.last_analysis,
            file_name=f"antwortbrief_{datetime.now().strftime('%d%m%Y')}.txt",
            mime="text/plain"
        )

with tab2:
    st.subheader("⚡ Sofort-Antworten")
    st.info("Kopiere diese Vorlagen direkt für schnelle Reaktionen:")
    with st.expander("⏳ Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren,\nin der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist bis zum [Datum].\n\nMit freundlichen Grüßen,\n[Name]", language="text")
    with st.expander("🛑 Widerspruch"):
        st.code("Sehr geehrte Damen und Herren,\ngegen den Bescheid vom [Datum] lege ich hiermit Widerspruch ein.\n\nMit freundlichen Grüßen,\n[Name]", language="text")

with tab3:
    st.subheader("Häufig gestellte Fragen (FAQ)")
    faqs = {
        "Ist das ein Abo?": "Nein. Jede Zahlung ist eine Einmalzahlung für die gewählte Anzahl an Scans.",
        "Datenschutz?": "Dateien werden per SSL übertragen und nach der Analyse sofort gelöscht.",
        "Rechtsberatung?": "Diese App ist eine Formulierungshilfe und ersetzt keinen Anwalt."
    }
    for q, a in faqs.items():
        st.markdown(f"**{q}**")
        st.write(a)

# --- 7. FOOTER (Impressum & Datenschutz) ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    with st.expander("🏢 Impressum"):
        st.markdown(f"""<div class="legal-box"><b>Betreiberin:</b> Elisabeth Reinecke, Ringelsweide 9, 40223 Düsseldorf.<br><b>Kontakt:</b> +49 211 15821329 | amtsschimmel-killer@proton.me<br><b>Web:</b> <a href="https://amtsschimmel-killer.streamlit.app">amtsschimmel-killer.streamlit.app</a></div>""", unsafe_allow_html=True)
with c2:
    with st.expander("⚖️ Datenschutz"):
        st.markdown(f"""<div class="legal-box"><b>Verantwortlich:</b> Elisabeth Reinecke.<br>Daten werden verschlüsselt verarbeitet und nicht dauerhaft gespeichert. Zahlungen erfolgen sicher über Stripe.</div>""", unsafe_allow_html=True)
