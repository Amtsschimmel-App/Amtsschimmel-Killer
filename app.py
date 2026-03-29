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

# 2. DESIGN (CSS)
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
    .legal-box { font-size: 0.85em; color: #334155; line-height: 1.6; background: #f1f5f9; padding: 25px; border-radius: 10px; border: 1px solid #cbd5e1; }
    .step-box { background: #eff6ff; padding: 15px; border-radius: 10px; border: 1px solid #bfdbfe; text-align: center; min-height: 100px; }
    </style>
    """, unsafe_allow_html=True)

# 3. SESSION STATE & ADMIN LOGIK (999 GUTHABEN FIX)
if "credits" not in st.session_state:
    st.session_state.credits = 0
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = ""

# --- ADMIN FREISCHALTUNG (ERZWUNGEN) ---
# WICHTIG: Die URL muss exakt so aussehen: 
# https://amtsschimmel-killer.streamlit.app!
try:
    query_params = st.query_params
    if "admin" in query_params and query_params["admin"] == "GeheimAmt2024!":
        st.session_state.credits = 999
        st.toast("🔓 ADMIN-MODUS AKTIV: 999 Scans freigeschaltet")
except Exception as e:
    pass

# 4. API INITIALISIERUNG
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("Guthaben aufladen")
    try:
        pkgs = [
            ("📄 Basis-Paket", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"),
            ("🚀 Spar-Paket", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"),
            ("💎 Profi-Paket", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")
        ]
        for name, link, count, price in pkgs:
            st.markdown(f'''<a href="{link}" target="_blank" class="buy-button"><b>{name}</b><br>{price} | {count}<br><small style="color: #16a34a;">✔ Einmalzahlung | Kein Abo</small></a>''', unsafe_allow_html=True)
    except: st.error("Fehler: Stripe-Links nicht konfiguriert.")

# --- 6. HAUPTBEREICH ---
t1, t2, t3 = st.tabs(["🚀 Brief-Killer", "⚡ Sofort-Antworten", "❓ FAQ & Hilfe"])

with t1:
    st.title("Amtsschimmel-Killer 📄🚀")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="step-box"><b>1. Guthaben</b><br><small>Paket links wählen.<br>Kein Abo.</small></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="step-box"><b>2. Upload</b><br><small>Brief hochladen.<br>PDF oder Foto.</small></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="step-box"><b>3. Antwort</b><br><small>Text kopieren &<br>verschicken.</small></div>', unsafe_allow_html=True)
    
    st.divider()

    if st.session_state.last_analysis:
        if st.button("🔄 Nächsten Brief bearbeiten"):
            st.session_state.last_analysis = ""
            st.rerun()

    if not st.session_state.last_analysis:
        st.info("💡 **Sicherheit:** Schwärze private Daten vor dem Upload. Aktenzeichen sollten lesbar bleiben.")
        upload = st.file_uploader("Behördenbrief wählen", type=['pdf', 'png', 'jpg', 'jpeg'])
        if upload and st.session_state.credits > 0:
            if st.button("🚀 Analyse starten"):
                with st.spinner("Amtsschimmel wird vertrieben..."):
                    # Simulierter Erfolg (Reale Logik hier einfügen)
                    st.session_state.last_analysis = "Sehr geehrte Damen und Herren,\n\nhiermit nehme ich Bezug auf Ihr Schreiben..." 
                    st.session_state.credits -= 1
                    st.rerun()
        elif upload: st.error("Guthaben leer. Bitte Paket in der Sidebar wählen.")

    if st.session_state.last_analysis:
        st.success("Analyse abgeschlossen!")
        st.code(st.session_state.last_analysis, language="text")
        st.download_button("💾 Download als Textdatei", st.session_state.last_analysis, "antwortbrief.txt")

with t2:
    st.subheader("⚡ Sofort-Antworten")
    with st.expander("⏳ Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren,\nin der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist bis zum [Datum]...", language="text")

with t3:
    st.subheader("❓ Häufig gestellte Fragen (FAQ)")
    faqs = [
        ("Ist das wirklich kein Abo?", "Ja. Jede Zahlung ist eine Einmalzahlung. Es gibt keine automatische Verlängerung."),
        ("Datensicherheit?", "Dokumente werden verschlüsselt verarbeitet und nach der Analyse sofort gelöscht."),
        ("Rechtsberatung?", "Nein. Die App ist eine Formulierungshilfe und kein Ersatz für einen Anwalt.")
    ]
    for q, a in faqs:
        st.markdown(f"**{q}**\n\n{a}")

# --- 7. FOOTER (VOLLES IMPRESSUM & LANGER DATENSCHUTZ) ---
st.divider()
col_imp, col_dat = st.columns(2)

with col_imp:
    with st.expander("🏢 Impressum"):
        st.markdown(f"""
        <div class="legal-box">
        <strong>Angaben gemäß § 5 TMG:</strong><br>
        Elisabeth Reinecke<br>
        Ringelsweide 9<br>
        40223 Düsseldorf<br><br>
        <strong>Kontakt:</strong><br>
        Telefon: +49 211 15821329<br>
        E-Mail: amtsschimmel-killer@proton.me<br>
        Web: amtsschimmel-killer.streamlit.app<br><br>
        <strong>Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV:</strong><br>
        Elisabeth Reinecke (Anschrift wie oben)
        </div>
        """, unsafe_allow_html=True)

with col_dat:
    with st.expander("⚖️ Datenschutzerklärung (DSGVO)"):
        st.markdown(f"""
        <div class="legal-box">
        <strong>1. Datenschutz auf einen Blick</strong><br>
        Die Betreiberin dieser Anwendung nimmt den Schutz Ihrer persönlichen Daten sehr ernst. Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Datenschutzvorschriften sowie dieser Datenschutzerklärung.<br><br>
        <strong>2. Datenerfassung in dieser App</strong><br>
        <strong>Dokumentenverarbeitung:</strong> Hochgeladene Dokumente werden verschlüsselt an die OpenAI-Schnittstelle zur Analyse übertragen. Wir speichern keine Dokumente dauerhaft. Sobald die Browsersitzung beendet wird, werden die Daten gelöscht.<br>
        <strong>Zahlungen:</strong> Wir nutzen Stripe für Zahlungen. Ihre Kreditkartendaten werden direkt von Stripe verarbeitet; wir haben keinen Zugriff darauf.<br><br>
        <strong>3. Hosting</strong><br>
        Diese App wird auf Streamlit Cloud gehostet. Dabei werden Server-Logfiles erfasst, auf die wir keinen direkten Einfluss haben.<br><br>
        <strong>4. Ihre Rechte</strong><br>
        Sie haben das Recht auf Auskunft, Berichtigung, Sperrung oder Löschung Ihrer Daten. Kontaktieren Sie uns hierzu unter der im Impressum angegebenen E-Mail.
        </div>
        """, unsafe_allow_html=True)
