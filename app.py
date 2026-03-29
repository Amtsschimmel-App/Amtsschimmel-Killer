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
    .legal-box { font-size: 0.8em; color: #475569; line-height: 1.6; background: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .faq-question { font-weight: bold; color: #1e3a8a; margin-top: 15px; font-size: 1.1em; }
    .faq-answer { margin-bottom: 15px; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. SESSION STATE & ADMIN LOGIK (999 GUTHABEN FIX)
if "credits" not in st.session_state:
    st.session_state.credits = 0
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = ""

# ADMIN-AKTIVIERUNG: Muss ganz oben stehen
# URL-Aufruf: https://amtsschimmel-killer.streamlit.app!
if st.query_params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999
    st.toast("🔓 ADMIN-MODUS AKTIV: 999 Scans freigeschaltet")

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
            st.markdown(f'''<a href="{link}" target="_blank" class="buy-button"><b>{name}</b><br>{price} | {count}<br><small>✔ Einmalzahlung | Kein Abo</small></a>''', unsafe_allow_html=True)
    except: st.error("Stripe-Links fehlen.")

# --- 6. HAUPTBEREICH (Tabs) ---
tab1, tab2, tab3 = st.tabs(["🚀 Brief-Killer", "⚡ Sofort-Antworten", "❓ FAQ & Hilfe"])

with tab1:
    st.title("Amtsschimmel-Killer 📄🚀")
    s1, s2, s3 = st.columns(3)
    with s1: st.markdown('<div style="text-align:center; padding:10px; background:#eff6ff; border-radius:10px;"><b>1. Guthaben</b><br><small>Paket links wählen.</small></div>', unsafe_allow_html=True)
    with s2: st.markdown('<div style="text-align:center; padding:10px; background:#eff6ff; border-radius:10px;"><b>2. Upload</b><br><small>Brief hochladen.</small></div>', unsafe_allow_html=True)
    with s3: st.markdown('<div style="text-align:center; padding:10px; background:#eff6ff; border-radius:10px;"><b>3. Antwort</b><br><small>Text kopieren.</small></div>', unsafe_allow_html=True)
    
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
                with st.spinner("KI arbeitet..."):
                    st.session_state.last_analysis = "KI-Vorschlag folgt..." 
                    st.session_state.credits -= 1
                    st.rerun()
        elif upload: st.error("Guthaben leer.")

    if st.session_state.last_analysis:
        st.success("Analyse abgeschlossen!")
        st.code(st.session_state.last_analysis, language="text")
        st.download_button("💾 Download", st.session_state.last_analysis, "antwort.txt")

with tab2:
    st.subheader("⚡ Sofort-Antworten")
    with st.expander("⏳ Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren,\nin der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist...", language="text")

with tab3:
    st.subheader("❓ Häufig gestellte Fragen (FAQ)")
    faq_data = [
        ("Ist das wirklich kein Abo?", "Ja. Jede Zahlung ist eine Einmalzahlung. Keine automatische Verlängerung."),
        ("Datensicherheit?", "Dokumente werden verschlüsselt verarbeitet und nach der Analyse sofort gelöscht."),
        ("Rechtsberatung?", "Nein. Die App ist eine Formulierungshilfe und kein Ersatz für einen Anwalt.")
    ]
    for q, a in faq_data:
        st.markdown(f"**{q}**\n\n{a}")

# --- 7. FOOTER (AUSFÜHRLICHES IMPRESSUM & DATENSCHUTZ) ---
st.divider()
c1, c2 = st.columns(2)

with c1:
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
        Web: <a href="https://amtsschimmel-killer.streamlit.app">amtsschimmel-killer.streamlit.app</a><br><br>
        <strong>Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV:</strong><br>
        Elisabeth Reinecke (Anschrift wie oben)
        </div>
        """, unsafe_allow_html=True)

with c2:
    with st.expander("⚖️ Datenschutzerklärung (DSGVO)"):
        st.markdown(f"""
        <div class="legal-box">
        <strong>1. Datenschutz auf einen Blick</strong><br>
        Die Betreiberin dieser App nimmt den Schutz Ihrer persönlichen Daten sehr ernst. Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Datenschutzvorschriften (DSGVO).<br><br>
        <strong>2. Datenerfassung</strong><br>
        - <strong>Dokumente:</strong> Hochgeladene Briefe werden verschlüsselt an die OpenAI-Schnittstelle zur Textextraktion übertragen. Wir speichern keine Dokumente dauerhaft auf unseren Servern.<br>
        - <strong>Zahlung:</strong> Die Zahlungsabwicklung erfolgt über Stripe. Wir speichern keine Kreditkartendaten.<br><br>
        <strong>3. Ihre Rechte</strong><br>
        Sie haben jederzeit das Recht auf Auskunft über Herkunft, Empfänger und Zweck Ihrer gespeicherten personenbezogenen Daten. Sie haben außerdem ein Recht, die Berichtigung oder Löschung dieser Daten zu verlangen. Kontaktieren Sie uns hierzu unter amtsschimmel-killer@proton.me.<br><br>
        <strong>4. Analyse-Tools</strong><br>
        Wir verzichten auf Tracking-Tools oder Cookies von Drittanbietern zu Werbezwecken. Es werden lediglich technisch notwendige Session-Daten zur Verwaltung Ihres Guthabens verwendet.
        </div>
        """, unsafe_allow_html=True)
