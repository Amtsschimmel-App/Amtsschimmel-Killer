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

# FUNKTION: PDF FÜR NUTZER ERSTELLEN
def create_pdf_output(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    clean_text = text.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    pdf.multi_cell(0, 10, txt=clean_text.encode('latin-1', 'replace').decode('latin-1'))
    return bytes(pdf.output())

# LOGO ANZEIGEN
try:
    logo = Image.open("icon_final_blau.png")
    st.image(logo, width=150)
except:
    st.info("💡 Logo wird geladen...")

st.title("Amtsschimmel-Killer 📄🚀")
st.write("Verstehe Behördenbriefe & PDFs in Sekunden.")
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
    st.caption("Version 1.4 - Stufe 3: Fristen-Check")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen (Bild oder PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        analysis_image = None
        if upload.type == "application/pdf":
            with st.spinner('PDF wird vorbereitet...'):
                pdf_pages = convert_from_bytes(upload.read(), first_page=1, last_page=1)
                if pdf_pages:
                    analysis_image = pdf_pages[0]
                    st.info("📄 PDF erkannt. Analysiere Seite 1...")
        else:
            analysis_image = Image.open(upload)
            st.image(analysis_image, caption="Dein Scan", width=300)

        if analysis_image and st.button("Dokument analysieren"):
            with st.spinner('Amtsschimmel wird gezähmt...'):
                try:
                    text_raw = pytesseract.image_to_string(analysis_image, lang='deu')
                except:
                    text_raw = pytesseract.image_to_string(analysis_image, lang='eng')
                
                if len(text_raw.strip()) < 10:
                    st.error("❌ Text nicht lesbar.")
                else:
                    # PROMPT FÜR STUFE 3 (Erklärung + Antwort + Fristen)
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Du bist der Amtsschimmel-Killer. Antworte IMMER strukturiert mit den Markern: ERKLÄRUNG_START, ERKLÄRUNG_ENDE, ANTWORT_START, ANTWORT_ENDE, FRISTEN_START, FRISTEN_ENDE."},
                            {"role": "user", "content": f"Analysiere:\n{text_raw}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Aufgabe] | [Datum]\nFRISTEN_ENDE"}
                        ]
                    )
                    
                    full_res = response['choices'][0]['message']['content']

                    # --- TEIL 1: ERKLÄRUNG ---
                    st.subheader("💡 Was bedeutet das?")
                    if "ERKLÄRUNG_START" in full_res:
                        st.info(full_res.split("ERKLÄRUNG_START")[1].split("ERKLÄRUNG_ENDE")[0].strip())

                    # --- TEIL 2: PRO-FUNKTIONEN ---
                    if ist_pro:
                        st.divider()
                        
                        # --- NEU: FRISTEN-TABELLE ---
                        st.subheader("🗓️ Deine Fristen-Übersicht")
                        if "FRISTEN_START" in full_res:
                            try:
                                fristen_raw = full_res.split("FRISTEN_START")[1].split("FRISTEN_ENDE")[0].strip()
                                lines = [line.split("|") for line in fristen_raw.split("\n") if "|" in line]
                                if lines:
                                    df = pd.DataFrame(lines, columns=["Aufgabe", "Datum"])
                                    st.table(df)
                                else:
                                    st.write("Keine konkreten Fristen gefunden.")
                            except:
                                st.write("Fristen konnten nicht formatiert werden.")

                        # --- ANTWORT-ENTWURF & PDF ---
                        st.subheader("📝 Antwort-Entwurf")
                        if "ANTWORT_START" in full_res:
                            antwort_text = full_res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0].strip()
                            final_text = st.text_area("Bearbeite den Entwurf:", value=antwort_text, height=300)
                            
                            pdf_bytes = create_pdf_output(final_text)
                            st.download_button(
                                label="📥 Antwort als PDF speichern",
                                data=pdf_bytes,
                                file_name="Amtsschimmel_Antwort.pdf",
                                mime="application/pdf"
                            )
                    else:
                        st.warning("🔒 Schalte PRO frei für Antwort-Entwürfe und Fristen-Checks.")

    except Exception as e:
        st.error(f"Fehler: {e}")

# 5. RECHTLICHES
st.divider()
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
