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

# VERBESSERTE FUNKTION: PDF ERSTELLEN (Unterstützt jetzt mehr Text/Seiten)
def create_pdf_output(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    # Sonderzeichen-Bereinigung
    clean_text = text.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    
    # Text mit automatischem Zeilenumbruch hinzufügen
    # Falls der Text sehr lang ist, erstellt fpdf automatisch neue Seiten
    pdf.multi_cell(0, 10, txt=clean_text.encode('latin-1', 'replace').decode('latin-1'))
    
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
    st.caption("Version 1.6 - Full Multi-Page Support")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen (Bild oder PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_document_text = ""
        
        if upload.type == "application/pdf":
            with st.spinner('Lese alle PDF-Seiten ein...'):
                # Alle Seiten in Bilder umwandeln
                pdf_pages = convert_from_bytes(upload.read())
                st.info(f"📄 Dokument mit {len(pdf_pages)} Seiten erkannt.")
                
                # Jede Seite einzeln per OCR auslesen
                for i, page in enumerate(pdf_pages):
                    page_text = pytesseract.image_to_string(page, lang='deu')
                    full_document_text += f"\n--- SEITE {i+1} ---\n{page_text}"
        else:
            # Einzelbild-Verarbeitung
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

                # --- ANZEIGE: ERKLÄRUNG ---
                st.subheader("💡 Analyse-Ergebnis")
                if "ERKLÄRUNG_START" in full_res:
                    parts = full_res.split("ERKLÄRUNG_START")
                    content = parts[1].split("ERKLÄRUNG_ENDE")
                    st.info(content[0].strip())

                # --- PRO-BEREICH ---
                if ist_pro:
                    st.divider()
                    
                    # 🗓️ FRISTEN
                    with st.expander("🗓️ Erkannte Fristen", expanded=True):
                        if "FRISTEN_START" in full_res:
                            try:
                                f_parts = full_res.split("FRISTEN_START")
                                f_content = f_parts[1].split("FRISTEN_ENDE")[0].strip()
                                lines = [line.split("|") for line in f_content.split("\n") if "|" in line]
                                if lines:
                                    df = pd.DataFrame(lines, columns=["Aufgabe", "Datum"])
                                    st.table(df)
                                else:
                                    st.write("Keine Fristen gefunden.")
                            except:
                                st.write("Fristen konnten nicht extrahiert werden.")

                    # 📝 ANTWORT-ENTWURF (Wird als PDF zum Download angeboten)
                    with st.expander("📝 Dein Antwort-Entwurf (PDF Export)", expanded=True):
                        if "ANTWORT_START" in full_res:
                            a_parts = full_res.split("ANTWORT_START")
                            antwort_text = a_parts[1].split("ANTWORT_ENDE")[0].strip()
                            
                            final_text = st.text_area("Vervollständige den Entwurf hier:", value=antwort_text, height=300)
                            
                            # Hier wird das PDF generiert
                            pdf_bytes = create_pdf_output(final_text)
                            st.download_button(
                                label="📥 Antwort-Schreiben als PDF herunterladen",
                                data=pdf_bytes,
                                file_name="Amtsschimmel_Antwort.pdf",
                                mime="application/pdf"
                            )
                else:
                    st.warning("🔒 PRO freischalten für Antwort-Entwürfe und Fristen-Checks.")

    except Exception as e:
        st.error(f"Fehler bei der Verarbeitung: {e}")

# 5. RECHTLICHES
st.divider()
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
