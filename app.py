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
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("⚠️ OpenAI API-Key fehlt!")

# FUNKTION: PDF ERSTELLEN (Ultra-Safe Version)
def create_full_pdf(erk, fri, ant, ste):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo & Zeitstempel
    try: pdf.image("icon_final_blau.png", x=10, y=8, w=25)
    except: pass
    
    pdf.set_font("Arial", size=9)
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(0, 10, f"Erstellt am: {zeit}", ln=1, align='R')
    pdf.ln(10)
    
    # Titel
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=1, align='C')
    pdf.ln(10)
    
    sections = [("Zusammenfassung", erk), ("Fristen", fri), ("Steuer", ste), ("Antwort", ant)]
    
    for title, content in sections:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{title}:", ln=1)
        
        pdf.set_font("Arial", size=11)
        
        # RADIKALER ENCODING-FIX: 
        # Wir entfernen alle Zeichen, die nicht in Standard-Latein-1 vorkommen
        text = str(content).replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
        # Alles was nicht Latin-1 ist, wird durch ein '?' ersetzt
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.multi_cell(0, 8, txt=safe_text)
        pdf.ln(5)
    
    # Rückgabe als Bytes
    return bytes(pdf.output())

# 3. UI
st.title("Amtsschimmel-Killer 📄🚀")
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    if ist_pro: st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 Pro freischalten](https://buy.stripe.com)")

# 4. ANALYSE
upload = st.file_uploader("Dokument hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_text = ""
        if upload.type == "application/pdf":
            with st.spinner('📑 Scanne PDF...'):
                pages = convert_from_bytes(upload.read())
                for page in pages:
                    full_text += pytesseract.image_to_string(page, lang='deu') + "\n"
        else:
            full_text = pytesseract.image_to_string(Image.open(upload), lang='deu')

        if full_text and st.button("🚀 Analyse starten"):
            with st.spinner('🧠 KI analysiert...'):
                prompt = f"Analysiere:\n{full_text}\n\nFormat: ERKLÄRUNG_START...ERKLÄRUNG_ENDE, ANTWORT_START...ANTWORT_ENDE, FRISTEN_START...FRISTEN_ENDE, STEUER_START...STEUER_ENDE (Trenner |)"
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Antworte präzise."},
                              {"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content

                def ext(s, e, src):
                    m = re.search(f"{s}(.*?){e}", src, re.DOTALL)
                    return m.group(1).strip() if m else ""

                erk, ant, fri, ste = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw), ext("ANTWORT_START", "ANTWORT_ENDE", raw), ext("FRISTEN_START", "FRISTEN_ENDE", raw), ext("STEUER_START", "STEUER_ENDE", raw)

                st.subheader("💡 Ergebnis")
                st.info(erk if erk else "Dokument analysiert.")

                if ist_pro:
                    st.divider()
                    df_steuer = None
                    if ste:
                        raw_lines = [l.strip() for l in ste.split("\n") if "|" in l]
                        rows = []
                        for line in raw_lines:
                            parts = [p.strip() for p in line.split("|")]
                            while len(parts) < 3: parts.append("-")
                            rows.append(parts[:3])
                        if rows: df_steuer = pd.DataFrame(rows, columns=["Betrag", "Kategorie", "Grund"])

                    c1, c2 = st.columns(2)
                    with c1:
                        if df_steuer is not None:
                            st.write("💰 **Steuer-Check**")
                            st.dataframe(df_steuer)
                        if fri:
                            st.write("🗓️ **Fristen**")
                            st.info(fri)

                    with c2:
                        st.write("📝 **Export**")
                        final_a = st.text_area("Entwurf:", value=ant, height=150)
                        
                        # PDF DOWNLOAD
                        pdf_bytes = create_full_pdf(erk, fri, final_a, ste)
                        st.download_button("📥 PDF Download", data=pdf_bytes, file_name="Analyse.pdf", mime="application/pdf")
                        
                        # EXCEL DOWNLOAD
                        if df_steuer is not None:
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                                df_steuer.to_excel(wr, index=False, sheet_name='Steuer')
                                workbook, worksheet = wr.book, wr.sheets['Steuer']
                                fmt = workbook.add_format({'bold': True, 'bg_color': '#1E3A8A', 'font_color': 'white'})
                                for i, col in enumerate(df_steuer.columns):
                                    worksheet.write(0, i, col, fmt)
                                    worksheet.set_column(i, i, max(df_steuer[col].astype(str).map(len).max(), len(col)) + 5)
                            st.download_button("📊 Excel Export", data=buf.getvalue(), file_name="Steuer.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("🔒 PRO-Status erforderlich.")
    except Exception as e:
        st.error(f"Fehler: {e}")

st.caption("v3.5 - Ultra Safe Build")
