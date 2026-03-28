import streamlit as st
from openai import OpenAI
from PIL import Image
import pytesseract
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re
from datetime import datetime

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel Killer", page_icon="📄", layout="wide")

# 2. API INITIALISIERUNG
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("⚠️ OpenAI API-Key fehlt in den Secrets!")

# FUNKTION: PDF ERSTELLEN (Unicode-Safe & Adobe-kompatibel)
def create_full_pdf(erk, fri, ant, ste):
    # 'unit=mm' und Standard-Setup für maximale Kompatibilität
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # LOGO
    try:
        pdf.image("icon_final_blau.png", x=10, y=8, w=25)
    except:
        pass 
    
    # ZEITSTEMPEL
    pdf.set_font("helvetica", size=9)
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(0, 10, f"Erstellt am: {zeit}", align='R')
    pdf.ln(20)
    
    # TITEL
    pdf.set_font("helvetica", style="B", size=18)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", align='C')
    pdf.ln(15)
    pdf.set_text_color(0, 0, 0)
    
    sections = [
        ("Zusammenfassung", erk),
        ("Wichtige Fristen", fri),
        ("Steuerliche Relevanz", ste),
        ("Antwort-Entwurf", ant)
    ]
    
    for title, content in sections:
        # Titel-Zeile
        pdf.set_font("helvetica", style="B", size=12)
        pdf.cell(0, 10, f"{title}:", ln=1)
        
        # Inhalts-Text
        pdf.set_font("helvetica", size=11)
        # WICHTIG: .encode('latin-1', 'replace').decode('latin-1') löst das Encoding-Problem
        clean_text = str(content).replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
        safe_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.multi_cell(0, 8, txt=safe_text)
        pdf.ln(5)
    
    # WICHTIG für Adobe: Rückgabe als reine Bytes
    return bytes(pdf.output())

# 3. UI
st.title("Amtsschimmel-Killer 📄🚀")
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    if ist_pro:
        st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 Pro freischalten](https://buy.stripe.com)")

# 4. UPLOAD & ANALYSE
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
                    messages=[{"role": "system", "content": "Du bist ein erfahrener Steuer- und Behördenexperte."},
                              {"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content

                def ext(s, e, src):
                    m = re.search(f"{s}(.*?){e}", src, re.DOTALL)
                    return m.group(1).strip() if m else ""

                erk, ant, fri, ste = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw), ext("ANTWORT_START", "ANTWORT_ENDE", raw), ext("FRISTEN_START", "FRISTEN_ENDE", raw), ext("STEUER_START", "STEUER_ENDE", raw)

                st.subheader("💡 Analyse-Ergebnis")
                st.info(erk if erk else "Dokument verarbeitet.")

                if ist_pro:
                    st.divider()
                    
                    # DATEN-AUFBEREITUNG (Vor den Spalten!)
                    df_s = None
                    if ste:
                        rows = [l.split("|") for l in ste.split("\n") if "|" in l]
                        if rows:
                            df_s = pd.DataFrame(rows, columns=["Betrag", "Kategorie", "Grund"])

                    c1, c2 = st.columns(2)
                    
                    with c1:
                        if df_s is not None:
                            st.write("💰 **Steuer-Check**")
                            st.dataframe(df_s, use_container_width=True)
                        if fri:
                            st.write("🗓️ **Wichtige Fristen**")
                            st.info(fri)

                    with c2:
                        st.write("📝 **Export & Antwort**")
                        final_a = st.text_area("Entwurf bearbeiten:", value=ant, height=200)
                        
                        # PDF DOWNLOAD
                        try:
                            pdf_bytes = create_full_pdf(erk, fri, final_a, ste)
                            st.download_button("📥 Analyse als PDF", data=pdf_bytes, file_name="Amtsschimmel_Analyse.pdf", mime="application/pdf")
                        except Exception as e_pdf:
                            st.error(f"PDF-Fehler: {e_pdf}")
                        
                        # EXCEL DOWNLOAD (Sicher platziert)
                        if df_s is not None:
                            excel_buf = io.BytesIO()
                            with pd.ExcelWriter(excel_buf, engine='xlsxwriter') as writer:
                                df_s.to_excel(writer, index=False, sheet_name='Steuer_Check')
                                workbook = writer.book
                                worksheet = writer.sheets['Steuer_Check']
                                
                                # Styling
                                fmt = workbook.add_format({'bold': True, 'bg_color': '#1E3A8A', 'font_color': 'white'})
                                for i, col in enumerate(df_s.columns):
                                    worksheet.write(0, i, col, fmt)
                                    worksheet.set_column(i, i, max(df_s[col].astype(str).map(len).max(), len(col)) + 5)
                            
                            st.download_button("📊 Steuer-Export (Excel)", data=excel_buf.getvalue(), file_name="Steuer_Export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("🔒 PRO-Funktionen (PDF, Excel, Fristen) sind im Basis-Modus deaktiviert.")
    except Exception as e:
        st.error(f"Systemfehler: {e}")

st.caption("v3.0 - Unicode-Safe Build")
