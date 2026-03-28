import streamlit as st
from openai import OpenAI
from PIL import Image
import pytesseract
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel Killer", page_icon="📄", layout="wide")

# 2. API INITIALISIERUNG
try:
    # Nutzt die Secrets von Streamlit Cloud
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("⚠️ OpenAI API-Key fehlt in den Streamlit Cloud Secrets!")

# FUNKTION: PDF ERSTELLEN (Optimiert für fpdf2)
def create_full_pdf(erk, fri, ant, ste):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    sections = [
        ("Zusammenfassung", erk),
        ("Wichtige Fristen", fri),
        ("Steuerliche Relevanz", ste),
        ("Antwort-Entwurf", ant)
    ]
    
    for title, content in sections:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"{title}:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", size=11)
        
        # Text säubern für PDF (Euro-Zeichen ersetzen)
        safe_text = str(content).replace('€', 'Euro')
        pdf.multi_cell(0, 8, txt=safe_text)
        pdf.ln(5)
    
    return pdf.output()

# 3. UI
st.title("Amtsschimmel-Killer 📄🚀")

# Pro-Status über URL-Parameter prüfen
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    if ist_pro:
        st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 Pro freischalten](https://buy.stripe.com)")

# 4. UPLOAD & ANALYSE
upload = st.file_uploader("Dokument hochladen (PDF, JPG, PNG)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_text = ""
        if upload.type == "application/pdf":
            with st.spinner('📑 Scanne PDF...'):
                # PDF in Bilder umwandeln für OCR
                pages = convert_from_bytes(upload.read())
                for page in pages:
                    full_text += pytesseract.image_to_string(page, lang='deu') + "\n"
        else:
            full_text = pytesseract.image_to_string(Image.open(upload), lang='deu')

        if full_text and st.button("🚀 Analyse starten"):
            with st.spinner('🧠 KI analysiert...'):
                prompt = f"Analysiere diesen Text:\n{full_text}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Entwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Aufgabe] | [Datum]\nFRISTEN_ENDE\n\nSTEUER_START\n[Betrag] | [Kategorie] | [Grund]\nSTEUER_ENDE"
                
                # HIER WAR DER FEHLER: response.choices[0] hinzugefügt
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Du bist ein Experte für Behördendeutsch."},
                              {"role": "user", "content": prompt}]
                )
                raw = response.choices[0].message.content

                def ext(s, e, src):
                    m = re.search(f"{s}(.*?){e}", src, re.DOTALL)
                    return m.group(1).strip() if m else ""

                erk = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw)
                ant = ext("ANTWORT_START", "ANTWORT_ENDE", raw)
                fri = ext("FRISTEN_START", "FRISTEN_ENDE", raw)
                ste = ext("STEUER_START", "STEUER_ENDE", raw)

                st.subheader("💡 Ergebnis")
                st.info(erk if erk else "Dokument erfolgreich analysiert.")

                if ist_pro:
                    st.divider()
                    c1, c2 = st.columns(2)
                    df_s = None
                    
                    with c1:
                        if ste:
                            st.write("💰 **Steuer-Check**")
                            rows = [l.split("|") for l in ste.split("\n") if "|" in l]
                            if rows:
                                df_s = pd.DataFrame(rows, columns=["Betrag", "Kategorie", "Grund"])
                                st.dataframe(df_s, use_container_width=True)
                        if fri:
                            st.write("🗓️ **Fristen**")
                            st.text(fri)

                    with c2:
                        st.write("📝 **Export & Antwort**")
                        final_a = st.text_area("Entwurf anpassen:", value=ant, height=150)
                        
                        # PDF DOWNLOAD
                        try:
                            pdf_bytes = create_full_pdf(erk, fri, final_a, ste)
                            st.download_button("📥 PDF Download", data=pdf_bytes, file_name="Amtsschimmel_Analyse.pdf", mime="application/pdf")
                        except Exception as pdf_err:
                            st.error(f"PDF-Fehler: {pdf_err}")
                        
                        # EXCEL DOWNLOAD
                        if df_s is not None:
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                                df_s.to_excel(wr, index=False, sheet_name='Steuer')
                            st.download_button("📊 Excel Export", data=buf.getvalue(), file_name="Amtsschimmel_Steuer.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.warning("🔒 PRO-Status erforderlich für Details.")
    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")

st.divider()
st.caption("Keine Rechts- oder Steuerberatung.")
