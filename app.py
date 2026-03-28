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

# FUNKTION: PDF ERSTELLEN (Die sicherste Methode für Streamlit Cloud)
def create_full_pdf(erk, fri, ant, ste):
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
        
        # DER FIX FÜR ENCODING: Wir lassen Python das Encoding für das PDF-Objekt regeln
        text_clean = str(content).replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
        
        # Wir schreiben den Text direkt. fpdf2 regelt das Encoding intern, 
        # solange wir keine manuellen Konvertierungen erzwingen.
        pdf.multi_cell(0, 8, txt=text_clean)
        pdf.ln(5)
    
    # WICHTIG: .output() liefert in fpdf2 ein bytearray. Wir machen daraus reine bytes.
    return bytes(pdf.output())

# 3. UI
st.title("Amtsschimmel-Killer 📄🚀")
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    if ist_pro: st.success("✨ PRO-Modus aktiv")
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
                prompt = f"Analysiere:\n{full_text}\n\nFormat:\nERKLÄRUNG_START...ERKLÄRUNG_ENDE\nANTWORT_START...ANTWORT_ENDE\nFRISTEN_START...FRISTEN_ENDE\nSTEUER_START\n[Betrag] | [Kategorie] | [Grund]\nSTEUER_ENDE"
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Du bist Behörden-Experte. Nutze IMMER das Trennsymbol | für Listen."},
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
                st.info(erk if erk else "Dokument erfolgreich verarbeitet.")

                if ist_pro:
                    st.divider()
                    
                    # DATEN-AUFBEREITUNG (Sicherer Check für Fristen & Steuer)
                    df_steuer = None
                    if ste:
                        raw_lines = [l.strip() for l in ste.split("\n") if "|" in l]
                        if raw_lines:
                            rows = [line.split("|") for line in raw_lines]
                            # Spalten-Anzahl fixen
                            rows = [r + ["-"] * (3 - len(r)) for r in rows]
                            df_steuer = pd.DataFrame([r[:3] for r in rows], columns=["Betrag", "Kategorie", "Grund"])

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("💰 Steuer-Check")
                        if df_steuer is not None: st.dataframe(df_steuer, use_container_width=True)
                        else: st.write("Keine Beträge erkannt.")

                        st.subheader("🗓️ Wichtige Fristen")
                        if fri: st.info(fri)
                        else: st.write("Keine Fristen gefunden.")

                    with col2:
                        st.subheader("📝 Export & Antwort")
                        final_a = st.text_area("Entwurf anpassen:", value=ant, height=150)
                        
                        # PDF DOWNLOAD
                        pdf_data = create_full_pdf(erk, fri, final_a, ste)
                        st.download_button("📥 PDF Download", data=pdf_data, file_name="Analyse.pdf", mime="application/pdf")
                        
                        # EXCEL DOWNLOAD
                        if df_steuer is not None:
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                                df_steuer.to_excel(wr, index=False, sheet_name='Steuer')
                                # Auto-Width & Style
                                workbook, worksheet = wr.book, wr.sheets['Steuer']
                                fmt = workbook.add_format({'bold': True, 'bg_color': '#1E3A8A', 'font_color': 'white'})
                                for i, col in enumerate(df_steuer.columns):
                                    worksheet.write(0, i, col, fmt)
                                    worksheet.set_column(i, i, 25)
                            st.download_button("📊 Excel Export", data=buf.getvalue(), file_name="Steuer.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("🔒 PRO-Status erforderlich für Fristen, Steuer-Check und Downloads.")
    except Exception as e:
        st.error(f"Systemfehler: {e}")

st.caption("v5.0 - Stable Final Build")
