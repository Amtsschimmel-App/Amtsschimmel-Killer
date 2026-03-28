import streamlit as st
import openai
from PIL import Image
import pytesseract
from fpdf import FPDF # Nutzt fpdf2
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

# FUNKTION: PDF ERSTELLEN (Optimiert für Stufe 2)
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    # Wir nutzen 'Helvetica' (Standard), da Arial manchmal Probleme macht
    pdf.set_font("Helvetica", size=12)
    
    # Text für PDF säubern (Umlaute-Fix)
    clean_text = text.replace('€', 'Euro').replace('„', '"').replace('“', '"')
    
    # Multi_cell schreibt den Text mit Zeilenumbruch
    pdf.multi_cell(0, 10, txt=clean_text)
    
    # PDF in den Speicher schreiben und als Bytes zurückgeben
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
    st.caption("Version 0.9 - PDF Export Aktiv")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen (Bilddatei)", type=['png', 'jpg', 'jpeg'])

if upload:
    try:
        image = Image.open(upload)
        st.image(image, caption="Dein Scan", width=300)
        
        if st.button("Brief analysieren"):
            with st.spinner('Amtsschimmel wird gezähmt...'):
                # Texterkennung
                try:
                    text_raw = pytesseract.image_to_string(image, lang='deu')
                except:
                    text_raw = pytesseract.image_to_string(image, lang='eng')
                
                if len(text_raw.strip()) < 10:
                    st.error("❌ Text nicht lesbar. Bitte Foto schärfer aufnehmen.")
                else:
                    # OpenAI Aufruf
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
                        st.info("Hier ist die Analyse deines Briefes:")
                        st.write(full_res)

                    # --- TEIL 2: PRO-FUNKTIONEN (Antwort & PDF) ---
                    if ist_pro:
                        st.divider()
                        st.subheader("🚀 PRO: Dein Aktions-Plan")
                        
                        if "ANTWORT_START" in full_res:
                            antwort_text = full_res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0].strip()
                            
                            st.markdown("### 📝 Antwort-Entwurf")
                            # Der Nutzer kann den Text hier noch anpassen
                            final_text = st.text_area("Bearbeite den Entwurf (z.B. Name ergänzen):", value=antwort_text, height=300)
                            
                            # PDF Download Button
                            pdf_output = create_pdf(final_text)
                            st.download_button(
                                label="📥 Als PDF herunterladen",
                                data=pdf_output,
                                file_name="Antwort_Amtsschimmel_Killer.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.warning("Antwort-Entwurf konnte nicht generiert werden.")
                    else:
                        st.divider()
                        st.warning("🔒 Schalte PRO frei für Antwort-Entwürfe und PDF-Download.")

    except Exception as e:
        st.error(f"Fehler: {e}")

# 5. RECHTLICHES
st.divider()
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
