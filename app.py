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
    .legal-box { font-size: 0.85em; color: #475569; line-height: 1.5; background: #f8fafc; padding: 15px; border-radius: 8px; }
    .faq-q { font-weight: bold; color: #1e3a8a; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
stripe.api_key = st.secrets["STRIPE_API_KEY"]

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

# --- 6. HAUPTBEREICH (Tabs für Funktionen) ---
tab1, tab2, tab3 = st.tabs(["🚀 Brief-Killer", "⚡ Sofort-Antworten", "❓ FAQ & Hilfe"])

with tab1:
    st.title("Amtsschimmel-Killer 📄🚀")
    st.write("Lade deinen Behördenbrief hoch. Wir analysieren Fristen und schreiben die perfekte Antwort.")
    
    upload = st.file_uploader("Datei wählen (PDF, JPG, PNG)", type=['pdf', 'png', 'jpg', 'jpeg'])
    
    if upload:
        if st.session_state.credits > 0:
            if st.button("🚀 Jetzt analysieren & Antwort erstellen"):
                with st.spinner("Amtsschimmel wird vertrieben..."):
                    # Hier folgt deine get_text_hybrid & KI-Logik
                    st.session_state.credits -= 1
                    st.session_state.last_analysis = "KI Ergebnis..." # Platzhalter
                    st.rerun()
        else:
            st.warning("Dein Guthaben ist leer. Bitte wähle ein Paket in der Seitenleiste (Einmalzahlung).")

with tab2:
    st.subheader("⚡ Sofort-Antworten")
    st.info("Kopiere diese Vorlagen für die häufigsten Fälle direkt heraus:")
    
    with st.expander("⏳ Fristverlängerung beantragen"):
        st.code("Sehr geehrte Damen und Herren,\n\nin der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen.\n\nMit freundlichen Grüßen,\n[Dein Name]", language="text")
    
    with st.expander("🛑 Widerspruch einlegen (Fristwahrend)"):
        st.code("Sehr geehrte Damen und Herren,\n\ngegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben.\n\nMit freundlichen Grüßen,\n[Dein Name]", language="text")

with tab3:
    st.subheader("Häufig gestellte Fragen (FAQ)")
    faqs = {
        "Ist das wirklich kein Abo?": "Ja, absolut sicher. Jede Zahlung ist eine Einmalzahlung für eine bestimmte Anzahl an Scans. Es gibt keine automatische Verlängerung.",
        "Was passiert mit meinen hochgeladenen Briefen?": "Deine Daten werden verschlüsselt an die KI (OpenAI) zur Analyse übertragen und nach der Sitzung sofort aus unserem Zwischenspeicher gelöscht.",
        "Ist die Antwort rechtssicher?": "Die App bietet eine starke Orientierungshilfe und professionelle Formulierungen. Sie ersetzt jedoch keine individuelle Rechtsberatung durch einen Anwalt.",
        "Wie erreiche ich den Support?": "Schreibe uns einfach eine E-Mail an die im Impressum angegebene Adresse."
    }
    for q, a in faqs.items():
        st.markdown(f"<div class='faq-q'>{q}</div>", unsafe_allow_html=True)
        st.write(a)

# --- 7. FOOTER (Impressum & Datenschutz kombiniert) ---
st.divider()
c1, c2 = st.columns(2)

with c1:
    with st.expander("🏢 Impressum"):
        st.markdown("""
        <div class="legal-box">
        <strong>Amtsschimmel-Killer</strong><br>
        Betreiber: [Dein Vorname Nachname]<br>
        [Deine Straße Hausnummer]<br>
        [Dein PLZ Ort]<br><br>
        <strong>Kontakt:</strong><br>
        E-Mail: [Deine E-Mail Adresse]<br>
        Web: amtsschimmel-killer.de<br><br>
        <strong>Haftungshinweis:</strong><br>
        Trotz sorgfältiger inhaltlicher Kontrolle übernehmen wir keine Haftung für die Inhalte externer Links oder die Richtigkeit der KI-generierten Texte.
        </div>
        """, unsafe_allow_html=True)

with c2:
    with st.expander("⚖️ Datenschutzerklärung (DSGVO)"):
        st.markdown("""
        <div class="legal-box">
        <strong>1. Datenverarbeitung:</strong> Hochgeladene Dokumente werden via TLS-Verschlüsselung an OpenAI zur Analyse übertragen. Wir speichern keine Dokumente dauerhaft.<br><br>
        <strong>2. Zahlungen:</strong> Wir nutzen Stripe. Es werden keine Bankdaten auf unseren Servern gespeichert.<br><br>
        <strong>3. Ihre Rechte:</strong> Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer personenbezogenen Daten im Rahmen der gesetzlichen Bestimmungen.<br><br>
        <strong>4. Cookies:</strong> Wir nutzen nur technisch notwendige Cookies, um Ihr Guthaben während der Sitzung zu verwalten.
        </div>
        """, unsafe_allow_html=True)
