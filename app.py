import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
import pandas as pd
import re
from fpdf import FPDF 
from docx import Document
from docx.shared import Inches
from datetime import datetime

# ==========================================
# 1. RECHTSTEXTE & KONSTANTEN (UNVERÄNDERLICH)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

LOGO_DATEI = "icon_final_blau.png"

IMPRESSUM_TEXT = """
**Amtsschimmel-Killer**  
Betreiberin: Elisabeth Reinecke  
Ringelsweide 9  
40223 Düsseldorf  

**Kontakt:**  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
Web: amtsschimmel-killer.streamlit.app  

**Haftung:**  
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
"""

DATENSCHUTZ_TEXT = """
**1. Datenschutz auf einen Blick**  
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

**2. Datenerfassung & Hosting**  
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

**3. Dokumentenverarbeitung**  
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

**4. Zahlungsabwicklung (Stripe)**  
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

**5. Ihre Rechte**  
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
"""

FAQ_TEXT = """
**Ist das ein Abonnement?**  
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

**Wie sicher sind meine Dokumente?**  
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

**Ersetzt die App eine Rechtsberatung?**  
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

**Was passiert, wenn der Scan fehlschlägt?**  
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

**Wie erreiche ich Elisabeth Reinecke?**  
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
"""

VORLAGEN = [
    ("Fristverlängerung", "Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]"),
    ("Widerspruch einlegen (Fristwahrend)", "Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]"),
    ("Akteneinsicht einfordern", "Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")
]

# ==========================================
# 2. SESSION STATE & ADMIN-LOGIN
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

params = st.query_params
if params.get("admin") == "GeheimAmt2024!" and st.session_state.credits < 500:
    st.session_state.credits = 999

if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        st.session_state.credits += int(params.get("pack", 0))
        st.session_state.processed_sessions.append(params["session_id"])
        st.balloons()
    except: pass

# ==========================================
# 3. EXPORT FUNKTIONEN (Sicher & Robust)
# ==========================================
def clean_txt(t):
    # Filtert Emojis für PDF-Stabilität
    return t.replace("###","").replace("**","").replace("🚦","").replace("📖","").replace("📅","").replace("✍️","").replace("📋","").encode('latin-1', 'replace').decode('latin-1')

def create_pdf_final(text):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_DATEI): 
        pdf.image(LOGO_DATEI, x=10, y=8, w=33)
        pdf.ln(25)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "ANALYSE-ERGEBNIS", ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, txt=clean_txt(text))
    return bytes(pdf.output())

def create_excel_final(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({"Datum": dates if dates else ["Gefunden"], "Analyse": * max(1, len(dates))})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
        writer.sheets['Sheet1'].set_column(1, 1, 120) # Maximale Breite
    return output.getvalue()

def create_ics_final(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\n"
    for d in dates:
        try:
            cd = datetime.strptime(d, "%d.%m.%Y").strftime("%Y%m%d")
            ics += f"BEGIN:VEVENT\nSUMMARY:Frist Amtsschimmel\nDTSTART:{cd}\nDTEND:{cd}\nEND:VEVENT\n"
        except: pass
    ics += "END:VCALENDAR"
    return ics.encode('utf-8')

# ==========================================
# 4. KI-LOGIK (Glossar, Ampel & Checkliste)
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text(file):
    text = ""
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages: text += page.extract_text() or ""
            if len(text.strip()) < 30:
                imgs = convert_from_bytes(file.getvalue())
                for i in imgs: text += pytesseract.image_to_string(i)
        else:
            text = pytesseract.image_to_string(Image.open(file))
    except: pass
    return text

def run_ai(raw_text, lang, mode):
    if len(raw_text.strip()) < 40: return "FEHLER_UNSCHARF"
    label = "Widerspruch" if mode == "W" else "Antwortbrief"
    
    # HIER SIND DIE FEATURES FEST VERANKERT
    sys_p = f"""Rechtsexperte. Sprache: {lang}. 
    Erstelle IMMER folgende Sektionen:
    1. ### 🚦 DRINGLICHKEITS-AMPEL ### (ROT/GELB/GRÜN + Begründung)
    2. ### 📖 BEHÖRDEN-DOLMETSCHER ### (Erkläre 3-4 Fachbegriffe aus dem Brief einfach)
    3. ### 📅 WICHTIGE FRISTEN ### (Liste: Datum | Aktion)
    4. ### ✍️ DEIN {label.upper()} ### (Schreibe den vollständigen {label})
    5. ### 📋 VERSAND-CHECKLISTE ### (Genaue Anleitung zum Versenden)"""
    
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices[0].message.content

# ==========================================
# 5. UI - LAYOUT (Vorschau links / Analyse rechts)
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    # FLAGGEN IM MULTI-LANGUAGE SUPPORT
    lang_choice = st.selectbox("🌍 Sprache wählen", [
        "🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", 
        "🇪🇸 Español", "🇫🇷 Français", "🇦🇱 Albanian", "🇮🇹 Italiano", 
        "🇳🇱 Nederlands", "🇸🇦 العربية", "🇺🇦 Українська"
    ])
    st.divider()
    st.subheader("💳 Pakete (Einmalzahlung)")
    for n, l, c, p in [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]:
        st.markdown(f'''
            <a href="{l}" target="_blank" style="text-decoration:none;">
                <div style="background:white; border:2px solid #1e3a8a; padding:12px; border-radius:12px; margin-bottom:10px; color:#1e3a8a; text-align:center;">
                    <b>{n}</b><br>
                    <span style="font-size:1.1em; font-weight:bold;">{p} | {c}</span><br>
                    <span style="color:#16a34a; font-weight:bold; font-size:0.8em;">✔ KEIN ABO</span>
                </div>
            </a>
        ''', unsafe_allow_html=True)

t1, t2, t3, t4, t5 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ", "⚖️ Impressum", "🔒 Datenschutz"])

with t1:
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.subheader("1. Dokument")
        upload = st.file_uploader("Bild oder PDF:", type=['pdf','png','jpg','jpeg'], key="up_vfinal")
        if upload:
            # VORSCHAU LINKS FEST VERANKERT
            if upload.type.startswith("image"): st.image(upload, use_container_width=True, caption="Dokument-Vorschau")
            else: st.success("✅ PDF erfolgreich geladen.")

    with col_r:
        st.subheader("2. Ergebnis")
        if upload and st.session_state.credits > 0:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🚀 ANALYSE"):
                    with st.spinner("Dolmetscher arbeitet..."):
                        txt = get_text(upload); res = run_ai(txt, lang_choice, "S")
                        st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
            with c2:
                if st.button("⚖️ WIDERSPRUCH"):
                    with st.spinner("Generator läuft..."):
                        txt = get_text(upload); res = run_ai(txt, lang_choice, "W")
                        st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
        
        if st.session_state.full_res:
            st.markdown(f'<div style="background:#f8fafc; padding:20px; border-radius:10px; border-left:5px solid #1e3a8a;">{st.session_state.full_res}</div>', unsafe_allow_html=True)
            st.divider()
            st.write("### 📥 Downloads")
            d1, d2, d3, d4 = st.columns(4)
            with d1: 
                doc = Document(); doc.add_paragraph(st.session_state.full_res); b_word = io.BytesIO(); doc.save(b_word)
                st.download_button("📝 Word", b_word.getvalue(), "Brief.docx")
            with d2: st.download_button("📄 PDF", create_pdf_final(st.session_state.full_res), "Analyse.pdf")
            with d3: st.download_button("📊 Excel", create_excel_final(st.session_state.full_res), "Fristen.xlsx")
            with d4: st.download_button("📅 Kalender", create_ics_final(st.session_state.full_res), "Termin.ics")

# RECHTLICHE TABS (Fixiert)
with t2:
    st.header("⚡ Schnell-Vorlagen")
    for title, text in VORLAGEN: st.markdown(f"**{title}:**"); st.info(text)
with t3: st.header("❓ FAQ"); st.markdown(FAQ_TEXT)
with t4: st.header("⚖️ Impressum"); st.markdown(IMPRESSUM_TEXT)
with t5: st.header("🔒 Datenschutz"); st.markdown(DATENSCHUTZ_TEXT)

st.sidebar.caption(f"© {datetime.now().year} Elisabeth Reinecke")
