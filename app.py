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
    # Sonderzeichen-Bereinigung
    clean_text = text.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
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
    st.caption("Version 1.1 - PDF Fix & Logic Update")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen (Bild oder PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        # Variable für das zu analysierende Bild vorbereiten
        analysis_image = None
        
        # LOGIK: Falls es ein PDF ist, wandle die erste Seite in ein Bild um
        if upload.type == "application/pdf":
            with st.spinner('PDF wird vorbereitet...'):
                # PDF in Bilder umwandeln
                pdf_images = convert_from_bytes(upload.read(), first_page=1, last_page=1)
                if pdf_images:
                    analysis_image = pdf_images[0]
                    st.info("📄 PDF erkannt. Analysiere Seite 1...")
        else:
            # Normales Bild laden
            analysis_image = Image.open(upload)
            st.image(analysis_image, caption="Dein Scan", width=300)

        if analysis_image and st.button("Dokument analysieren"):
            with st.spinner('KI liest den Amtsschimmel...'):
                # Texterkennung (OCR)
                try:
                    text_raw = pytesseract.image_to_string(analysis_image, lang='deu')
                except:
                    text_raw = pytesseract.image_to_string(analysis_image, lang='eng')
                
                if len(text_raw.strip()) < 10:
                    st.error("❌ Dokument konnte nicht gelesen werden. Ist das Bild scharf?")
                else:
                    # OpenAI Aufruf (Fix für den 'list' Fehler)
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Du bist der Amtsschimmel-Killer. Antworte immer strukturiert."},
                            {"role": "user", "content": f"Analysiere diesen Text:\n{text_raw}\n\nFormat:\nERKLÄRUNG_START\n[3 einfache Sätze]\nERKLÄRUNG_ENDE\nANTWORT_START\n[Ein förmlicher Briefentwurf]\nANTWORT_ENDE"}
                        ]
                    )
                    
                    # KORREKTER ZUGRIFF auf die Antwort:
                    full_res = response['choices'][0]['message']['content']

                    # --- TEIL 1: ERKLÄRUNG ---
                    st.subheader("💡 Was bedeutet das?")
                    if "ERKLÄRUNG_START" in full_res:
                        try:
                            erklaerung = full_res.split("ERKLÄRUNG_START")[1].split("ERKLÄRUNG_ENDE")[0]
                            st.info(erklaerung.strip())
                        except:
                            st.write(full_res)
                    else:
                        st.write(full_res)

                    # --- TEIL 2: PRO-FUNKTIONEN ---
                    if ist_pro:
                        st.divider()
                        st.subheader("🚀 PRO: Dein Aktions-Plan")
                        
                        if "ANTWORT_START" in full_res:
                            try:
                                antwort_text = full_res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0].strip()
                                st.markdown("### 📝 Antwort-Entwurf")
                                final_text = st.text_area("Bearbeite den Entwurf:", value=antwort_text, height=300)
                                
                                # PDF Download
                                pdf_bytes = create_pdf_output(final_text)
                                st.download_button(
                                    label="📥 Antwort als PDF speichern",
                                    data=pdf_bytes,
                                    file_name="Amtsschimmel_Antwort.pdf",
                                    mime="application/pdf"
                                )
                            except:
                                st.warning("Fehler beim Extrahieren des Antwort-Entwurfs.")
                        else:
                            st.warning("Kein Antwort-Entwurf im Text gefunden.")
                    else:
                        st.warning("🔒 Schalte PRO frei für Antwort-Entwürfe.")

    except Exception as e:
        st.error(f"Fehler: {e}")

# 5. RECHTLICHES
st.divider()
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
