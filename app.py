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

# FUNKTION: PDF ERSTELLEN (UTF-8 Safe & Adobe-kompatibel)
def create_full_pdf(erk, fri, ant, ste):
    # Wir nutzen fpdf2 im Unicode-Modus (Standard bei fpdf2)
    pdf = FPDF()
    pdf.add_page()
    
    # Logo & Zeitstempel
    try: pdf.image("icon_final_blau.png", x=10, y=8, w=25)
    except: pass
    
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
        # RADIKALER FIX: Wir entfernen nur das Euro-Zeichen (wird oft nicht unterstützt)
        # Ansonsten lassen wir den String als reines UTF-8 stehen.
        safe_text = str(content).replace('€', 'Euro').replace('„', '"').replace('“', '"')
        
        # WICHTIG: multi_cell in fpdf2 verarbeitet Python-Strings direkt als UTF-8
        pdf.multi_cell(0, 8, txt=safe_text)
        pdf.ln(5)
    
    # Output als Bytes für den Download-Button
    return bytes(pdf.output())

# 3. UI
st.title("Amtsschimmel-Killer 📄🚀")
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    if ist_pro: st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 Pro freischalten](https://buy.stripe.com)")

# 4. ANALYSE-LOGIK
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
                prompt = f"Analysiere:\n{full_text}\n\nFormat: ERKLÄRUNG_START...ERKLÄRUNG_ENDE, ANTWORT_START...ANTWORT_ENDE, FRISTEN_START...FRISTEN_ENDE, STEUER_START\n[Betrag] | [Kategorie] | [Grund]\nSTEUER_ENDE"
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Du bist Behörden-Experte. Trenne Steuerdaten immer mit |."},
                              {"role": "user", "content": prompt}]
                )
                raw_res = response.choices[0].message.content

                def ext(s, e, src):
                    m = re.search(f"{s}(.*?){e}", src, re.DOTALL)
                    return m.group(1).strip() if m else ""

                erk = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw_res)
                ant = ext("ANTWORT_START", "ANTWORT_ENDE", raw_res)
                fri = ext("FRISTEN_START", "FRISTEN_ENDE", raw_res)
                ste = ext("STEUER_START", "STEUER_ENDE", raw_res)

                st.subheader("💡 Ergebnis")
                st.info(erk if erk else "Dokument erkannt.")

                if ist_pro:
                    st.divider()
                    
                    # ROBUSTE EXCEL-DATEN (Fix für Spalten-Fehler)
                    df_s = None
                    if ste:
                        raw_lines = [l.strip() for l in ste.split("\n") if "|" in l]
                        rows = []
                        for line in raw_lines:
                            parts = [p.strip() for p in line.split("|")]
                            while len(parts) < 3: parts.append("-")
                            rows.append(parts[:3])
                        if rows: df_s = pd.DataFrame(rows, columns=["Betrag", "Kategorie", "Grund"])

                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("💰 Steuer-Check")
                        if df_s is not None: st.dataframe(df_s, use_container_width=True)
                        else: st.write("Keine Beträge erkannt.")
                        
                        st.subheader("🗓️ Fristen")
                        if fri: st.info(fri)
                        else: st.write("Keine Fristen gefunden.")

                    with col2:
                        st.subheader("📝 Export")
                        final_a = st.text_area("Entwurf:", value=ant, height=150)
                        
                        # PDF DOWNLOAD
                        pdf_data = create_full_pdf(erk, fri, final_a, ste)
                        st.download_button("📥 PDF Download", data=pdf_data, file_name="Analyse.pdf", mime="application/pdf")
                        
                        # EXCEL DOWNLOAD
                        if df_s is not None:
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                                df_s.to_excel(wr, index=False, sheet_name='Steuer')
                                workbook, worksheet = wr.book, wr.sheets['Steuer']
                                fmt = workbook.add_format({'bold': True, 'bg_color': '#1E3A8A', 'font_color': 'white'})
                                for i, col in enumerate(df_s.columns):
                                    worksheet.write(0, i, col, fmt)
                                    worksheet.set_column(i, i, 25)
                            st.download_button("📊 Excel Export", data=buf.getvalue(), file_name="Steuer.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("🔒 PRO-Status erforderlich.")
    except Exception as e:
        st.error(f"Fehler: {e}")

st.caption("v5.2 - UTF-8 Stable Build")
