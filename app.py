import streamlit as st
import openai
from PIL import Image
import pytesseract
import pandas as pd
from fpdf import FPDF # Neu für Stufe 2
import io

# 1. SEITEN-KONFIGURATION
st.set_page_config(
    page_title="Amtsschimmel Killer", 
    page_icon="icon_final_blau.png",
    layout="wide"
)

# FUNKTION: PDF ERSTELLEN (Neu für Stufe 2)
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

# 2. SICHERHEIT (OpenAI Key)
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
        st.success("Abo aktiv: PRO-Status! 🎉")
    else:
        st.info("Basis-Modus")
        st.markdown("[👉 Jetzt Pro freischalten (2€)](https://buy.stripe.com)")
    
    st.divider()
    st.caption("Version 0.4 - Stufe 2: PDF Export")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    image = Image.open(upload)
    st.image(image, caption="Dein Scan", width=300)
    
    if st.button("Brief analysieren"):
        with st.spinner('KI arbeitet...'):
            try:
                text_raw = pytesseract.image_to_string(image, lang='deu')
                
                if len(text_raw.strip()) < 10:
                    st.error("❌ Text nicht lesbar.")
                else:
                    prompt = f"""
                    Du bist 'Amtsschimmel-Killer'. Analysiere:
                    ---
                    {text_raw}
                    ---
                    Erstelle:
                    1. ERKLÄRUNG: (3 einfache Sätze)
                    2. ANTWORT-ENTWURF: (Förmliches Schreiben mit Platzhaltern [NAME], [DATUM])
                    
                    Format:
                    ERKLÄRUNG_START
                    ...
                    ERKLÄRUNG_ENDE
                    ANTWORT_START
                    ...
                    ANTWORT_ENDE
                    """

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    full_res = response.choices[0].message.content

                    # --- TEIL 1: BASIS-ERKLÄRUNG ---
                    st.subheader("💡 Was bedeutet das?")
                    try:
                        erklaerung = full_res.split("ERKLÄRUNG_START")[1].split("ERKLÄRUNG_ENDE")[0]
                        st.info(erklaerung.strip())
                    except:
                        st.info(full_res)

                    # --- TEIL 2: PRO-FUNKTIONEN ---
                    if ist_pro:
                        st.divider()
                        st.subheader("🚀 PRO: Dein Aktions-Plan")
                        
                        try:
                            antwort_text = full_res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0].strip()
                            
                            # Textarea zur Ansicht
                            st.markdown("### 📝 Antwort-Entwurf")
                            final_text = st.text_area("Bearbeite den Text hier, falls nötig:", value=antwort_text, height=300)
                            
                            # PDF GENERIEREN BUTTON (Stufe 2)
                            pdf_data = create_pdf(final_text)
                            st.download_button(
                                label="📥 Als PDF herunterladen",
                                data=pdf_data,
                                file_name="Antwort_Amtsschimmel_Killer.pdf",
                                mime="application/pdf"
                            )
                            st.caption("Tipp: Das PDF kannst du direkt ausdrucken oder per E-Mail versenden.")
                            
                        except:
                            st.warning("Antwort konnte nicht erstellt werden.")
                    else:
                        st.warning("🔒 Schalte PRO frei für Antwort-Entwürfe und PDF-Download.")

            except Exception as e:
                st.error(f"Fehler: {e}")

# 5. RECHTLICHES
st.divider()
st.markdown("### Rechtliches")
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
