import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
import pandas as pd
from docx import Document
from fpdf import FPDF 
from datetime import datetime

# ==========================================
# 1. SETUP & GUTHABEN-LOGIK
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

if "credits" not in st.session_state:
    st.session_state.credits = 0
if "full_res" not in st.session_state:
    st.session_state.full_res = None
if "processed_sessions" not in st.session_state:
    st.session_state.processed_sessions = set()

# STRIPE LINKS
STRIPE_1 = "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" 
STRIPE_2 = "https://buy.stripe.com/8x228retRbj50paalq1gs03" 
STRIPE_3 = "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04" 

# ZAHLUNGSERKENNUNG
params = st.query_params
sid = params.get("session_id", "")
if "pack" in params and sid not in st.session_state.processed_sessions:
    val = params["pack"]
    if val == "1": st.session_state.credits += 1
    elif val == "2": st.session_state.credits += 3
    elif val == "3": st.session_state.credits += 10
    if sid: st.session_state.processed_sessions.add(sid)
    st.toast("✅ Zahlung erfolgreich verbucht!", icon="💰")

if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

# ==========================================
# 2. EXPORT FUNKTIONEN
# ==========================================
def get_pdf_bytes(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=True, align='C')
    pdf.ln(10)
    for k, v in data.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, k.upper(), ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 7, txt=str(v).encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)
    return bytes(pdf.output(dest='S'))

def get_docx_bytes(data):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Analyse', 0)
    for k, v in data.items():
        doc.add_heading(k, level=1)
        doc.add_paragraph(str(v))
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def get_xlsx_bytes(data):
    df = pd.DataFrame([{"Kategorie": k, "Inhalt": v} for k, v in data.items()])
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
    return bio.getvalue()

def get_ics_bytes(data):
    content = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:Frist: Amtsschimmel-Killer\nDESCRIPTION:{data.get('Fristen', 'Frist prüfen')}\nEND:VEVENT\nEND:VCALENDAR"
    return content.encode('utf-8')

# ==========================================
# 3. DESIGN & STYLING
# ==========================================
st.markdown("""
    <style>
        .block-container { padding-top: 3rem !important; }
        .paket-card { 
            border: 1px solid #dee2e6; padding: 15px; border-radius: 12px; 
            background-color: #ffffff; margin-bottom: 10px; text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .price-tag { font-size: 16px; font-weight: bold; color: #0d47a1; margin-top: 5px; }
        .no-abo-text { font-size: 11px; color: #d32f2f; font-weight: bold; text-transform: uppercase; }
        .result-box { background-color: #f8fbff; padding: 15px; border-radius: 10px; border-left: 5px solid #0d47a1; margin-bottom: 10px; }
        .stLinkButton a {
            background-color: #0d47a1 !important; color: white !important;
            border-radius: 6px !important; width: 100% !important; display: block;
            text-align: center; padding: 8px; font-weight: bold; text-decoration: none;
        }
    </style>
    """, unsafe_allow_html=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# 4. INFOS & RECHTLICHES (EXPANDER)
# ==========================================
st.title("Amtsschimmel-Killer 🪓")

t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.write("**Amtsschimmel-Killer**")
        st.write("Betreiberin: Elisabeth Reinecke")
        st.write("Ringelsweide 9, 40223 Düsseldorf")
        st.write("")
        st.write("**Kontakt:**")
        st.write("Telefon: +49 211 15821329")
        st.write("E-Mail: amtsschimmel-killer@proton.me")
        st.write("Web: amtsschimmel-killer.streamlit.app")
        st.write("")
        st.write("**Haftung:**")
        st.write("Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.write("**1. Datenschutz auf einen Blick**")
        st.write("Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).")
        st.write("")
        st.write("**2. Datenerfassung & Hosting**")
        st.write("Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.")
        st.write("")
        st.write("**3. Dokumentenverarbeitung**")
        st.write("Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern.")
        st.write("")
        st.write("**4. Zahlungsabwicklung (Stripe)**")
        st.write("Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung.")
        st.write("")
        st.write("**5. Ihre Rechte**")
        st.write("Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontakt unter amtsschimmel-killer@proton.me.")

with t3:
    with st.expander("❓ FAQ"):
        st.write("**Ist das ein Abonnement?**")
        st.write("Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung.")
        st.write("")
        st.write("**Wie sicher sind meine Dokumente?**")
        st.write("Verschlüsselte Übertragung, keine dauerhafte Speicherung auf unseren Servern. Löschung nach dem Scan.")
        st.write("")
        st.write("**Ersetzt die App eine Rechtsberatung?**")
        st.write("Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis.")
        st.write("")
        st.write("**Was passiert, wenn der Scan fehlschlägt?**")
        st.write("Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat.")
        st.write("")
        st.write("**Wie erreiche ich Elisabeth Reinecke?**")
        st.write("Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me.")

with t4:
    with st.expander("📝 Vorlagen"):
        st.write("**Fristverlängerung:**")
        st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen.")
        st.write("")
        st.write("**Widerspruch:**")
        st.code("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein.")
        st.write("")
        st.write("**Akteneinsicht:**")
        st.code("Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X Akteneinsicht.")

st.divider()

# ==========================================
# 5. HAUPTBEREICH (3 SPALTEN)
# ==========================================
col_paks, col_up, col_res = st.columns([1, 1.2, 1.4])

# --- SPALTE 1: PAKETE ---
with col_paks:
    st.subheader("🌐 Sprachen")
    lang = st.selectbox("Wahl", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇺🇦 Ukrainska"], label_visibility="collapsed")
    st.write("---")
    
    paks = [
        ("📄", "Analyse (1 Dokument)", "3,99 €", STRIPE_1),
        ("📦", "Spar Paket (3 Dokumente)", "9,99 €", STRIPE_2),
        ("👑", "Sorglos Paket (10 Dokumente)", "19,99 €", STRIPE_3)
    ]
    for icon, t, p, l in paks:
        st.markdown(f'<div class="paket-card"><span style="font-size: 24px;">{icon}</span><br>Amtsschimmel Killer: {t}<br><div class="price-tag">Einmalpreis {p}</div><div class="no-abo-text">❌ KEIN ABO</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", l)
        st.write("")

# --- SPALTE 2: UPLOAD (TIEFER GESETZT) ---
with col_up:
    # Der Abstandshalter, um den Upload nach unten neben die Pakete zu schieben
    st.write("<div style='height: 110px;'></div>", unsafe_allow_html=True)
    st.subheader("📑 Upload & Vorschau")
    st.info(f"Guthaben: **{st.session_state.credits} Scans**")
    upped = st.file_uploader("Datei hier reinziehen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if upped:
        if upped.type == "application/pdf":
            raw = upped.read()
            st.image(convert_from_bytes(raw, first_page=1, last_page=1), caption="Vorschau", use_container_width=True)
            upped.seek(0)
        else:
            st.image(Image.open(upped), use_container_width=True)

# --- SPALTE 3: ANALYSE ---
with col_res:
    st.subheader("🔍 Analyse & Antwort")
    if upped and st.button("🚀 JETZT ANALYSIEREN", type="primary", use_container_width=True):
        if st.session_state.credits > 0:
            with st.spinner("KI liest den Amtsschimmel..."):
                try:
                    text = ""
                    if upped.type == "application/pdf":
                        with pdfplumber.open(upped) as pdf:
                            for p in pdf.pages: text += (p.extract_text() or "")
                    else:
                        text = pytesseract.image_to_string(Image.open(upped))
                    
                    prompt = f"Analysiere auf {lang}. Trenne: ###SUM### Zusammenfassung, ###FRIST### Fristen, ###ANTWORT### Antwortentwurf. Text: {text}"
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
                    full = res.choices[0].message.content
                    
                    st.session_state.full_res = {
                        "Zusammenfassung": full.split("###SUM###")[-1].split("###FRIST###")[0].strip(),
                        "Fristen": full.split("###FRIST###")[-1].split("###ANTWORT###")[0].strip(),
                        "Antwort-Entwurf": full.split("###ANTWORT###")[-1].strip()
                    }
                    st.session_state.credits -= 1
                    st.balloons()
                    st.rerun()
                except Exception as e: st.error(f"Fehler: {e}")
        else: st.warning("Bitte erst links Guthaben kaufen!")

    if st.session_state.full_res:
        for title, content in st.session_state.full_res.items():
            st.markdown(f'<div class="result-box"><b>{title.upper()}</b><br>{content}</div>', unsafe_allow_html=True)
        
        st.write("---")
        ex1, ex2, ex3, ex4 = st.columns(4)
        with ex1: st.download_button("📄 PDF", get_pdf_bytes(st.session_state.full_res), "Analyse.pdf")
        with ex2: st.download_button("📝 Word", get_docx_bytes(st.session_state.full_res), "Analyse.docx")
        with ex3: st.download_button("📊 Excel", get_xlsx_bytes(st.session_state.full_res), "Analyse.xlsx")
        with ex4: st.download_button("📅 iCal", get_ics_bytes(st.session_state.full_res), "frist.ics")
        
        if st.button("🔄 Neuer Scan", use_container_width=True):
            st.session_state.full_res = None
            st.rerun()
    else:
        st.info("Hier erscheint das Ergebnis nach dem Scan.")
