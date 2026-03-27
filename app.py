import streamlit as st
import openai
from PIL import Image
import pytesseract
import pandas as pd
import re

# 1. SEITEN-KONFIGURATION (Hier ist das blaue Icon!)
st.set_page_config(
    page_title="Amtsschimmel Killer", 
    page_icon="icon_final_blau.png",
    layout="wide"
)

# LOGO ANZEIGEN
try:
    # Nutzt jetzt auch das neue blaue Logo als Bild in der App
    logo = Image.open("icon_final_blau.png")
    st.image(logo, width=150)
except:
    st.info("💡 Logo wird geladen...")

st.title("Amtsschimmel-Killer 📄🚀")
st.write("Verstehe Behördenbriefe in Sekunden.")
st.divider()

# 2. SICHERHEIT (OpenAI Key aus den Streamlit Secrets)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ API-Key fehlt in den Streamlit-Secrets!")

# 3. STRIPE & PRO-STATUS (Scharfgeschaltet ohne Test-Modus)
params = st.query_params
ist_pro = params.get("payment") == "success"

with st.sidebar:
    st.header("✨ Account-Status")
    if ist_pro:
        st.success("Abo aktiv: PRO-Status! 🎉")
        st.balloons()
    else:
        st.info("Basis-Modus")
        # Dein Stripe-Link für die 2€ Zahlung
        st.markdown("[👉 Jetzt Pro freischalten (2€)](https://buy.stripe.com)")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    image = Image.open(upload)
    st.image(image, caption="Dein Scan", width=300)
    
    if st.button("Brief analysieren"):
        with st.spinner('KI analysiert...'):
            try:
                text_raw = pytesseract.image_to_string(image, lang='deu')
                if len(text_raw.strip()) < 10:
                    st.error("❌ Foto zu unscharf oder kein Text erkannt.")
                else:
                    system_msg = "Du bist Experte für Behördendeutsch und erklärst Briefe einfach."
                    user_msg = f"Erkläre einfach. Liste Fristen am Ende so: FRIST: [Aufgabe] | DATUM: [TT.MM.JJJJ]\n\nText: {text_raw}"

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_msg}, 
                            {"role": "user", "content": user_msg}
                        ]
                    )
                    ergebnis = response.choices[0].message.content
                    st.subheader("Einfach erklärt:")
                    st.info(ergebnis)

                    # PRO-FUNKTION: Fristen-Tabelle
                    if ist_pro:
                        st.divider()
                        st.subheader("🗓️ Deine Fristen (PRO)")
                        match = re.search(r"FRIST: (.*?) \| DATUM: (.*?)", ergebnis)
                        if match:
                            df = pd.DataFrame({
                                "Aufgabe": [match.group(1)], 
                                "Datum": [match.group(2).strip()]
                            })
                            st.table(df)
            except Exception as e:
                st.error(f"Fehler bei der Analyse: {e}")

# 5. RECHTLICHES
st.divider()
st.markdown("### Rechtliches")

# Link zu deiner PDF-Datenschutzerklärung auf Google Drive
pdf_url = "https://drive.google.com"
st.markdown(f'<a href="{pdf_url}" target="_blank">📄 Datenschutzerklärung (PDF)</a>', unsafe_allow_html=True)

st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung. Nutzung auf eigene Gefahr.")
