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

# ==========================================
# 1. SETUP & OPTIK
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; }
        .paket-box { border: 2px solid #0d47a1; padding: 10px; border-radius: 10px; background-color: #f0f7ff; margin-bottom: 5px; text-align: center; }
        .stDownloadButton button { width: 100% !important; background-color: #e1f5fe; border: 1px solid #01579b; font-weight: bold; }
        .stLinkButton a { width: 100% !important; background-color: #0d47a1 !important; color: white !important; font-weight: bold; padding: 10px; border-radius: 8px; text-decoration: none; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# 2. ADMIN & SESSION STATE (999 SCANS)
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""

# Admin Modus via URL: ?admin=GeheimAmt2024!
if st.query_params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

# ==========================================
# 3. OBERE ZEILE: NEBENEINANDER (FIXIERT)
# ==========================================
st.title("Amtsschimmel-Killer 🪓")

top_col1, top_col2, top_col3, top_col4 = st.columns(4)

with top_col1:
    with st.expander("⚖️ Impressum", expanded=True):
        st.markdown("**Amtsschimmel-Killer**\nElisabeth Reinecke\nRingelsweide 9, 40223 Düsseldorf\n+49 211 15821329\namtsschimmel-killer@proton.me\n\nKeine Haftung für KI-Texte.")

with top_col2:
    with st.expander("🛡️ Datenschutz", expanded=True):
        st.markdown("1. DSGVO konform\n2. Hosting: Streamlit Cloud\n3. TLS-Verschlüsselung\n4. Keine Speicherung von Briefen.")

with top_col3:
    with st.expander("❓ FAQ", expanded=True):
        st.markdown("**Abo?** Nein! Einmalzahlung.\n**Sicherheit?** Dokumente werden gelöscht.\n**Recht?** Keine Rechtsberatung.")

with top_col4:
    with st.expander("📝 Vorlagen", expanded=True):
        st.markdown("**Frist:** Bitte um Verlängerung bis...\n**Widerspruch:** Hiermit lege ich Widerspruch ein...")

st.divider()

# ==========================================
# 4. HAUPTBEREICH (LINKS PAKETE | RECHTS APP)
# ==========================================
main_l, main_r = st.columns([1, 2.5])

with main_l:
    # Sprachen
    st.subheader("🌐 Sprachen")
    st.selectbox("Sprache wählen:", ["Deutsch", "English", "Türkçe", "Polski", "Русский", "العربية"])
    
    # Logo
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, width=200)
    
    # DIE STRIPE PAKETE (FEST VERANKERT)
    st.subheader("💰 Scans kaufen")
    
    # Paket 1
    st.markdown('<div class="paket-box"><b>📦 1. Paket</b><br>1 Scan für 3,99€<br><small>Einmalzahlung - Kein Abo</small></div>', unsafe_allow_html=True)
    st.link_button("1 Scan kaufen", "https://buy.stripe.com")
    
    # Paket 2
    st.markdown('<div class="paket-box"><b>📦 2. Paket</b><br>3 Scans für 9,99€<br><small>Einmalzahlung - Kein Abo</small></div>', unsafe_allow_html=True)
    st.link_button("3 Scans kaufen", "https://buy.stripe.com")
    
    # Paket 3
    st.markdown('<div class="paket-box"><b>📦 3. Paket</b><br>10 Scans für 19,99€<br><small>Einmalzahlung - Kein Abo</small></div>', unsafe_allow_html=True)
    st.link_button("10 Scans kaufen", "https://buy.stripe.com")

with main_r:
    st.subheader("📄 Analyse-Zentrum")
    st.info(f"Dein Guthaben: **{st.session_state.credits} Scans**")
    
    uploaded_file = st.file_uploader("Dokument hochladen", type=["pdf", "jpg", "png", "jpeg"])
    
    if uploaded_file and st.session_state.credits > 0:
        if st.button("🚀 JETZT ANALYSIEREN"):
            with st.spinner("Amtsschimmel wird verjagt..."):
                # OCR Logik
                text = ""
                if uploaded_file.type == "application/pdf":
                    with pdfplumber.open(uploaded_file) as pdf:
                        for page in pdf.pages: text += (page.extract_text() or "") + "\n"
                else:
                    text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
                
                # KI Analyse
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": "Analysiere: 🚦 WICHTIGKEIT, 📖 ZUSAMMENFASSUNG, 📅 FRISTEN, ✍️ ANTWORT-ENTWURF."},
                              {"role": "user", "content": text}]
                )
                st.session_state.full_res = response.choices.message.content
                st.session_state.credits -= 1
                st.rerun()

    # Ergebnis-Boxen
    if st.session_state.full_res:
        res = st.session_state.full_res
        st.divider()
        box1, box2 = st.columns(2)
        with box1: st.info(f"### 🚦 Wichtigkeit\n{re.search(r'🚦(.*?)(?=📖|$)', res, re.S).group(1) if '🚦' in res else 'Hoch'}")
        with box2: st.write(f"### 📖 Zusammenfassung\n{re.search(r'📖(.*?)(?=📅|$)', res, re.S).group(1) if '📖' in res else 'Inhalt analysiert.'}")
        
        box3, box4 = st.columns(2)
        with box3: st.warning(f"### 📅 Fristen\n{re.search(r'📅(.*?)(?=✍️|$)', res, re.S).group(1) if '📅' in res else 'Keine Fristen erkannt.'}")
        with box4: st.success(f"### ✍️ Antwort-Entwurf\n{re.search(r'✍️(.*)', res, re.S).group(1) if '✍️' in res else 'Entwurf bereit.'}")

        # DOWNLOADS GANZ UNTEN
        st.divider()
        st.subheader("📥 Downloads")
        d1, d2, d3, d4 = st.columns(4)
        
        # Hilfsfunktion PDF/Word/Excel
        def create_pdf_data(txt):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 10, txt.encode('latin-1', 'replace').decode('latin-1'))
            return pdf.output(dest='S').encode('latin-1')

        def create_excel_data(txt):
            dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', txt)
            df = pd.DataFrame({"Termine": dates if dates else ["Keine"], "Analyse": [txt]})
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return out.getvalue()

        with d1: st.download_button("📄 PDF", create_pdf_data(res), "Analyse.pdf")
        with d2: st.download_button("📝 Word", create_pdf_data(res), "Analyse.docx")
        with d3: st.download_button("📊 Excel", create_excel_data(res), "Fristen.xlsx")
        with d4: st.download_button("📅 Kalender", b"BEGIN:VCALENDAR\nEND:VCALENDAR", "Termin.ics")
