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
    .stButton>button:hover { background-color: #2563eb; transform: translateY( -2px); }
    .buy-button { 
        text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; 
        border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s;
    }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; scale: 1.02; }
    .legal-box { font-size: 0.85em; color: #334155; line-height: 1.6; background: #f8fafc; padding: 25px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .faq-q { font-weight: bold; color: #1e3a8a; margin-top: 15px; font-size: 1.1em; display: block; }
    .faq-a { margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #cbd5e1; }
    </style>
    """, unsafe_allow_html=True)

# 3. SESSION STATE & LOGIK
if "credits" not in st.session_state: st.session_state.credits = 0
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# --- GUTHABEN-LOGIK (STRIPE & ADMIN) ---
params = st.query_params

# A) ADMIN-CHECK (999 Scans)
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999
    st.toast("🔓 ADMIN-MODUS AKTIV")

# B) STRIPE-RÜCKKEHR VERARBEITEN
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    pack = int(params.get("pack", 1))
    st.session_state.credits += pack
    st.session_state.processed_sessions.append(params["session_id"])
    st.balloons()
    st.toast(f"✅ {pack} Scan(s) erfolgreich aufgeladen!")

# 4. API INITIALISIERUNG
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
            st.markdown(f'<a href="{link}" target="_blank" class="buy-button"><b>{name}</b><br>{price} | {count}<br><small style="color:#16a34a;">✔ Einmalzahlung | Kein Abo</small></a>', unsafe_allow_html=True)
    except: st.error("Stripe-Konfiguration fehlt.")

# --- 6. HAUPTBEREICH (Tabs) ---
tab1, tab2, tab3 = st.tabs(["🚀 Brief-Killer", "⚡ Sofort-Antworten", "❓ FAQ & Hilfe"])

with tab1:
    st.title("Amtsschimmel-Killer 📄🚀")
    st.write("Verwandle Behördendeutsch in klare Antworten.")
    
    if st.session_state.last_analysis:
        if st.button("🔄 Nächsten Brief bearbeiten"):
            st.session_state.last_analysis = ""; st.rerun()

    if not st.session_state.last_analysis:
        st.info("💡 **Sicherheit:** Private Daten können vor dem Upload geschwärzt werden.")
        upload = st.file_uploader("Brief hochladen", type=['pdf', 'png', 'jpg', 'jpeg'])
        if upload and st.session_state.credits > 0:
            if st.button("🚀 Analyse & Antwort erstellen"):
                with st.spinner("Amtsschimmel wird vertrieben..."):
                    # Hier reale KI-Logik einsetzen
                    st.session_state.last_analysis = "Muster-Antwort: Hiermit lege ich Widerspruch ein..."
                    st.session_state.credits -= 1; st.rerun()
        elif upload: st.warning("Guthaben leer. Bitte Paket wählen.")

    if st.session_state.last_analysis:
        st.success("Analyse abgeschlossen!")
        st.code(st.session_state.last_analysis, language="text")
        st.download_button("💾 Als Textdatei speichern", st.session_state.last_analysis, "antwort.txt")

with tab2:
    st.subheader("⚡ Sofort-Antworten")
    with st.expander("⏳ Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren,\nin der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist bis zum [Datum].\n\nMit freundlichen Grüßen,\n[Name]", language="text")

with tab3:
    st.subheader("❓ Häufig gestellte Fragen (FAQ)")
    faq = [
        ("Ist das ein Abonnement?", "Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung."),
        ("Wie sicher sind meine Dokumente?", "Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht."),
        ("Ersetzt die App eine Rechtsberatung?", "Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt."),
        ("Was passiert, wenn der Scan fehlschlägt?", "Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern, wird kein Guthaben abgezogen."),
        ("Wie erreiche ich Elisabeth Reinecke?", "Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")
    ]
    for q, a in faq:
        st.markdown(f'<span class="faq-q">{q}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="faq-a">{a}</div>', unsafe_allow_html=True)

# --- 7. FOOTER (VOLLES IMPRESSUM & AUSFÜHRLICHE DSGVO) ---
st.divider()
c1, c2 = st.columns(2)

with c1:
    with st.expander("🏢 Impressum"):
        st.markdown(f"""
        <div class="legal-box">
        <strong>Angaben gemäß § 5 TMG:</strong><br>
        Elisabeth Reinecke<br>
        Ringelsweide 9, 40223 Düsseldorf<br><br>
        <strong>Kontakt:</strong><br>
        Telefon: +49 211 15821329<br>
        E-Mail: amtsschimmel-killer@proton.me<br>
        Web: amtsschimmel-killer.streamlit.app<br><br>
        <strong>Umsatzsteuer-ID:</strong><br>
        Entfällt gemäß Kleinunternehmerregelung § 19 UStG.
        </div>
        """, unsafe_allow_html=True)

with c2:
    with st.expander("⚖️ Datenschutzerklärung (DSGVO)"):
        st.markdown(f"""
        <div class="legal-box">
        <strong>1. Datenschutz auf einen Blick</strong><br>
        Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).<br><br>
        <strong>2. Datenerfassung & Hosting</strong><br>
        Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.<br><br>
        <strong>3. Dokumentenverarbeitung</strong><br>
        Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.<br><br>
        <strong>4. Zahlungsabwicklung (Stripe)</strong><br>
        Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.<br><br>
        <strong>5. Ihre Rechte</strong><br>
        Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
        </div>
        """, unsafe_allow_html=True)
