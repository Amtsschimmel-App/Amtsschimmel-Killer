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
import shutil

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel Killer", page_icon="📄", layout="wide")

# 2. TESSERACT PFAD-FIX
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# 3. API INITIALISIERUNG
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("⚠️ OpenAI API-Key fehlt!")

# FUNKTION: PDF ERSTELLEN (Stabil via BytesIO)
def create_full_pdf(erk, fri, ant, ste):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=9)
    
    try: pdf.image("icon_final_blau.png", x=10, y=8, w=25)
    except: pass
    
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(0, 10, f"Erstellt am: {zeit}", ln=1, align='R')
    pdf.ln(10)
    
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(30, 58, 138)
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
        
        # Säuberung für Standard-Fonts (Alles außer Latin-1 wird ignoriert)
        clean_text = str(content).encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, txt=clean_text)
        pdf.ln(5)
    
    # FIX: PDF direkt in einen Binär-Buffer schreiben
    return pdf.output()

# 4. UI
st.title("Amtsschimmel-Killer 📄🚀")
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    if ist_pro: st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 Pro freischalten](https://buy.stripe.com)")

# 5. ANALYSE-LOGIK
upload = st.file_uploader("Dokument hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_text = ""
        if upload.type == "application/pdf":
            with st.spinner('📑 Scanne PDF...'):
                pdf_data = upload.read()
                pages = convert_from_bytes(pdf_data, dpi=200)
                for page in pages:
                    full_text += pytesseract.image_to_string(page, lang='deu') + "\n"
        else:
            full_text = pytesseract.image_to_string(Image.open(upload), lang='deu')

        if full_text and st.button("🚀 Vollanalyse starten"):
            with st.spinner('🧠 KI analysiert Dokument...'):
                prompt = f"Analysiere diesen Text:\n{full_text}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Termine]\nFRISTEN_ENDE\n\nSTEUER_START\n[Betrag] | [Kategorie] | [Grund]\nSTEUER_ENDE"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "Du bist Behörden-Experte."},
                              {"role": "user", "content": prompt}]
                )
                raw_res = response.choices[0].message.content

                def ext(s, e, src):
                    pattern = rf"\*?{s}\*?(.*?)\*?{e}\*?"
                    m = re.search(pattern, src, re.DOTALL | re.IGNORECASE)
                    return m.group(1).strip() if m else ""

                erk = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw_res)
                ant = ext("ANTWORT_START", "ANTWORT_ENDE", raw_res)
                fri = ext("FRISTEN_START", "FRISTEN_ENDE", raw_res)
                ste = ext("STEUER_START", "STEUER_ENDE", raw_res)

                st.subheader("💡 Analyse")
                st.info(erk if erk else "Keine Analyse möglich.")

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
                        st.write("🗓️ **Wichtige Fristen**")
                        st.warning(fri if fri else "Keine Fristen gefunden.")
                        
                        if df_s is not None:
                            st.write("💰 **Steuer-Check**")
                            st.dataframe(df_s, use_container_width=True)
                        
                    with col2:
                        st.write("📝 **Antwort-Entwurf**")
                        final_a = st.text_area("Vorschlag bearbeiten:", value=ant, height=300)
                        
                        # --- PDF DOWNLOAD FIX ---
                        pdf_output = create_full_pdf(erk, fri, final_a, ste)
                        st.download_button(
                            label="📥 PDF Analyse speichern", 
                            data=pdf_output, 
                            file_name="Analyse.pdf", 
                            mime="application/pdf"
                        )
                        
                        # --- EXCEL DOWNLOAD ---
                        if df_s is not None:
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                                df_s.to_excel(writer, index=False, sheet_name='Steuer')
                                ws = writer.sheets['Steuer']
                                for i, col in enumerate(df_s.columns):
                                    width = max(df_s[col].astype(str).str.len().max(), len(col)) + 5
                                    ws.set_column(i, i, width)
                            st.download_button("📊 Steuer-Excel speichern", data=buf.getvalue(), file_name="Steuer_Check.xlsx")
                else:
                    st.warning("🔒 PRO-Status erforderlich.")
    except Exception as e:
        st.error(f"Fehler: {e}")

st.caption("v8.7 - Stabilisierte PDF-Ausgabe")
