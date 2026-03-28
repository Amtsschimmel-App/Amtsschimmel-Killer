import streamlit as st
import openai
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

# FUNKTION: PDF ERSTELLEN
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Ersetzt Zeilenumbrüche für PDF-Kompatibilität
    multi_line_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=multi_line_text)
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

# 2. SICHERHEIT
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ API-Key fehlt in den Streamlit-Secrets!")

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
    st.caption("Version 0.5 - Bugfix PDF-Upload")

# 4. BRIEF-ANALYSE
# HINWEIS: Wir beschränken uns hier erst einmal auf Bilder, um den PIL-Fehler zu vermeiden
upload = st.file_uploader("Brief hochladen (Bilddatei)", type=['png', 'jpg', 'jpeg'])

if upload:
    try:
        # Sicherstellen, dass es ein Bild ist
        image = Image.open(upload)
        st.image(image, caption="Dein Scan", width=300)
        
        if st.button("Brief analysieren"):
            with st.spinner('KI arbeitet...'):
                # Texterkennung
                text_raw = pytesseract.image_to_string(image, lang='deu')
                
                if len(text_raw.strip()) < 10:
                    st.error("❌ Text nicht lesbar. Bitte Foto schärfer aufnehmen.")
                else:
                    prompt = f"""
                    Du bist 'Amtsschimmel-Killer'. Analysiere diesen Text:
                    ---
                    {text_raw}
                    ---
                    Erstelle:
                    1. ERKLÄRUNG: (3 einfache Sätze)
                    2. ANTWORT-ENTWURF: (Förmliches Schreiben mit Platzhaltern [NAME], [DATUM])
                    
                    Format:
                    ERKLÄRUNG_START
                    [Text]
                    ERKLÄRUNG_ENDE
                    ANTWORT_START
                    [Text]
                    ANTWORT_ENDE
                    """

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
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
                            # Textarea zum Bearbeiten
                            final_text = st.text_area("Hier kannst du den Entwurf anpassen:", value=antwort_text, height=300)
                            
                            # PDF Download
                            pdf_data = create_pdf(final_text)
                            st.download_button(
                                label="📥 Als PDF herunterladen",
                                data=pdf_data,
                                file_name="Antwort_Amtsschimmel_Killer.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.warning("Antwort konnte nicht separat erstellt werden.")
                    else:
                        st.divider()
                        st.warning("🔒 Schalte PRO frei für Antwort-Entwürfe und PDF-Download.")
    except Exception as e:
        st.error(f"Fehler beim Laden des Bildes: {e}")

# 5. RECHTLICHES
st.divider()
st.markdown("### Rechtliches")
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
