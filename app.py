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

# 2. SESSION STATE & ADMIN
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

params = st.query_params
if params.get("admin") == "GeheimAmt2024!": st.session_state.credits = 999
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        pack = int(params.get("pack", 0))
        st.session_state.credits += pack
        st.session_state.processed_sessions.append(params["session_id"])
        st.balloons()
    except: pass

# 3. DESIGN (CSS)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; scale: 1.02; }
    .legal-box { font-size: 0.9em; color: #334155; line-height: 1.6; background: #f8fafc; padding: 25px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .result-section { background-color: #ffffff; border-left: 5px solid #1e3a8a; padding: 15px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); white-space: pre-wrap; }
    .ampel-red { background: #fee2e2; color: #991b1b; padding: 10px; border-radius: 8px; font-weight: bold; border: 1px solid #f87171; margin-bottom: 10px; }
    .ampel-yellow { background: #fef9c3; color: #854d0e; padding: 10px; border-radius: 8px; font-weight: bold; border: 1px solid #facc15; margin-bottom: 10px; }
    .ampel-green { background: #f0fdf4; color: #166534; padding: 10px; border-radius: 8px; font-weight: bold; border: 1px solid #4ade80; margin-bottom: 10px; }
    .faq-q { font-weight: bold; color: #1e3a8a; margin-top: 15px; font-size: 1.1em; display: block; }
    .faq-a { margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #cbd5e1; color: #475569; }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNKTIONEN
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_letter(raw_text, lang, mode="Standard"):
    if len(raw_text) < 45: return "FEHLER_UNSCHARF"
    
    intent = "Erstelle eine professionelle Antwort." if mode == "Standard" else "Erstelle einen rechtlich fundierten, harten WIDERSPRUCH gegen diesen Bescheid."
    
    sys_p = f"""Rechtsexperte. Sprache: {lang}. 
    Analysiere den Brief. Falls unleserlich, antworte NUR: FEHLER_UNSCHARF.
    Struktur:
    ### AMPEL ### (Farbe: ROT, GELB oder GRÜN + Grund)
    ### GLOSSAR ### (3-4 Behördenbegriffe aus dem Brief einfach erklärt)
    ### FRISTEN ### (Liste: Datum | Aktion | Dringlichkeit)
    ### ANTWORTBRIEF ### ({intent})
    ### CHECKLISTE ### (Genaue Versandanweisung)"""
    
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices[0].message.content

def create_excel_pro(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({"Frist-Datum": dates, "Details": ["Termin aus Behördenbrief" for _ in dates]})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Fristen')
        worksheet = writer.sheets['Fristen']
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 5
            worksheet.set_column(i, i, max_len)
    return output.getvalue()

def create_pdf_bytes(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return bytes(pdf.output())

# 5. SIDEBAR
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    st.divider()
    st.subheader("Einstellungen")
    lang_choice = st.selectbox("Zielsprache der Analyse", 
        ["Deutsch", "English", "Türkçe", "Polski", "Русский", "Español", "Français", "Albanian", "Italiano", "Nederlands", "العربية", "Українська"])
    
    st.divider()
    st.subheader("Guthaben aufladen")
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small>✔ Einmalzahlung | <b>KEIN ABO</b></small></a>', unsafe_allow_html=True)

# 6. HAUPTBEREICH
t1, t2, t3 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ & Hilfe"])

with t1:
    st.title("Amtsschimmel-Killer 📄🚀")
    col_v, col_a = st.columns([1, 1.2]) 
    
    with col_v:
        upload = st.file_uploader("Brief hier hochladen:", type=['pdf', 'png', 'jpg', 'jpeg'])
        if upload:
            if upload.type == "application/pdf":
                try:
                    images = convert_from_bytes(upload.getvalue(), dpi=72, first_page=1, last_page=1)
                    st.image(images, caption="Vorschau Seite 1", use_container_width=True)
                except: st.info("✅ PDF geladen.")
            else: st.image(upload, caption="Vorschau", use_container_width=True)

    with col_a:
        if upload and st.session_state.credits > 0 and not st.session_state.full_res:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🚀 ANALYSE STARTEN"):
                    with st.spinner("Analyse läuft..."):
                        # Logik: get_text_hybrid einfügen
                        res = analyze_letter("Dummy Text...", lang_choice, "Standard")
                        if "FEHLER_UNSCHARF" in res: st.error("⚠️ Foto zu unscharf! Kein Abzug.")
                        else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
            with c2:
                if st.button("⚖️ WIDERSPRUCH ERSTELLEN"):
                    with st.spinner("Widerspruch wird generiert..."):
                        res = analyze_letter("Dummy Text...", lang_choice, "Widerspruch")
                        if "FEHLER_UNSCHARF" in res: st.error("⚠️ Foto zu unscharf! Kein Abzug.")
                        else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
        
        if st.session_state.full_res:
            # Ampel Visualisierung
            if "ROT" in st.session_state.full_res: st.markdown('<div class="ampel-red">🚦 DRINGLICHKEIT: HOCH</div>', unsafe_allow_html=True)
            elif "GELB" in st.session_state.full_res: st.markdown('<div class="ampel-yellow">🚦 DRINGLICHKEIT: MITTEL</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="ampel-green">🚦 DRINGLICHKEIT: NIEDRIG</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="result-section">{st.session_state.full_res}</div>', unsafe_allow_html=True)
            
            d1, d2, d3 = st.columns(3)
            with d1: st.download_button("📊 Excel Fristen", create_excel_pro(st.session_state.full_res), "fristen.xlsx")
            with d2: st.download_button("📄 PDF Brief", create_pdf_bytes(st.session_state.full_res), "antwort.pdf")
            with d3: 
                if st.button("🔄 Nächster Brief"): st.session_state.full_res = ""; st.rerun()

with t2:
    st.subheader("Vorlagen")
    st.markdown("**Fristverlängerung:**")
    st.info("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")
    st.markdown("**Widerspruch einlegen (Fristwahrend):**")
    st.info("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]")
    st.markdown("**Akteneinsicht einfordern:**")
    st.info("Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

with t3:
    st.subheader("FAQ")
    faq_list = [
        ("Ist das ein Abonnement?", "Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung."),
        ("Wie sicher sind meine Dokumente?", "Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht."),
        ("Ersetzt die App eine Rechtsberatung?", "Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt."),
        ("Was passiert, wenn der Scan fehlschlägt?", "Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen."),
        ("Wie erreiche ich Elisabeth Reinecke?", "Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")
    ]
    for q, a in faq_list:
        st.markdown(f'<span class="faq-q">{q}</span><div class="faq-a">{a}</div>', unsafe_allow_html=True)

# 7. FOOTER (Impressum & Datenschutz Wort für Wort)
st.divider()
c_imp, c_dat = st.columns(2)
with c_imp:
    with st.expander("🏢 Impressum"):
        st.markdown("""<div class="legal-box"><strong>Amtsschimmel-Killer</strong><br>Betreiberin: Elisabeth Reinecke<br>Ringelsweide 9, 40223 Düsseldorf<br><br><strong>Kontakt:</strong><br>Telefon: +49 211 15821329<br>E-Mail: amtsschimmel-killer@proton.me<br>Web: amtsschimmel-killer.streamlit.app<br><br><strong>Haftung:</strong><br>Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.</div>""", unsafe_allow_html=True)
with c_dat:
    with st.expander("⚖️ Datenschutz"):
        st.markdown("""<div class="legal-box"><strong>1. Datenschutz auf einen Blick</strong><br>Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).<br><br><strong>2. Datenerfassung & Hosting</strong><br>Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.<br><br><strong>3. Dokumentenverarbeitung</strong><br>Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.<br><br><strong>4. Zahlungsabwicklung (Stripe)</strong><br>Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.<br><br><strong>5. Ihre Rechte</strong><br>Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.</div>""", unsafe_allow_html=True)
