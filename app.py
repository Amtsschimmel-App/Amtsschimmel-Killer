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
import pandas as pd
import re
from fpdf import FPDF
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
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; scale: 1.02; }
    .legal-box { font-size: 0.9em; color: #334155; line-height: 1.6; background: #f8fafc; padding: 25px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .result-section { background-color: #ffffff; border-left: 5px solid #1e3a8a; padding: 15px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .faq-q { font-weight: bold; color: #1e3a8a; margin-top: 15px; font-size: 1.1em; display: block; }
    .faq-a { margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #cbd5e1; color: #475569; }
    </style>
    """, unsafe_allow_html=True)

# 3. SESSION STATE
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# Admin & Stripe Check
params = st.query_params
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        pack_val = int(params.get("pack", 0))
        if pack_val > 0:
            st.session_state.credits += pack_val
            st.session_state.processed_sessions.append(params["session_id"])
    except: pass

# 4. FUNKTIONEN
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

def analyze_letter(raw_text, lang):
    sys_p = f"""Rechtsexperte. Sprache: {lang}. 
    Analysiere strikt in diesem Format:
    ### FRISTEN & TERMINE ###
    (Hier alle Daten auflisten)
    ### ANTWORTBRIEF ###
    (Hier den Brieftext mit [Platzhaltern])"""
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices[0].message.content

def create_excel_clean(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({"Frist-Datum": dates, "Beschreibung": ["Ereignis aus dem Brief" for _ in dates]})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Fristen')
        worksheet = writer.sheets['Fristen']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, max(len(col), 30))
    return output.getvalue()

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, txt=text.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output()

# 5. SIDEBAR
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    lang_choice = st.radio("Sprache", ["Deutsch", "English"], horizontal=True)
    st.divider()
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), 
            ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), 
            ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small style="color:#16a34a;">✔ Einmalzahlung | <b>KEIN ABO</b></small></a>', unsafe_allow_html=True)

# 6. HAUPTBEREICH
t1, t2, t3 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ & Hilfe"])

with t1:
    st.title("Amtsschimmel-Killer 📄🚀")
    
    col_v, col_a = st.columns([1, 1.2]) 
    
    with col_v:
        upload = st.file_uploader("Brief hochladen", type=['pdf', 'png', 'jpg', 'jpeg'])
        if upload:
            if upload.type != "application/pdf":
                st.image(upload, caption="Vorschau deines Briefs", use_container_width=True)
            else:
                st.info("PDF zur Analyse bereit.")

    with col_a:
        if upload and st.session_state.credits > 0 and not st.session_state.full_res:
            if st.button("🚀 Analyse & Antwort jetzt erstellen"):
                with st.spinner("Amtsschimmel wird vertrieben..."):
                    raw = get_text_hybrid(upload)
                    st.session_state.full_res = analyze_letter(raw, lang_choice)
                    st.session_state.credits -= 1
                    st.rerun()

        if st.session_state.full_res:
            st.success("Analyse erfolgreich abgeschlossen!")
            
            # Blöcke trennen
            if "### ANTWORTBRIEF ###" in st.session_state.full_res:
                parts = st.session_state.full_res.split("### ANTWORTBRIEF ###")
                st.markdown('<div class="result-section"><b>📅 Fristen & Termine</b><br>' + parts[0].replace("### FRISTEN & TERMINE ###", "") + '</div>', unsafe_allow_html=True)
                st.markdown('<div class="result-section"><b>✍️ Antwortbrief Vorschlag</b><br>' + parts[1] + '</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="result-box">{st.session_state.full_res}</div>', unsafe_allow_html=True)

            # DOWNLOADS
            st.subheader("📥 Export & Download")
            d1, d2, d3 = st.columns(3)
            with d1: st.download_button("💾 Text download", st.session_state.full_res, "antwort.txt")
            with d2: st.download_button("📅 Excel (breite Spalten)", create_excel_clean(st.session_state.full_res), "fristen.xlsx")
            with d3: st.download_button("📄 PDF Brief", create_pdf(st.session_state.full_res), "antwortbrief.pdf")
            
            if st.button("🔄 Nächsten Brief bearbeiten"):
                st.session_state.full_res = ""; st.rerun()

with t2:
    st.subheader("Vorlagen")
    st.info("Fristverlängerung: Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")
    st.info("Widerspruch einlegen (Fristwahrend): Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]")
    st.info("Akteneinsicht einfordern: Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

with t3:
    st.subheader("FAQ")
    st.markdown("<span class='faq-q'>Ist das ein Abonnement?</span><div class='faq-a'>Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.</div>", unsafe_allow_html=True)
    st.markdown("<span class='faq-q'>Wie sicher sind meine Dokumente?</span><div class='faq-a'>Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.</div>", unsafe_allow_html=True)
    st.markdown("<span class='faq-q'>Ersetzt die App eine Rechtsberatung?</span><div class='faq-a'>Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.</div>", unsafe_allow_html=True)
    st.markdown("<span class='faq-q'>Was passiert, wenn der Scan fehlschlägt?</span><div class='faq-a'>Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern, wird kein Guthaben abgezogen.</div>", unsafe_allow_html=True)
    st.markdown("<span class='faq-q'>Wie erreiche ich Elisabeth Reinecke?</span><div class='faq-a'>Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.</div>", unsafe_allow_html=True)

# 7. FOOTER
st.divider()
c_imp, c_dat = st.columns(2)
with c_imp:
    with st.expander("🏢 Impressum"):
        st.markdown("""<div class="legal-box"><strong>Amtsschimmel-Killer</strong><br>Betreiberin: Elisabeth Reinecke<br>Ringelsweide 9, 40223 Düsseldorf<br><br><strong>Kontakt:</strong><br>Telefon: +49 211 15821329<br>E-Mail: amtsschimmel-killer@proton.me<br>Web: amtsschimmel-killer.streamlit.app<br><br><strong>Haftung:</strong><br>Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.</div>""", unsafe_allow_html=True)
with c_dat:
    with st.expander("⚖️ Datenschutz"):
        st.markdown("""<div class="legal-box"><strong>1. Datenschutz auf einen Blick</strong><br>Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).<br><br><strong>2. Datenerfassung & Hosting</strong><br>Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.<br><br><strong>3. Dokumentenverarbeitung</strong><br>Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.<br><br><strong>4. Zahlungsabwicklung (Stripe)</strong><br>Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.<br><br><strong>5. Ihre Rechte</strong><br>Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.</div>""", unsafe_allow_html=True)
