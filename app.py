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
    st.error("⚠️ OpenAI API-Key fehlt in den Streamlit Secrets!")

# FUNKTION: PDF ERSTELLEN (Unicode-Safe & Adobe-kompatibel)
def create_full_pdf(erk, fri, ant, ste):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo & Zeitstempel
    try:
        pdf.image("icon_final_blau.png", x=10, y=8, w=25)
    except:
        pass
    
    pdf.set_font("helvetica", size=9)
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(0, 10, f"Erstellt am: {zeit}", ln=1, align='R')
    pdf.ln(10)
    
    # Titel
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=1, align='C')
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    
    sections = [
        ("Zusammenfassung", erk),
        ("Wichtige Fristen", fri),
        ("Steuerliche Relevanz", ste),
        ("Antwort-Entwurf", ant)
    ]
    
    for title, content in sections:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"{title}:", ln=1)
        
        pdf.set_font("helvetica", size=11)
        # RADIKALER FIX FÜR ENCODING FEHLER:
        # Wir ersetzen alle Nicht-Latin-1 Zeichen manuell
        text = str(content)
        replacements = {
            '€': 'Euro', '„': '"', '“': '"', '”': '"', '‘': "'", '’': "'",
            '–': '-', '—': '-', '…': '...', '•': '*'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        # Jetzt sicher in Latin-1 konvertieren (Standard-PDF Kodierung)
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, txt=safe_text)
        pdf.ln(5)
    
    # Output als Bytes (Stabil für Adobe Acrobat)
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

# 4. ANALYSE
upload = st.file_uploader("Dokument hochladen (PDF, JPG, PNG)", type=['png', 'jpg', 'jpeg', 'pdf'])

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
                    messages=[{"role": "system", "content": "Du bist Behörden-Experte."},
                              {"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content

                def ext(s, e, src):
                    m = re.search(f"{s}(.*?){e}", src, re.DOTALL)
                    return m.group(1).strip() if m else ""

                erk, ant, fri, ste = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw), ext("ANTWORT_START", "ANTWORT_ENDE", raw), ext("FRISTEN_START", "FRISTEN_ENDE", raw), ext("STEUER_START", "STEUER_ENDE", raw)

                st.subheader("💡 Ergebnis")
                st.info(erk if erk else "Dokument erkannt.")

                if ist_pro:
                    st.divider()
                    
                    # Steuerdaten vorbereiten
                    df_steuer = None
                    if ste:
                        rows = [l.split("|") for l in ste.split("\n") if "|" in l]
                        if rows:
                            df_steuer = pd.DataFrame(rows, columns=["Betrag", "Kategorie", "Grund"])

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if df_steuer is not None:
                            st.write("💰 **Steuer-Check**")
                            st.dataframe(df_steuer, use_container_width=True)
                        if fri:
                            st.write("🗓️ **Fristen**")
                            st.info(fri)

                    with col2:
                        st.write("📝 **Export & Antwort**")
                        final_a = st.text_area("Entwurf:", value=ant, height=150)
                        
                        # PDF DOWNLOAD
                        pdf_bytes = create_full_pdf(erk, fri, final_a, ste)
                        st.download_button(label="📥 Analyse als PDF", data=pdf_bytes, file_name="Analyse.pdf", mime="application/pdf")
                        
                        # EXCEL DOWNLOAD
                        if df_steuer is not None:
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                                df_steuer.to_excel(wr, index=False, sheet_name='Steuer')
                                workbook, worksheet = wr.book, wr.sheets['Steuer']
                                # Styling & Auto-Width
                                fmt = workbook.add_format({'bold': True, 'bg_color': '#1E3A8A', 'font_color': 'white'})
                                for i, col in enumerate(df_steuer.columns):
                                    worksheet.write(0, i, col, fmt)
                                    worksheet.set_column(i, i, max(df_steuer[col].astype(str).map(len).max(), len(col)) + 5)
                            
                            st.download_button(label="📊 Steuer-Daten (Excel)", data=buf.getvalue(), file_name="Steuer_Check.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("🔒 PRO-Status erforderlich.")
    except Exception as e:
        st.error(f"Fehler: {e}")

st.caption("v3.3 - Stable Final Build")
