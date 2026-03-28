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
    st.caption("Version 1.5 - Multi-Page Update")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen (Bild oder PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        text_raw = ""
        
        # VERFEINERUNG: PDF-VERARBEITUNG FÜR ALLE SEITEN
        if upload.type == "application/pdf":
            with st.spinner('PDF wird komplett eingelesen (alle Seiten)...'):
                pdf_pages = convert_from_bytes(upload.read())
                st.info(f"📄 PDF mit {len(pdf_pages)} Seite(n) erkannt.")
                for i, page in enumerate(pdf_pages):
                    page_text = pytesseract.image_to_string(page, lang='deu')
                    text_raw += f"\n--- SEITE {i+1} ---\n" + page_text
        else:
            # Bildverarbeitung
            image = Image.open(upload)
            st.image(image, caption="Dein Scan", width=300)
            text_raw = pytesseract.image_to_string(image, lang='deu')

        if text_raw and st.button("Dokument jetzt analysieren"):
            with st.spinner('KI analysiert den gesamten Inhalt...'):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Du bist der Amtsschimmel-Killer. Antworte IMMER mit den Markern: ERKLÄRUNG_START, ERKLÄRUNG_ENDE, ANTWORT_START, ANTWORT_ENDE, FRISTEN_START, FRISTEN_ENDE."},
                        {"role": "user", "content": f"Analysiere diesen Text (kann mehrere Seiten enthalten):\n{text_raw}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Aufgabe] | [Datum]\nFRISTEN_ENDE"}
                    ]
                )
                
                full_res = response['choices'][0]['message']['content']

                # --- AUSGABE: ERKLÄRUNG ---
                st.subheader("💡 Was bedeutet das?")
                if "ERKLÄRUNG_START" in full_res:
                    st.info(full_res.split("ERKLÄRUNG_START")[1].split("ERKLÄRUNG_ENDE")[0].strip())
                else:
                    st.write("Analyse vollständig. Details siehe unten.")

                # --- PRO-BEREICH ---
                if ist_pro:
                    st.divider()
                    
                    # 🗓️ FRISTEN (In einem Expander für bessere Übersicht)
                    with st.expander("🗓️ Deine Fristen-Übersicht", expanded=True):
                        if "FRISTEN_START" in full_res:
                            try:
                                fristen_raw = full_res.split("FRISTEN_START")[1].split("FRISTEN_ENDE")[0].strip()
                                lines = [line.split("|") for line in fristen_raw.split("\n") if "|" in line]
                                if lines:
                                    df = pd.DataFrame(lines, columns=["Aufgabe", "Datum"])
                                    st.table(df)
                                else:
                                    st.write("Keine konkreten Fristen im Dokument gefunden.")
                            except:
                                st.write("Fristen-Formatierung fehlgeschlagen.")

                    # 📝 ANTWORT-ENTWURF
                    with st.expander("📝 Dein Antwort-Entwurf & PDF", expanded=True):
                        if "ANTWORT_START" in full_res:
                            antwort_text = full_res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0].strip()
                            final_text = st.text_area("Hier Text ergänzen (z.B. dein Name):", value=antwort_text, height=300)
                            
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
