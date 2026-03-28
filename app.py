import streamlit as st
import openai
from PIL import Image
import pytesseract
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re # Neu für robustere Suche

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel Killer", page_icon="icon_final_blau.png", layout="wide")

# 2. SICHERHEIT (Legacy Mode)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ API-Key fehlt!")

# FUNKTION: PDF ERSTELLEN (Inkl. Fristen-Sektion)
def create_full_pdf(erklaerung, fristen_text, antwort_text, original_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer: Vollstaendige Analyse", ln=True, align='C')
    pdf.ln(10)
    
    # Sektionen hinzufügen
    sections = [
        ("1. Zusammenfassung:", erklaerung, 11),
        ("2. Wichtige Fristen:", fristen_text, 11),
        ("3. Antwort-Entwurf:", antwort_text, 11)
    ]
    
    for title, content, size in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Helvetica", size=size)
        text = content.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
        pdf.multi_cell(0, 8, txt=text.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)

    # Archivseite
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "4. Analysierter Originaltext (Archiv):", ln=True)
    pdf.set_font("Helvetica", size=8)
    pdf.multi_cell(0, 5, txt=original_text.replace('€', 'Euro').encode('latin-1', 'replace').decode('latin-1'))
    
    return bytes(pdf.output())

# LOGO
try:
    st.image(Image.open("icon_final_blau.png"), width=150)
except:
    st.info("💡 Logo lädt...")

st.title("Amtsschimmel-Killer 📄🚀")
st.divider()

ist_pro = st.query_params.get("payment") == "success"

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen (Bild oder PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_doc_text = ""
        if upload.type == "application/pdf":
            with st.spinner('Lese alle Seiten des Dokuments...'):
                pdf_pages = convert_from_bytes(upload.read())
                for i, page in enumerate(pdf_pages):
                    full_doc_text += f"\n--- SEITE {i+1} ---\n" + pytesseract.image_to_string(page, lang='deu')
        else:
            full_doc_text = pytesseract.image_to_string(Image.open(upload), lang='deu')

        if full_doc_text and st.button("Dokument vollständig analysieren"):
            with st.spinner('KI erstellt die Vollanalyse...'):
                user_msg = f"Analysiere diesen Text:\n{full_doc_text}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Aufgabe] | [Datum]\nFRISTEN_ENDE"
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Du bist der Amtsschimmel-Killer."},
                              {"role": "user", "content": user_msg}]
                )
                res = response['choices'][0]['message']['content']

                # --- ROBUSTE EXTRAKTION ---
                def extract(start_token, end_token, source):
                    pattern = f"{start_token}(.*?){end_token}"
                    match = re.search(pattern, source, re.DOTALL)
                    return match.group(1).strip() if match else ""

                erk = extract("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", res)
                ant = extract("ANTWORT_START", "ANTWORT_ENDE", res)
                fri = extract("FRISTEN_START", "FRISTEN_ENDE", res)

                st.subheader("💡 Deine Analyse")
                st.info(erk if erk else "Analyse erfolgreich durchgeführt.")

                if ist_pro:
                    st.divider()
                    st.subheader("🚀 PRO: Aktions-Plan")
                    
                    # FRISTEN-TABELLE
                    with st.expander("🗓️ Erkannte Fristen", expanded=True):
                        if fri:
                            lines = [line.split("|") for line in fri.split("\n") if "|" in line]
                            if lines:
                                st.table(pd.DataFrame(lines, columns=["Aufgabe", "Datum"]))
                            else:
                                st.write(fri)
                        else:
                            st.write("Keine Fristen im Dokument gefunden.")

                    # ANTWORT & PDF
                    with st.expander("📝 Antwort-Entwurf & Voll-Download", expanded=True):
                        final_ant = st.text_area("Entwurf bearbeiten:", value=ant, height=300)
                        pdf_data = create_full_pdf(erk, fri, final_ant, full_doc_text)
                        st.download_button(label="📥 Vollständige Analyse als PDF speichern", 
                                           data=pdf_data, file_name="Amtsschimmel_Vollanalyse.pdf", mime="application/pdf")
    except Exception as e:
        st.error(f"Fehler: {e}")
