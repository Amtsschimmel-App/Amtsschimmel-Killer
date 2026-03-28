import streamlit as st
import openai
from PIL import Image
import pytesseract
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pandas as pd
import io

# 1. SEITEN-KONFIGURATION
st.set_page_config(
    page_title="Amtsschimmel Killer", 
    page_icon="icon_final_blau.png",
    layout="wide"
)

# 2. SICHERHEIT (Legacy Mode openai==0.28)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ API-Key fehlt in den Streamlit-Secrets!")

# ERWEITERTE FUNKTION: PDF ERSTELLEN (Jetzt mit Originaltext)
def create_pdf_output(erklaerung, antwort_text, original_text):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer: Komplette Analyse", ln=True)
    pdf.ln(5)
    
    # 1. Erklärung
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "1. Einfache Erklaerung:", ln=True)
    pdf.set_font("Helvetica", size=11)
    clean_erk = erklaerung.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    pdf.multi_cell(0, 8, txt=clean_erk.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(5)
    
    # 2. Antwort-Entwurf
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "2. Antwort-Entwurf:", ln=True)
    pdf.set_font("Helvetica", size=11)
    clean_ant = antwort_text.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    pdf.multi_cell(0, 8, txt=clean_ant.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(10)

    # 3. Das Original (Neu hinzugefügt!)
    pdf.add_page() # Neue Seite für das Original
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "3. Analysierter Originaltext (OCR-Scan):", ln=True)
    pdf.set_font("Helvetica", size=9) # Etwas kleinerer Text für das Original
    clean_orig = original_text.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    pdf.multi_cell(0, 5, txt=clean_orig.encode('latin-1', 'replace').decode('latin-1'))
    
    return bytes(pdf.output())

# LOGO
try:
    logo = Image.open("icon_final_blau.png")
    st.image(logo, width=150)
except:
    st.info("💡 Logo wird geladen...")

st.title("Amtsschimmel-Killer 📄🚀")
st.write("Verstehe Behördenbriefe & archiviere das Original.")
st.divider()

# 3. STRIPE & PRO-STATUS
params = st.query_params
ist_pro = params.get("payment") == "success"

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
        full_document_text = ""
        if upload.type == "application/pdf":
            with st.spinner('Lese alle PDF-Seiten ein...'):
                pdf_pages = convert_from_bytes(upload.read())
                for i, page in enumerate(pdf_pages):
                    page_text = pytesseract.image_to_string(page, lang='deu')
                    full_document_text += f"\n--- SEITE {i+1} ---\n{page_text}"
        else:
            image = Image.open(upload)
            st.image(image, caption="Dein Scan", width=300)
            full_document_text = pytesseract.image_to_string(image, lang='deu')

        if full_document_text and st.button("Dokument vollständig analysieren"):
            with st.spinner('KI analysiert den gesamten Inhalt...'):
                system_msg = "Du bist der Amtsschimmel-Killer. Antworte strukturiert."
                user_msg = f"Analysiere diesen Text:\n{full_document_text}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Aufgabe] | [Datum]\nFRISTEN_ENDE"
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg}
                    ]
                )
                
                full_res = response['choices'][0]['message']['content']

                # EXTRAKTION
                ex_erklaerung = ""
                if "ERKLÄRUNG_START" in full_res:
                    ex_erklaerung = full_res.split("ERKLÄRUNG_START")[1].split("ERKLÄRUNG_ENDE")[0].strip()
                    st.subheader("💡 Analyse-Ergebnis")
                    st.info(ex_erklaerung)

                if ist_pro:
                    st.divider()
                    # FRISTEN
                    if "FRISTEN_START" in full_res:
                        with st.expander("🗓️ Erkannte Fristen", expanded=True):
                            f_content = full_res.split("FRISTEN_START")[1].split("FRISTEN_ENDE")[0].strip()
                            lines = [line.split("|") for line in f_content.split("\n") if "|" in line]
                            if lines:
                                st.table(pd.DataFrame(lines, columns=["Aufgabe", "Datum"]))

                    # ANTWORT-ENTWURF & DOWNLOAD
                    if "ANTWORT_START" in full_res:
                        with st.expander("📝 Dein Aktions-Plan (Vollständiges PDF)", expanded=True):
                            ex_antwort = full_res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0].strip()
                            final_antwort = st.text_area("Entwurf anpassen:", value=ex_antwort, height=300)
                            
                            # GENERIERUNG MIT ORIGINAL-TEXT
                            pdf_bytes = create_pdf_output(ex_erklaerung, final_antwort, full_document_text)
                            st.download_button(
                                label="📥 Komplette Analyse + Original-Text speichern",
                                data=pdf_bytes,
                                file_name="Amtsschimmel_Vollanalyse.pdf",
                                mime="application/pdf"
                            )
                else:
                    st.warning("🔒 Schalte PRO frei für den vollständigen PDF-Export.")
    except Exception as e:
        st.error(f"Fehler: {e}")

st.divider()
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
