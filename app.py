import streamlit as st
import openai
from PIL import Image
import pytesseract
import pandas as pd
import re

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄")

try:
    logo = Image.open("logo.png")
    st.image(logo, width=150)
except:
    st.info("💡 Tipp: Lade ein 'logo.png' hoch.")

st.title("Amtsschimmel-Killer 📄🚀")
st.write("Verstehe Behördenbriefe in Sekunden.")
st.divider()

# 2. SICHERHEIT
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ API-Key fehlt!")

# 3. STRIPE
params = st.query_params
kommt_von_stripe = params.get("payment") == "success"

with st.sidebar:
    st.header("✨ Account-Status")
    if kommt_von_stripe:
        ist_pro = True
        st.success("Abo aktiv: PRO-Status! 🎉")
    else:
        ist_pro = st.toggle("Pro-Funktionen (Test-Modus)", value=False)
    if not ist_pro:
        # HIER DEINEN STRIPE-LINK EINSETZEN (z.B. https://buy.stripe.com)
        st.markdown("[👉 Jetzt Pro freischalten (2€)](https://buy.stripe.com/4gM9AT1H51Iv7RC0KQ1gs00)")

# 4. ANALYSE
upload = st.file_uploader("Brief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    image = Image.open(upload)
    st.image(image, caption="Dein Scan", width=300)
    
    if st.button("Brief analysieren"):
        with st.spinner('KI analysiert...'):
            try:
                text_raw = pytesseract.image_to_string(image, lang='deu')
                if len(text_raw.strip()) < 10:
                    st.error("❌ Foto zu unscharf.")
                else:
                    system_msg = "Du bist Experte für Behördendeutsch."
                    user_msg = f"Erkläre einfach. Liste Fristen am Ende so: FRIST: [Aufgabe] | DATUM: [TT.MM.JJJJ]\n\nText: {text_raw}"

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
                    )
                    ergebnis = response.choices.message.content
                    st.subheader("Einfach erklärt:")
                    st.info(ergebnis)

                    if ist_pro:
                        st.divider()
                        st.subheader("🗓️ Deine Fristen (PRO)")
                        match = re.search(r"FRIST: (.*?) \| DATUM: (.*?)", ergebnis)
                        if match:
                            df = pd.DataFrame({"Aufgabe": [match.group(1)], "Datum": [match.group(2).strip()]})
                            st.table(df)
            except Exception as e:
                st.error(f"Fehler: {e}")

# 5. RECHTLICHES
st.divider()
st.markdown("### Rechtliches")

# DER KOMPLETTE LINK ZU DEINER PDF:
pdf_url = "https://drive.google.com/file/d/102IPPN6Gjwfg7Sovbc7pfo7y2Zq9YBMv/view"

st.markdown(f'<a href="{pdf_url}" target="_blank">📄 Datenschutzerklärung direkt öffnen (PDF)</a>', unsafe_allow_html=True)

st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung. Nutzung auf eigene Gefahr.")
