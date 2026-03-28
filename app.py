import streamlit as st
import openai
from PIL import Image
import pytesseract
from fpdf import FPDF
from pdf2image import convert_from_bytes
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
    # Sonderzeichen-Bereinigung für PDF-Export
    clean_text = text.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
    # Latin-1 Kodierung sicherstellen
    pdf.multi_cell(0, 10, txt=clean_text.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output()

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
    st.caption("Version 1.2 - Robust Split Logic")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen (Bild oder PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        analysis_image = None
        
        # PDF in Bild umwandeln
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
                # Texterkennung
                try:
                    text_raw = pytesseract.image_to_string(analysis_image, lang='deu')
                except:
                    text_raw = pytesseract.image_to_string(analysis_image, lang='eng')
                
                if len(text_raw.strip()) < 10:
                    st.error("❌ Dokument konnte nicht gelesen werden. Ist das Bild scharf?")
                else:
                    # OpenAI Aufruf
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Du bist der Amtsschimmel-Killer. Antworte IMMER mit den Markierungen ERKLÄRUNG_START, ERKLÄRUNG_ENDE, ANTWORT_START und ANTWORT_ENDE."},
                            {"role": "user", "content": f"Analysiere diesen Text:\n{text_raw}\n\nFormat:\nERKLÄRUNG_START\n[3 Sätze]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE"}
                        ]
                    )
                    
                    full_res = response['choices'][0]['message']['content']

                    # --- TEIL 1: ERKLÄRUNG (Robustes Splitting) ---
                    st.subheader("💡 Was bedeutet das?")
                    if "ERKLÄRUNG_START" in full_res and "ERKLÄRUNG_ENDE" in full_res:
                        erklaerung = full_res.split("ERKLÄRUNG_START")[1].split("ERKLÄRUNG_ENDE")[0].strip()
                        st.info(erklaerung)
                    else:
                        st.write("Analyse abgeschlossen. Hier ist die Zusammenfassung:")
                        st.info(full_res.split("ANTWORT_START")[0].strip())

                    # --- TEIL 2: PRO-FUNKTIONEN ---
                    if ist_pro:
                        st.divider()
                        st.subheader("🚀 PRO: Dein Aktions-Plan")
                        
                        # Extraktion des Antwort-Entwurfs
                        antwort_text = ""
                        if "ANTWORT_START" in full_res and "ANTWORT_ENDE" in full_res:
                            antwort_text = full_res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0].strip()
                        else:
                            # Fallback: Falls Markierungen fehlen, nimm den Rest ab ANTWORT_START
                            if "ANTWORT_START" in full_res:
                                antwort_text = full_res.split("ANTWORT_START")[1].strip()
                            else:
                                antwort_text = "Bitte fülle den Entwurf manuell aus oder versuche es erneut."

                        st.markdown("### 📝 Antwort-Entwurf")
                        final_text = st.text_area("Bearbeite den Entwurf:", value=antwort_text, height=300)
                        
                        if final_text:
                            pdf_bytes = create_pdf_output(final_text)
                            st.download_button(
                                label="📥 Antwort als PDF speichern",
                                data=pdf_bytes,
                                file_name="Amtsschimmel_Antwort.pdf",
                                mime="application/pdf"
                            )
                    else:
                        st.warning("🔒 Schalte PRO frei für Antwort-Entwürfe.")

    except Exception as e:
        st.error(f"Fehler: {e}")

# 5. RECHTLICHES
st.divider()
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
