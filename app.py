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
    content = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:Frist: Amtsschimmel-Killer\nDESCRIPTION:{data.get('Fristen', 'Termin prüfen')}\nEND:VEVENT\nEND:VCALENDAR"
    return content.encode('utf-8')

# ==========================================
# 3. DESIGN & STYLING
# ==========================================
st.markdown("""
    <style>
        .block-container { padding-top: 5rem !important; }
        .paket-card { 
            border: 1px solid #dee2e6; padding: 15px; border-radius: 12px; 
            background-color: #ffffff; margin-bottom: 10px; text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .price-tag { font-size: 18px; font-weight: bold; color: #0d47a1; }
        .result-box { 
            background-color: #f8fbff; padding: 15px; border-radius: 10px; 
            border-left: 5px solid #0d47a1; margin-bottom: 10px; 
        }
        .stLinkButton a {
            background-color: #0d47a1 !important; color: white !important;
            border-radius: 6px !important; width: 100% !important; display: block;
            text-align: center; padding: 10px; font-weight: bold; text-decoration: none;
        }
    </style>
    """, unsafe_allow_html=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# 4. INFOS & RECHTLICHES (EXPANDER MIT ABSTÄNDEN)
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
        st.write("Diese App wird auf Streamlit Cloud gehostet. Logfiles werden automatisch vom Hoster erfasst.")
        st.write("")
        st.write("**3. Dokumentenverarbeitung**")
        st.write("Übertragung an OpenAI (USA) via TLS. Keine dauerhafte Speicherung der Briefe.")
        st.write("")
        st.write("**4. Zahlungsabwicklung**")
        st.write("Abwicklung via Stripe. Wir erhalten nur die Zahlungsbestätigung.")
        st.write("")
        st.write("**5. Ihre Rechte**")
        st.write("Recht auf Auskunft & Löschung via amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.write("**Ist das ein Abonnement?**")
        st.write("Nein. Jede Zahlung ist eine Einmalzahlung. Wir hassen Abos!")
        st.write("")
        st.write("**Wie sicher sind meine Dokumente?**")
        st.write("Verschlüsselte Verarbeitung, Löschung nach dem Scan.")
        st.write("")
        st.write("**Ersetzt die App eine Rechtsberatung?**")
        st.write("Nein. Wir bieten eine Formulierungshilfe.")
        st.write("")
        st.write("**Was passiert bei Fehlern?**")
        st.write("Nur erfolgreiche Analysen verbrauchen Guthaben.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.info("Fristverlängerung")
        st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung...")
        st.info("Widerspruch")
        st.code("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum] lege ich hiermit Widerspruch ein...")
        st.info("Akteneinsicht")
        st.code("Sehr geehrte Damen und Herren, beantrage ich hiermit gemäß § 25 SGB X Akteneinsicht.")

st.divider()

# ==========================================
# 5. HAUPTBEREICH (3 SPALTEN FIXIERT)
# ==========================================
col_links, col_mitte, col_rechts = st.columns([1, 1.2, 1.4])

# --- SPALTE LINKS: PAKETE ---
with col_links:
    st.subheader("🌐 Sprachen")
    lang = st.selectbox("Wahl", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇺🇦 Ukrainska"], label_visibility="collapsed")
    st.write("")
    if os.path.exists("icon_final_blau.png"): 
        st.image("icon_final_blau.png", width=100)
    st.write("---")
    paks = [
        ("📄", "Analyse (1 Dok)", "3,99 €", STRIPE_1),
        ("📦", "Spar-Paket (3 Dok)", "9,99 €", STRIPE_2),
        ("👑", "Sorglos-Paket (10 Dok)", "19,99 €", STRIPE_3)
    ]
    for icon, t, p, l in paks:
        st.markdown(f'<div class="paket-card"><span style="font-size: 24px;">{icon}</span><br><b>{t}</b><br><span class="price-tag">{p}</span><br><small>❌ KEIN ABO</small></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", l)
        st.write("")

# --- SPALTE MITTE: UPLOAD ---
with col_mitte:
    st.subheader("📑 Upload & Vorschau")
    st.info(f"Guthaben: **{st.session_state.credits} Scans**")
    upped = st.file_uploader("Upload", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if upped:
        if upped.type == "application/pdf":
            raw = upped.read()
            st.image(convert_from_bytes(raw, first_page=1, last_page=1), caption="Vorschau", use_container_width=True)
            upped.seek(0)
        else:
            st.image(Image.open(upped), use_container_width=True)

# --- SPALTE RECHTS: ANALYSE & EXPORT ---
with col_rechts:
    st.subheader("🔍 Analyse & Antwort")
    
    if upped and st.button("🚀 JETZT ANALYSIEREN", type="primary", use_container_width=True):
        if st.session_state.credits > 0:
            with st.spinner("Analyse läuft..."):
                try:
                    text = ""
                    if upped.type == "application/pdf":
                        with pdfplumber.open(upped) as pdf:
                            for p in pdf.pages: text += (p.extract_text() or "")
                    else:
                        text = pytesseract.image_to_string(Image.open(upped))
                    
                    prompt = f"Analysiere auf {lang}. ###SUM### Zusammenfassung, ###FRIST### Fristen, ###ANTWORT### Entwurf. Text: {text}"
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
        for title, text in st.session_state.full_res.items():
            st.markdown(f'<div class="result-box"><b>{title.upper()}</b><br>{text}</div>', unsafe_allow_html=True)
        
        st.write("---")
        st.write("📥 **Export-Optionen:**")
        ex1, ex2, ex3, ex4 = st.columns(4)
        with ex1: st.download_button("📄 PDF", get_pdf_bytes(st.session_state.full_res), "Analyse.pdf")
        with ex2: st.download_button("📝 Word", get_docx_bytes(st.session_state.full_res), "Analyse.docx")
        with ex3: st.download_button("📊 Excel", get_xlsx_bytes(st.session_state.full_res), "Analyse.xlsx")
        with ex4: st.download_button("📅 Kalender", get_ics_bytes(st.session_state.full_res), "frist.ics")
        
        if st.button("🔄 Neuer Scan", use_container_width=True):
            st.session_state.full_res = None
            st.rerun()
    else:
        st.info("Hier erscheint das Ergebnis nach dem Scan.")
