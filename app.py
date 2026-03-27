import streamlit as st
import openai
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

import fitz

st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄")

try:
    st.image("logo.png", width=200)
except:
    pass

st.title("Amtsschimmel-Killer 📄🚀")
st.write("Verstehe Behördenbriefe in Sekunden.")

if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ API-Key fehlt in .streamlit/secrets.toml!")
    st.stop()

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

upload = st.file_uploader("Brief hochladen", type=["png", "jpg", "jpeg", "pdf"])

if upload:
    text_raw = ""
    if upload.type == "application/pdf":
        with fitz.open(stream=upload.read(), filetype="pdf") as doc:
            for page in doc:
                text_raw += page.get_text()
        st.success("PDF wurde eingelesen!")
    else:
        image = Image.open(upload)
        st.image(image, caption="Dein Scan", width=300)
        with st.spinner("Lese Text aus Bild..."):
            text_raw = pytesseract.image_to_string(image, lang='deu')

    if st.button("Brief analysieren"):
        if not text_raw.strip():
            st.warning("Kein Text gefunden!")
        else:
            with st.spinner('KI arbeitet...'):
                try:
                    # ACHTUNG: Hier darf kein Buchstabe fehlen!
                    mein_prompt = "Erkläre den Brief einfach, nenne Fristen fett und gib eine Schritt-für-Schritt-Anleitung."
                    
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": mein_prompt},
                            {"role": "user", "content": text_raw}
                        ]
                    )
                    st.subheader("Das steht drin:")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"KI-Fehler: {e}")
# ... dein vorheriger Code (Ende der Analyse-Logik)

st.divider()  # Eine Trennlinie für die Optik
st.markdown("### Rechtliches")

# Der direkte Link zu deiner PDF (Raw-Version für direktes Öffnen)
pdf_url = "https://raw.githubusercontent.com"
st.markdown(f"📄 [Datenschutzerklärung lesen]({pdf_url})")

st.caption("© 2026 Amtsschimmel-Killer | Keine Rechtsberatung")
