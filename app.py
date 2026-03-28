import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
from fpdf import FPDF 
import pdfplumber
from pdf2image import convert_from_bytes
import pandas as pd
import io
import os
import shutil
import stripe
from datetime import datetime
from openpyxl.styles import Alignment

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# 2. DESIGN (CSS)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #10b981; color: white; font-weight: bold; }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 2px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; }
    .frist-box { background-color: #fef9c3; border-left: 5px solid #facc15; padding: 15px; border-radius: 5px; color: #854d0e; margin-bottom: 20px; font-weight: bold; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
stripe.api_key = st.secrets["STRIPE_API_KEY"]

if shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

# --- HILFSFUNKTIONEN ---
def get_text_hybrid(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        if len(text.strip()) < 50:
            images = convert_from_bytes(file_bytes, dpi=150)
            text = "\n".join([pytesseract.image_to_string(img, lang='deu') for img in images])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    return text.strip()

# --- 4. SESSION STATE & ADMIN-LOGIK ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []
if "last_fristen" not in st.session_state: st.session_state.last_fristen = ""
if "last_brief" not in st.session_state: st.session_state.last_brief = ""

params = st.query_params

# DEIN NEUES ADMIN-PASSWORT
ADMIN_PASSWORT = "GeheimAmt2024!" 

is_admin = params.get("admin") == ADMIN_PASSWORT

if is_admin:
    # Admin bekommt autom. Credits und kann Pakete testen
    if st.session_state.credits < 100: st.session_state.credits = 999
    if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
        pack_size = int(params.get("pack", 1))
        st.session_state.credits += pack_size
        st.session_state.processed_sessions.append(params["session_id"])
        st.toast(f"🛠️ ADMIN: {pack_size} Scans gutgeschrieben!")

# Regulärer Stripe Check
elif "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        session = stripe.checkout.Session.retrieve(params["session_id"])
        if session.payment_status in ["paid", "no_payment_required"]:
            pack_size = int(params.get("pack", 1))
            st.session_state.credits += pack_size
            st.session_state.processed_sessions.append(params["session_id"])
            st.toast(f"✅ {pack_size} Analyse(n) freigeschaltet!")
            st.query_params.clear()
    except: pass

# --- 5. SIDEBAR ---
with st.sidebar:
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    if is_admin: st.warning("🔓 Admin-Zugriff aktiv")
    st.divider()
    st.subheader("💳 Guthaben laden")
    st.caption("Einmalzahlung • Kein Abo")
    packages = [("📄 1 Analyse", st.secrets["STRIPE_LINK_1"], "3,99 € | KEIN ABO"),
                ("🚀 Spar-Paket (3)", st.secrets["STRIPE_LINK_3"], "9,99 € | KEIN ABO"),
                ("💎 Sorglos-Paket (10)", st.secrets["STRIPE_LINK_10"], "19,99 € | KEIN ABO")]
    for title, link, sub in packages:
        st.markdown(f'<a href="{link}" target="_blank" class="buy-button"><b>{title}</b><br><small>{sub}</small></a>', unsafe_allow_html=True)

# --- 6. HAUPTSEITE ---
st.title("Amtsschimmel-Killer 📄🚀")
upload = st.file_uploader("Behörden-Dokument hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_v, col_a = st.columns([1, 1.5])
    with col_v:
        if upload.type == "application/pdf":
            try:
                imgs = convert_from_bytes(upload.getvalue(), dpi=72, first_page=1, last_page=1)
                st.image(imgs, use_container_width=True)
            except: st.info("Vorschau lädt...")
        else:
            st.image(upload, use_container_width=True)

    with col_a:
        if st.session_state.last_brief:
            # 1. Fristen-Box oben
            st.subheader("⚠️ Wichtige Fristen")
            st.markdown(f'<div class="frist-box">{st.session_state.last_fristen}</div>', unsafe_allow_html=True)
            
            # 2. Brief-Entwurf
            st.subheader("📝 Entwurf Antwortschreiben")
            st.markdown(st.session_state.last_brief)
            st.divider()
            
            c1, c2 = st.columns(2)
            # PDF DOWNLOAD
            with c1:
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("helvetica", style="B", size=14)
                    pdf.cell(0, 10, txt="WICHTIGE FRISTEN", ln=True)
                    pdf.set_font("helvetica", size=11)
                    clean_f = st.session_state.last_fristen.replace("€", "Euro").replace("–", "-").replace("✅", "OK")
                    pdf.multi_cell(0, 8, txt=clean_f.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.ln(10)
                    pdf.set_font("helvetica", style="B", size=14)
                    pdf.cell(0, 10, txt="ANTWORTSCHREIBEN", ln=True)
                    pdf.set_font("helvetica", size=11)
                    clean_b = st.session_state.last_brief.replace("€", "Euro").replace("–", "-").replace("✅", "OK")
                    pdf.multi_cell(0, 8, txt=clean_b.encode('latin-1', 'replace').decode('latin-1'))
                    st.download_button("📩 PDF laden", bytes(pdf.output()), "Amtsschimmel_Antwort.pdf", "application/pdf")
                except Exception as e: st.error(f"PDF-Fehler: {e}")
            
            # EXCEL DOWNLOAD
            with c2:
                try:
                    datum = datetime.now().strftime("%d.%m.%Y")
                    df = pd.DataFrame([
                        {"Datum": datum, "Bereich": "GEFUNDENE FRISTEN", "Inhalt": st.session_state.last_fristen},
                        {"Datum": datum, "Bereich": "ANTWORTSCHREIBEN", "Inhalt": st.session_state.last_brief}
                    ])
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Analyse')
                        ws = writer.sheets['Analyse']
                        ws.column_dimensions['A'].width = 15
                        ws.column_dimensions['B'].width = 25
                        ws.column_dimensions['C'].width = 110
                        for row in ws.iter_rows(min_row=2, max_col=3):
                            for cell in row:
                                cell.alignment = Alignment(wrap_text=True, vertical='top')
                    st.download_button("📊 Excel laden", buf.getvalue(), "Amtsschimmel_Analyse.xlsx")
                except Exception as e: st.error(f"Excel-Fehler: {e}")
            
            if st.button("🔄 Nächstes Dokument"):
                st.session_state.last_fristen = ""; st.session_state.last_brief = ""; st.rerun()

        elif st.session_state.credits > 0:
            if st.button("🚀 JETZT ANALYSIEREN"):
                with st.spinner("Anwalt-KI analysiert..."):
                    try:
                        extracted = get_text_hybrid(upload)
                        res = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[{"role": "system", "content": "Du bist Fachanwalt. STRUKTUR: Liste zuerst FRISTEN fett auf. Dann ein TRENNER Wort. Dann den BRIEF (min. 600 Wörter).\nAufbau:\nFRISTEN: [Inhalt]\nTRENNER\nBRIEF: [Inhalt]"},
                                      {"role": "user", "content": extracted}]
                        )
                        raw = res.choices[0].message.content
                        if "TRENNER" in raw:
                            st.session_state.last_fristen = raw.split("TRENNER")[0].replace("FRISTEN:", "").strip()
                            st.session_state.last_brief = raw.split("TRENNER")[1].replace("BRIEF:", "").strip()
                        else:
                            st.session_state.last_brief = raw
                            st.session_state.last_fristen = "Siehe Briefinhalt."
                        st.session_state.credits -= 1
                        st.rerun()
                    except Exception as e: st.error(f"KI-Fehler: {e}")
        else:
            st.warning("💳 Bitte lade dein Guthaben in der Sidebar auf (KEIN ABO).")

st.info("Hinweis: KI-basierte Analyse. Keine Rechtsberatung.")
