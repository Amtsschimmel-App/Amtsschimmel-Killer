import streamlit as st
import openai
from PIL import Image
import pytesseract
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pandas as pd
import io

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel Killer", page_icon="icon_final_blau.png", layout="wide")

# 2. SICHERHEIT (Legacy Mode openai==0.28)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ API-Key fehlt in den Streamlit-Secrets!")

# ERWEITERTE FUNKTION: PDF ERSTELLEN (Jetzt mit Originaltext-Archiv)
def create_full_pdf(erklaerung, antwort_text, original_text):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer: Vollstaendige Analyse", ln=True)
    pdf.ln(5)
    
    # Sektion 1: Erklaerung
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "1. Einfache Erklaerung:", ln=True)
    pdf.set_font("Helvetica", size=11)
    clean_erk = erklaerung.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    pdf.multi_cell(0, 8, txt=clean_erk.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(10)
    
    # Sektion 2: Antwort-Entwurf
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "2. Antwort-Entwurf:", ln=True)
    pdf.set_font("Helvetica", size=11)
    clean_ant = antwort_text.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    pdf.multi_cell(0, 8, txt=clean_ant.encode('latin-1', 'replace').decode('latin-1'))
    
    # Sektion 3: Originaldokument (Archivseite)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "3. Analysierter Originaltext (Archiv):", ln=True)
    pdf.set_font("Helvetica", size=8) # Kleinerer Text für das Archiv
    clean_orig = original_text.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    pdf.multi_cell(0, 5, txt=clean_orig.encode('latin-1', 'replace').decode('latin-1'))
    
    return bytes(pdf.output())

# LOGO ANZEIGEN
try:
    logo = Image.open("icon_final_blau.png")
    st.image(logo, width=150)
except:
    st.info("💡 Logo wird geladen...")

st.title("Amtsschimmel-Killer 📄🚀")
st.write("Verstehe Behördenbriefe & archiviere das Original.")
st.divider()

# 3. STRIPE & PRO-STATUS
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    st.header("✨ Account-Status")
    if ist_pro:
        st.success("PRO-Status aktiv! 🎉")
    else:
        st.info("Basis-Modus")
        st.markdown("[👉 Jetzt Pro freischalten (2€)](https://buy.stripe.com)")
    st.divider()
    st.caption("Version 2.0 - Full Report Export")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen (Bild oder PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_doc_text = ""
        if upload.type == "application/pdf":
            with st.spinner('Lese alle Seiten des Originalschreibens...'):
                pdf_pages = convert_from_bytes(upload.read())
                for i, page in enumerate(pdf_pages):
                    full_doc_text += f"\n--- SEITE {i+1} ---\n" + pytesseract.image_to_string(page, lang='deu')
        else:
            full_doc_text = pytesseract.image_to_string(Image.open(upload), lang='deu')

        if full_doc_text and st.button("Dokument vollständig analysieren"):
            with st.spinner('KI verarbeitet das gesamte Dokument...'):
                user_msg = f"Analysiere diesen Text:\n{full_doc_text}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Aufgabe] | [Datum]\nFRISTEN_ENDE"
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Du bist der Amtsschimmel-Killer."},
                              {"role": "user", "content": user_msg}]
                )
                res = response['choices']['message']['content']

                # Extraktion
                erk = res.split("ERKLÄRUNG_START")[1].split("ERKLÄRUNG_ENDE")[0].strip() if "ERKLÄRUNG_START" in res else ""
                ant = res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0].strip() if "ANTWORT_START" in res else ""
                
                st.subheader("💡 Deine Analyse")
                st.info(erk)

                if ist_pro:
                    st.divider()
                    st.subheader("🚀 PRO: Aktions-Plan")
                    with st.expander("📝 Antwort-Entwurf & Vollstaendiger PDF-Export", expanded=True):
                        final_ant = st.text_area("Entwurf anpassen:", value=ant, height=300)
                        
                        # Generiert das PDF mit ALLEN Infos
                        pdf_data = create_full_pdf(erk, final_ant, full_doc_text)
                        st.download_button(label="📥 Vollstaendige Analyse (inkl. Original-Text) speichern", 
                                           data=pdf_data, 
                                           file_name="Amtsschimmel_Vollanalyse.pdf", 
                                           mime="application/pdf")
    except Exception as e:
        st.error(f"Fehler: {e}")

st.divider()
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
