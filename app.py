import streamlit as st
import openai
from PIL import Image
import pytesseract
import pandas as pd
import re

# 1. SEITEN-KONFIGURATION
st.set_page_config(
    page_title="Amtsschimmel Killer", 
    page_icon="icon_final_blau.png",
    layout="wide"
)

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
        st.balloons()
    else:
        st.info("Basis-Modus")
        st.markdown("[👉 Jetzt Pro freischalten (2€)](https://buy.stripe.com)")
    
    st.divider()
    st.caption("Version 0.3 - Stufe 1 Aktiv")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    image = Image.open(upload)
    st.image(image, caption="Dein Scan", width=300)
    
    if st.button("Brief analysieren"):
        with st.spinner('Amtsschimmel wird gezähmt...'):
            try:
                # Texterkennung via OCR
                text_raw = pytesseract.image_to_string(image, lang='deu')
                
                if len(text_raw.strip()) < 10:
                    st.error("❌ Foto zu unscharf oder kein Text erkannt.")
                else:
                    # KOMBINIERTER PROMPT (Erklärung + Antwort-Entwurf)
                    prompt = f"""
                    Du bist 'Amtsschimmel-Killer'. Analysiere diesen Text:
                    ---
                    {text_raw}
                    ---
                    Erstelle folgende Sektionen, getrennt durch Trennzeichen:
                    1. ERKLÄRUNG: (3 einfache Sätze für Laien)
                    2. ANTWORT-ENTWURF: (Verfasse ein förmliches Antwortschreiben an die Behörde. 
                       Nutze Platzhalter wie [DEIN NAME], [DATUM], [AKTENZEICHEN] etc.)
                    
                    Gib die Daten strikt so aus:
                    ERKLÄRUNG_START
                    [Hier die Erklärung]
                    ERKLÄRUNG_ENDE
                    
                    ANTWORT_START
                    [Hier der Briefentwurf]
                    ANTWORT_ENDE
                    """

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    full_res = response.choices[0].message.content

                    # --- TEIL 1: BASIS-ERKLÄRUNG (Für alle) ---
                    st.subheader("💡 Was bedeutet das?")
                    try:
                        erklaerung = full_res.split("ERKLÄRUNG_START")[1].split("ERKLÄRUNG_ENDE")[0]
                        st.info(erklaerung.strip())
                    except:
                        st.write(full_res) # Fallback, falls Split fehlschlägt

                    # --- TEIL 2: PRO-FUNKTIONEN (Antwort-Entwurf) ---
                    if ist_pro:
                        st.divider()
                        st.subheader("🚀 PRO: Dein Aktions-Plan")
                        
                        try:
                            antwort = full_res.split("ANTWORT_START")[1].split("ANTWORT_ENDE")[0]
                            st.markdown("### 📝 Antwort-Entwurf (Copy & Paste)")
                            st.text_area("Markiere und kopiere den Text für dein Schreiben:", 
                                         value=antwort.strip(), 
                                         height=400)
                            st.caption("⚠️ Hinweis: Dies ist ein Entwurf. Bitte ergänze deine persönlichen Daten.")
                            
                            st.info("💡 In Kürze verfügbar: Button 'Als PDF speichern' (Stufe 2).")
                        except:
                            st.warning("Antwort-Entwurf konnte nicht separat extrahiert werden.")
                    else:
                        st.divider()
                        st.warning("🔒 Antwort-Entwürfe und Fristen-Checks sind PRO-Features.")
                        st.info("Schalte PRO frei, um direkt einen fertigen Antwort-Entwurf zu erhalten.")

            except Exception as e:
                st.error(f"Fehler bei der Analyse: {e}")

# 5. RECHTLICHES
st.divider()
st.markdown("### Rechtliches")
pdf_url = "https://drive.google.com" # Dein Link
st.markdown(f'<a href="{pdf_url}" target="_blank">📄 Datenschutzerklärung (PDF)</a>', unsafe_allow_html=True)
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung. Nutzung auf eigene Gefahr.")
