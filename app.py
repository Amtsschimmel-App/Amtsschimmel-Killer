import streamlit as st
import openai
from PIL import Image
import pytesseract
import pandas as pd
import json # Neu für saubere Daten

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
st.write("Verstehe Behördenbriefe in Sekunden.")
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
    st.caption("Version 0.2 - Beta")

# 4. BRIEF-ANALYSE
upload = st.file_uploader("Brief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    image = Image.open(upload)
    st.image(image, caption="Dein Scan", width=300)
    
    if st.button("Brief analysieren"):
        with st.spinner('KI analysiert den Amtsschimmel...'):
            try:
                text_raw = pytesseract.image_to_string(image, lang='deu')
                
                if len(text_raw.strip()) < 10:
                    st.error("❌ Text konnte nicht gelesen werden. Bitte Foto verbessern.")
                else:
                    # Verbesserter Prompt für strukturierte Daten
                    prompt = f"""
                    Analysiere diesen Behördenbrief. 
                    1. Erkläre den Inhalt in 3 einfachen Sätzen.
                    2. Erstelle eine Liste ALLER Fristen.
                    3. Gib die Fristen am Ende STRENG im JSON-Format aus: 
                    JSON_START {{"fristen": [{{"aufgabe": "...", "datum": "..."}}]}} JSON_END
                    
                    Brieftext: {text_raw}
                    """

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    ergebnis_text = response.choices[0].message.content
                    
                    # Trennung von Text und JSON-Daten
                    anzeige_text = ergebnis_text.split("JSON_START")[0]
                    st.subheader("Einfach erklärt:")
                    st.info(anzeige_text)

                    # PRO-FUNKTIONEN
                    if ist_pro:
                        st.divider()
                        st.subheader("🗓️ Deine Fristen-Übersicht (PRO)")
                        
                        # Versuche JSON-Daten für die Tabelle zu extrahieren
                        try:
                            json_str = ergebnis_text.split("JSON_START")[1].split("JSON_END")[0]
                            data = json.loads(json_str)
                            if data["fristen"]:
                                df = pd.DataFrame(data["fristen"])
                                st.table(df)
                                st.success("✅ Fristen erkannt und im Kalender-Format bereit.")
                            else:
                                st.write("Keine konkreten Fristen gefunden.")
                        except:
                            st.warning("Fristen konnten nicht tabellarisch erfasst werden.")

                        st.subheader("💡 Nächste Schritte")
                        st.write("Als Pro-Nutzer erhältst du bald hier vorgefertigte Antwortschreiben.")

            except Exception as e:
                st.error(f"Fehler: {e}")

# 5. RECHTLICHES
st.divider()
st.markdown("### Rechtliches")
st.markdown('[📄 Datenschutzerklärung](https://drive.google.com)', unsafe_allow_html=True)
st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung.")
