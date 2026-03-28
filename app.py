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

# FUNKTION: PDF ERSTELLEN (Adobe-kompatibel + Logo + Zeitstempel)
def create_full_pdf(erk, fri, ant, ste):
    pdf = FPDF()
    pdf.add_page()
    
    # LOGO (oben links)
    try:
        pdf.image("icon_final_blau.png", x=10, y=8, w=25)
    except:
        pass 
    
    # ZEITSTEMPEL (oben rechts)
    pdf.set_font("helvetica", size=9)
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(0, 10, f"Erstellt am: {zeit}", ln=True, align='R')
    pdf.ln(15)
    
    # TITEL
    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(30, 58, 138) # Dunkelblau
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=True, align='C')
    pdf.set_text_color(0, 0, 0) 
    pdf.ln(10)
    
    sections = [
        ("Zusammenfassung", erk),
        ("Wichtige Fristen", fri),
        ("Steuerliche Relevanz", ste),
        ("Antwort-Entwurf", ant)
    ]
    
    for title, content in sections:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"{title}:", ln=True)
        pdf.set_font("helvetica", size=11)
        # Radikale Bereinigung für Adobe Acrobat Kompatibilität
        t = str(content).replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-').replace('—', '-')
        pdf.multi_cell(0, 7, txt=t)
        pdf.ln(4)
    
    # WICHTIG: Explizite Konvertierung in Bytes für Adobe
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
                    messages=[{"role": "system", "content": "Du bist Behörden-Experte."},
                              {"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content

                def ext(s, e, src):
                    m = re.search(f"{s}(.*?){e}", src, re.DOTALL)
                    return m.group(1).strip() if m else ""

                erk, ant, fri, ste = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw), ext("ANTWORT_START", "ANTWORT_ENDE", raw), ext("FRISTEN_START", "FRISTEN_ENDE", raw), ext("STEUER_START", "STEUER_ENDE", raw)

                st.subheader("💡 Ergebnis")
                st.info(erk if erk else "Analyse erfolgreich.")

                if ist_pro:
                    st.divider()
                    # Wir bereiten die Daten VOR den Spalten vor
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
                            st.write("🗓️ **Fristen**")
                            st.text(fri)

                    with c2:
                        st.write("📝 **Export**")
                        final_a = st.text_area("Entwurf anpassen:", value=ant, height=150)
                        
                        # PDF DOWNLOAD
                        pdf_data = create_full_pdf(erk, fri, final_a, ste)
                        st.download_button("📥 Analyse als PDF", data=pdf_data, file_name="Analyse.pdf", mime="application/pdf")
                        
                        # EXCEL DOWNLOAD
                        if df_s is not None:
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                                df_s.to_excel(wr, index=False, sheet_name='Steuer')
                                workbook = wr.book
                                worksheet = wr.sheets['Steuer']
                                
                                # Blaues Design für Header
                                header_format = workbook.add_format({
                                    'bold': True, 'font_color': 'white', 'bg_color': '#1E3A8A', 'border': 1
                                })
                                for col_num, value in enumerate(df_s.columns.values):
                                    worksheet.write(0, col_num, value, header_format)
                                    # Auto-Width
                                    width = max(df_s[df_s.columns[col_num]].astype(str).map(len).max(), len(value)) + 3
                                    worksheet.set_column(col_num, col_num, width)
                                    
                            st.download_button("📊 Steuer-Liste als Excel", data=buf.getvalue(), file_name="Steuer.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("🔒 PRO-Status erforderlich.")
    except Exception as e:
        st.error(f"Fehler: {e}")

st.caption("v2.9 - Final Stable Build")
