import streamlit as st
import openai  # Wir nutzen hier wieder die klassische Schreibweise
from PIL import Image
import pytesseract
import pandas as pd
from fpdf import FPDF
import io

# 1. SEITEN-KONFIGURATION
st.set_page_config(
    page_title="Amtsschimmel Killer", 
    page_icon="icon_final_blau.png",
    layout="wide"
)

# 2. SICHERHEIT (OpenAI Key aus den Streamlit Secrets)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ API-Key fehlt in den Streamlit-Secrets!")

# FUNKTION: PDF ERSTELLEN
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Sonderzeichen-Fix für PDF
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output()

# LOGO ANZEIGEN
try:
    logo = Image.open("icon_final_blau.png")
    st.image(logo, width=150)
except:
    st.info("💡 Logo wird geladen...")

st.title("Amtsschimmel-Killer 📄🚀")
st.write("Verstehe Behördenbriefe in Sekunden und reagiere sofort.")
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
    st.caption("Version 0.8 - Stable Legacy Mode")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen (Bilddatei)", type=['png', 'jpg', 'jpeg'])

if upload:
    try:
        image = Image.open(upload)
        st.image(image, caption="Dein Scan", width=300)
        
        if st.button("Brief analysieren"):
            with st.spinner('Amtsschimmel wird gezähmt...'):
                # Texterkennung (OCR)
                try:
                    text_raw = pytesseract.image_to_string(image, lang='deu')
                except:
                    text_raw = pytesseract.image_to_string(image, lang='eng')
                
                if len(text_raw.strip()) < 10:
                    st.error("❌ Text nicht lesbar. Bitte Foto schärfer aufnehmen.")
                else:
                    # Klassischer OpenAI Aufruf für Version 0.28
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Du bist der Amtsschimmel-Killer."},
                            {"role": "user", "content": f"Analysiere diesen Text:\n{text_raw}\n\nFormat:\nERKLÄRUNG_START\n[3 Sätze]\nERKLÄRUNG_ENDE\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE"}
                        ]
                    )
                    full_res = response.choices[0].message.content

                    # --- TEIL 1: BASIS-ERKLÄRUNG ---
                    st.subheader("💡 Was bedeutet das?")
                    if "ERKLÄRUNG_START" in full_res:
                        erklaerung = full_res.split("ERKLÄRUNG_START")[1].split("ERKLÄRUNG_ENDE")[0]
                        st.info(erklaerung.strip())
                    else:
                        st.info(full_res)

                    # --- TEIL 2: PRO-FUNKTIONEN ---
                    if ist_pro:
                        st.divider()
                        st.subheader("🚀 PRO: Dein Aktions-Plan")
                        
                        if "ANTWORT_START" in full_res:
                            antwort_text = full_res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0].strip()
                            st.markdown("### 📝 Antwort-Entwurf")
                            final_text = st.text_area("Hier kannst du den Entwurf anpassen:", value=antwort_text, height=300)
                            
                            pdf_data = create_pdf(final_text)
                            st.download_button(
                                label="📥 Als PDF herunterladen",
                                data=bytes(pdf_data),
                                file_name="Antwort_Amtsschimmel.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.warning("Antwort konnte nicht separat erstellt werden.")
                    else:
                        st.divider()
                        st.warning("🔒 Schalte PRO frei für Antwort-Entwürfe.")
    except Exception as e:
        st.error(f"Fehler: {e}")

# 5. RECHTLICHES
st.divider()
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
