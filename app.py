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

# 1. KONFIGURATION & DESIGN
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")
LOGO_DATEI = "icon_final_blau.png"

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; scale: 1.02; }
    .legal-box { font-size: 0.9em; color: #334155; line-height: 1.6; background: #f8fafc; padding: 25px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .faq-q { font-weight: bold; color: #1e3a8a; margin-top: 15px; font-size: 1.1em; display: block; }
    .faq-a { margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #cbd5e1; color: #475569; }
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE INITIALISIERUNG
if "credits" not in st.session_state: st.session_state.credits = 0
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# --- 3. GUTHABEN-LOGIK (STRIPE & ADMIN) ---
params = st.query_params

# A) ADMIN-CHECK (999 Scans)
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999
    st.toast("🔓 ADMIN-MODUS AKTIV")

# B) STRIPE-ZAHLUNG VERARBEITEN
# Wenn der Nutzer von Stripe zurückkommt (URL enthält session_id)
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        # Wir vertrauen dem 'pack' Parameter in der Rückkehr-URL
        pack_size = int(params.get("pack", 0))
        if pack_size > 0:
            st.session_state.credits += pack_size
            st.session_state.processed_sessions.append(params["session_id"])
            st.balloons()
            st.toast(f"✅ {pack_size} Scan(s) erfolgreich aufgeladen!")
    except:
        pass

# 4. API INITIALISIERUNG
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text_hybrid(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        if len(text.strip()) < 50:
            images = convert_from_bytes(file_bytes, dpi=200)
            text = "\n".join([pytesseract.image_to_string(img, lang='deu') for img in images])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    return text.strip()

def analyze_letter(raw_text, language):
    sys_p = f"Rechtsexperte. Sprache: {language}. Analysiere den Brief, liste Fristen auf und erstelle einen Antworttext mit Platzhaltern."
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices.message.content

# 5. SIDEBAR
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("Einstellungen")
    lang_choice = st.radio("Sprache", ["Deutsch", "English"], horizontal=True)
    voice_choice = st.selectbox("Vorlese-Stimme", ["Weiblich", "Männlich"])
    st.divider()
    st.subheader("Guthaben aufladen")
    # WICHTIG: Die Stripe-Links müssen in deinen Secrets als STRIPE_LINK_1, STRIPE_LINK_3 etc. hinterlegt sein
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), 
            ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), 
            ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small style="color:#16a34a;">✔ Einmalzahlung | <b>KEIN ABO</b></small></a>', unsafe_allow_html=True)

# 6. HAUPTBEREICH
t1, t2, t3 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ & Hilfe"])

with t1:
    st.title("Amtsschimmel-Killer 📄🚀")
    if st.session_state.last_analysis:
        if st.button("🔄 Nächsten Brief bearbeiten"):
            st.session_state.last_analysis = ""; st.rerun()

    if not st.session_state.last_analysis:
        upload = st.file_uploader("Brief hochladen", type=['pdf', 'png', 'jpg', 'jpeg'])
        if upload:
            if upload.type != "application/pdf": st.image(upload, width=350)
            if st.session_state.credits > 0:
                if st.button("🚀 Analyse starten"):
                    with st.spinner("Amtsschimmel wird vertrieben..."):
                        raw = get_text_hybrid(upload)
                        st.session_state.last_analysis = analyze_letter(raw, lang_choice)
                        st.session_state.credits -= 1
                        st.rerun()
            else: st.error("Guthaben leer. Bitte Paket links wählen.")

    if st.session_state.last_analysis:
        st.success("Analyse abgeschlossen!")
        st.markdown(f'<div style="white-space: pre-wrap; background: white; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0;">{st.session_state.last_analysis}</div>', unsafe_allow_html=True)
        st.code(st.session_state.last_analysis, language="text")

with t2:
    st.subheader("⚡ Vorlagen")
    st.write("Kopiere diese Texte für schnelle Antworten:")
    with st.expander("⏳ Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Fristverlängerung bis zum [Datum]...", language="text")

with t3:
    st.subheader("❓ Häufig gestellte Fragen (FAQ)")
    faq_data = [
        ("Ist das ein Abonnement?", "Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung."),
        ("Wie sicher sind meine Dokumente?", "Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht."),
        ("Ersetzt die App eine Rechtsberatung?", "Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt."),
        ("Was passiert, wenn der Scan fehlschlägt?", "Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern, wird kein Guthaben abgezogen."),
        ("Wie erreiche ich Elisabeth Reinecke?", "Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")
    ]
    for q, a in faq_data:
        st.markdown(f'<span class="faq-q">{q}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="faq-a">{a}</div>', unsafe_allow_html=True)

# 7. FOOTER
st.divider()
c1, c2 = st.columns(2)
with c1:
    with st.expander("🏢 Impressum"):
        st.markdown("""
        <div class="legal-box">
        <strong>Amtsschimmel-Killer</strong><br>Betreiberin: Elisabeth Reinecke<br>Ringelsweide 9, 40223 Düsseldorf<br><br>
        <strong>Kontakt:</strong><br>Telefon: +49 211 15821329<br>E-Mail: amtsschimmel-killer@proton.me<br>Web: amtsschimmel-killer.streamlit.app<br><br>
        <strong>Haftung:</strong><br>Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        </div>""", unsafe_allow_html=True)
with c2:
    with st.expander("⚖️ Datenschutz"):
        st.markdown("""
        <div class="legal-box">
        <strong>1. Datenschutz auf einen Blick</strong><br>Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).<br><br>
        <strong>2. Datenerfassung & Hosting</strong><br>Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.<br><br>
        <strong>3. Dokumentenverarbeitung</strong><br>Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.<br><br>
        <strong>4. Zahlungsabwicklung (Stripe)</strong><br>Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.<br><br>
        <strong>5. Ihre Rechte</strong><br>Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
        </div>""", unsafe_allow_html=True)
