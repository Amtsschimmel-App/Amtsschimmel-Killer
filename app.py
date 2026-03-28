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

# FUNKTION: PDF ERSTELLEN (Jetzt mit besserer Struktur für den Export)
def create_pdf_output(erklaerung, antwort_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=True)
    pdf.ln(5)
    
    # Sektion 1: Erklärung
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "1. Einfache Erklaerung:", ln=True)
    pdf.set_font("Helvetica", size=11)
    # Text-Säuberung
    clean_erklaerung = erklaerung.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    pdf.multi_cell(0, 8, txt=clean_erklaerung.encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.ln(10)
    
    # Sektion 2: Antwort-Entwurf
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "2. Antwort-Entwurf:", ln=True)
    pdf.set_font("Helvetica", size=11)
    clean_antwort = antwort_text.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    pdf.multi_cell(0, 8, txt=clean_antwort.encode('latin-1', 'replace').decode('latin-1'))
    
    return bytes(pdf.output())

# LOGO ANZEIGEN
try:
    logo = Image.open("icon_final_blau.png")
    st.image(logo, width=150)
except:
    st.info("💡 Logo wird geladen...")

st.title("Amtsschimmel-Killer 📄🚀")
st.write("Verstehe Behördenbriefe & mehrseitige PDFs in Sekunden.")
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
    st.caption("Version 1.7 - Enhanced PDF Export")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen (Bild oder PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_document_text = ""
        
        if upload.type == "application/pdf":
            with st.spinner('Lese alle PDF-Seiten ein...'):
                pdf_pages = convert_from_bytes(upload.read())
                st.info(f"📄 Dokument mit {len(pdf_pages)} Seiten erkannt.")
                for i, page in enumerate(pdf_pages):
                    page_text = pytesseract.image_to_string(page, lang='deu')
                    full_document_text += f"\n--- SEITE {i+1} ---\n{page_text}"
        else:
            image = Image.open(upload)
            st.image(image, caption="Dein Scan", width=300)
            full_document_text = pytesseract.image_to_string(image, lang='deu')

        if full_document_text and st.button("Gesamtes Dokument analysieren"):
            with st.spinner('KI analysiert den gesamten Text...'):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Aufgabe] | [Datum]\nFRISTEN_ENDE"}
                    ]
                )
                
                full_res = response['choices']['message']['content']

                # --- EXTRAKTION ---
                final_erklaerung = ""
                if "ERKLÄRUNG_START" in full_res:
                    final_erklaerung = full_res.split("ERKLÄRUNG_START")[1].split("ERKLÄRUNG_ENDE")[0].strip()
                
                # --- ANZEIGE: ERKLÄRUNG ---
                st.subheader("💡 Analyse-Ergebnis")
                if final_erklaerung:
                    st.info(final_erklaerung)

                # --- PRO-BEREICH ---
                if ist_pro:
                    st.divider()
                    
                    # 🗓️ FRISTEN
                    with st.expander("🗓️ Erkannte Fristen", expanded=True):
                        if "FRISTEN_START" in full_res:
                            try:
                                f_content = full_res.split("FRISTEN_START")[1].split("FRISTEN_ENDE")[0].strip()
                                lines = [line.split("|") for line in f_content.split("\n") if "|" in line]
                                if lines:
                                    df = pd.DataFrame(lines, columns=["Aufgabe", "Datum"])
                                    st.table(df)
                            except:
                                st.write("Keine Fristen gefunden.")

                    # 📝 ANTWORT-ENTWURF & PDF
                    with st.expander("📝 Dein Aktions-Plan (PDF Export)", expanded=True):
                        if "ANTWORT_START" in full_res:
                            antwort_raw = full_res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0].strip()
                            
                            # Nutzer kann hier den Antwort-Text bearbeiten
                            final_antwort = st.text_area("Vervollständige den Entwurf:", value=antwort_raw, height=300)
                            
                            # Generiere PDF aus BEIDEN Teilen
                            pdf_bytes = create_pdf_output(final_erklaerung, final_antwort)
                            
                            st.download_button(
                                label="📥 Komplette Analyse als PDF herunterladen",
                                data=pdf_bytes,
                                file_name="Amtsschimmel_Killer_Analyse.pdf",
                                mime="application/pdf"
                            )
                else:
                    st.warning("🔒 PRO freischalten für Antwort-Entwürfe und PDF-Export.")

    except Exception as e:
        st.error(f"Fehler bei der Verarbeitung: {e}")

# 5. RECHTLICHES
st.divider()
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
