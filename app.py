import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re
from datetime import datetime

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel Killer", page_icon="📄", layout="wide")

# 2. API INITIALISIERUNG
# Nutzt st.secrets für Streamlit Cloud oder lokale .streamlit/secrets.toml
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("⚠️ OpenAI API-Key fehlt! Bitte in den Secrets hinterlegen.")

# FUNKTION: PDF ERSTELLEN (Optimiert mit fpdf2 für Unicode/Euro)
def create_full_pdf(erk, fri, ant, ste):
    pdf = FPDF()
    pdf.add_page()
    
    # Standard-Schriftarten unterstützen Unicode in fpdf2 meist besser
    pdf.set_font("helvetica", size=9)
    
    # Logo & Zeitstempel
    try: 
        # Falls das Logo lokal nicht existiert, wird dieser Block übersprungen
        pdf.image("icon_final_blau.png", x=10, y=8, w=25)
    except: 
        pass
    
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(0, 10, f"Erstellt am: {zeit}", ln=1, align='R')
    pdf.ln(10)
    
    # Titel
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(30, 58, 138) # Dunkelblau
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=1, align='C')
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    
    sections = [
        ("Zusammenfassung", erk),
        ("Wichtige Fristen", fri),
        ("Steuerliche Relevanz", ste),
        ("Antwort-Vorschlag", ant)
    ]
    
    for title, content in sections:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"{title}:", ln=1)
        pdf.set_font("helvetica", size=11)
        
        # Inhalt säubern (Sonderzeichen-Fix für Standard-Fonts)
        clean_text = content.replace('€', 'Euro').replace('„', '"').replace('“', '"')
        pdf.multi_cell(0, 8, txt=clean_text)
        pdf.ln(5)
    
    # WICHTIG: .output() gibt bei fpdf2 direkt bytes zurück
    return pdf.output()

# 3. UI DESIGN
st.title("Amtsschimmel-Killer 📄🚀")
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    if ist_pro: 
        st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 Pro freischalten](https://buy.stripe.com)")
    st.divider()
    st.caption("Version 8.1 - Unicode Stable")

# 4. ANALYSE-LOGIK
upload = st.file_uploader("Dokument hochladen (PDF oder Bild)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_text = ""
        if upload.type == "application/pdf":
            with st.spinner('📑 Scanne PDF...'):
                # DPI auf 200 für bessere Performance
                pages = convert_from_bytes(upload.read(), dpi=200)
                for page in pages:
                    full_text += pytesseract.image_to_string(page, lang='deu') + "\n"
        else:
            full_text = pytesseract.image_to_string(Image.open(upload), lang='deu')

        if full_text and st.button("🚀 Vollanalyse starten"):
            with st.spinner('🧠 KI analysiert Dokument...'):
                # Prompt an GPT-4o-mini (besser & günstiger)
                prompt = f"Analysiere diesen Text:\n{full_text}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Termine]\nFRISTEN_ENDE\n\nSTEUER_START\n[Betrag] | [Kategorie] | [Grund]\nSTEUER_ENDE"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini", # Upgrade von 3.5-turbo
                    messages=[
                        {"role": "system", "content": "Du bist Experte für Behörden. Antworte strukturiert."},
                        {"role": "user", "content": prompt}
                    ]
                )
                raw_res = response.choices[0].message.content

                # Extraktion mit flexibler Regex (erkennt auch **STEUER_START**)
                def ext(s, e, src):
                    pattern = rf"\*?{s}\*?(.*?)\*?{e}\*?"
                    m = re.search(pattern, src, re.DOTALL | re.IGNORECASE)
                    return m.group(1).strip() if m else ""

                erk = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw_res)
                ant = ext("ANTWORT_START", "ANTWORT_ENDE", raw_res)
                fri = ext("FRISTEN_START", "FRISTEN_ENDE", raw_res)
                ste = ext("STEUER_START", "STEUER_ENDE", raw_res)

                st.subheader("💡 Analyse")
                st.info(erk if erk else "Analyse fehlgeschlagen.")

                if ist_pro:
                    st.divider()
                    df_s = None
                    if ste:
                        raw_lines = [l.strip() for l in ste.split("\n") if "|" in l]
                        rows = [line.split("|") for line in raw_lines]
                        if rows:
                            rows = [r + ["-"] * (3 - len(r)) for r in rows]
                            df_s = pd.DataFrame([r[:3] for r in rows], columns=["Betrag", "Kategorie", "Grund"])

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("💰 **Steuer-Check**")
                        if df_s is not None: st.dataframe(df_s, use_container_width=True)
                        else: st.write("Keine Beträge erkannt.")
                        
                        st.write("🗓️ **Wichtige Fristen**")
                        st.warning(fri if fri else "Keine Fristen gefunden.")

                    with col2:
                        st.write("📝 **Antwort-Entwurf**")
                        final_ant = st.text_area("Vorschlag bearbeiten:", value=ant, height=300)
                        
                        # PDF DOWNLOAD (Nutzt die korrigierte Bytes-Ausgabe)
                        pdf_data = create_full_pdf(erk, fri, final_ant, ste)
                        st.download_button(
                            label="📥 PDF Analyse herunterladen",
                            data=pdf_data,
                            file_name=f"Analyse_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                        
                        if df_s is not None:
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                                df_s.to_excel(writer, index=False, sheet_name='Steuer')
                            st.download_button("📊 Excel-Export", data=buf.getvalue(), file_name="Steuerdaten.xlsx")
                else:
                    st.warning("🔒 Upgrade auf PRO für PDF-Export und Steuer-Details.")
                    
    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")
