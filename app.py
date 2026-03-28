import streamlit as st
import openai
from PIL import Image
import pytesseract
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re

# 1. SEITEN-KONFIGURATION & DESIGN-INJECTION
st.set_page_config(
    page_title="Amtsschimmel Killer", 
    page_icon="icon_final_blau.png", 
    layout="wide"
)

# --- CSS FÜR DAS DESIGN ---
st.markdown("""
    <style>
    /* Hintergrund und Schrift */
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f1f4f9 100%);
    }
    
    /* Titel-Styling */
    h1 {
        color: #1e3a8a;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Karten-Design für Boxen */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #1e3a8a;
    }
    
    /* Button Design */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #1e3a8a;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
    }
    .stButton>button:hover {
        background-color: #3b82f6;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
    
    /* Tabellen Styling */
    .styled-table {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SICHERHEIT (Legacy Mode)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ API-Key fehlt!")

# FUNKTION: PDF ERSTELLEN
def create_full_pdf(erklaerung, fristen_text, antwort_text, original_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer: Vollstaendige Analyse", ln=True, align='C')
    pdf.ln(10)
    
    sections = [
        ("1. Zusammenfassung:", erklaerung),
        ("2. Wichtige Fristen:", fristen_text),
        ("3. Antwort-Entwurf:", antwort_text)
    ]
    
    for title, content in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Helvetica", size=11)
        text = content.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
        pdf.multi_cell(0, 8, txt=text.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "4. Analysierter Originaltext (Archiv):", ln=True)
    pdf.set_font("Helvetica", size=8)
    pdf.multi_cell(0, 5, txt=original_text.replace('€', 'Euro').encode('latin-1', 'replace').decode('latin-1'))
    return bytes(pdf.output())

# 3. UI-ELEMENTE
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("icon_final_blau.png", width=120)
    except:
        st.write("📄")
with col2:
    st.title("Amtsschimmel-Killer")
    st.write("_Behördenbriefe verstehen. Fristen sichern. Antworten schreiben._")

st.divider()

# PRO-STATUS CHECK
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    st.markdown("### 🛠️ Menü")
    if ist_pro:
        st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 **Jetzt Pro freischalten (2€)**](https://buy.stripe.com)")
    
    st.divider()
    st.caption("v2.3 | © 2026 Amtsschimmel-Killer")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("📂 Ziehe dein Dokument hierher (Bild oder PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_doc_text = ""
        if upload.type == "application/pdf":
            with st.spinner('📑 PDF-Seiten werden gescannt...'):
                pdf_pages = convert_from_bytes(upload.read())
                for i, page in enumerate(pdf_pages):
                    full_doc_text += f"\n--- SEITE {i+1} ---\n" + pytesseract.image_to_string(page, lang='deu')
        else:
            full_doc_text = pytesseract.image_to_string(Image.open(upload), lang='deu')

        if full_doc_text and st.button("🚀 Dokument jetzt analysieren"):
            with st.spinner('🧠 KI extrahiert Fakten...'):
                user_msg = f"Analysiere diesen Text:\n{full_doc_text}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Aufgabe] | [Datum]\nFRISTEN_ENDE"
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Du bist der Amtsschimmel-Killer."},
                              {"role": "user", "content": user_msg}]
                )
                res = response['choices']['message']['content']

                # ROBUSTE EXTRAKTION
                def extract(start, end, source):
                    pattern = f"{start}(.*?){end}"
                    match = re.search(pattern, source, re.DOTALL)
                    return match.group(1).strip() if match else ""

                erk = extract("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", res)
                ant = extract("ANTWORT_START", "ANTWORT_ENDE", res)
                fri = extract("FRISTEN_START", "FRISTEN_ENDE", res)

                # ANZEIGE
                st.subheader("💡 Die Analyse")
                st.info(erk if erk else "Text erfolgreich analysiert.")

                if ist_pro:
                    st.divider()
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.subheader("🗓️ Fristen")
                        if fri:
                            lines = [line.split("|") for line in fri.split("\n") if "|" in line]
                            if lines:
                                st.table(pd.DataFrame(lines, columns=["Aufgabe", "Datum"]))
                            else: st.write(fri)
                        else: st.write("Keine Fristen gefunden.")

                    with c2:
                        st.subheader("📝 Aktions-Plan")
                        final_ant = st.text_area("Entwurf anpassen:", value=ant, height=250)
                        pdf_data = create_full_pdf(erk, fri, final_ant, full_doc_text)
                        st.download_button(
                            label="📥 Vollständige Analyse (PDF)", 
                            data=pdf_data, 
                            file_name="Amtsschimmel_Vollanalyse.pdf", 
                            mime="application/pdf"
                        )
                else:
                    st.warning("🔒 PRO-Status erforderlich für Fristen & Antwortschreiben.")
    except Exception as e:
        st.error(f"Fehler: {e}")

st.divider()
st.caption("Keine Rechtsberatung. Nutzung auf eigene Gefahr.")
