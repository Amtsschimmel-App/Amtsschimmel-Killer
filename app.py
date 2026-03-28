import streamlit as st
import openai
from PIL import Image
import pytesseract
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re

# 1. SEITEN-KONFIGURATION & DESIGN
st.set_page_config(page_title="Amtsschimmel Killer", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #ffffff 0%, #f1f4f9 100%); }
    h1 { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1e3a8a; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. SICHERHEIT & API
# Falls du lokal arbeitest, kannst du hier deinen Key auch direkt einsetzen: 
# openai.api_key = "DEIN_KEY"
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.warning("⚠️ API-Key nicht in Secrets gefunden. Bitte prüfen.")

# FUNKTION: PDF ERSTELLEN
def create_full_pdf(erklaerung, fristen_text, antwort_text, steuer_text, original_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer: Analyse", ln=True, align='C')
    pdf.ln(10)
    
    sections = [
        ("1. Zusammenfassung:", erklaerung),
        ("2. Wichtige Fristen:", fristen_text),
        ("3. Steuerliche Relevanz:", steuer_text),
        ("4. Antwort-Entwurf:", antwort_text)
    ]
    
    for title, content in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Helvetica", size=11)
        text = str(content).replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
        pdf.multi_cell(0, 8, txt=text.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)

    return bytes(pdf.output())

# 3. UI
st.title("Amtsschimmel-Killer")
st.write("_Behörden-Check & Steuer-Optimierung_")

st.divider()
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    st.markdown("### 🛠️ Status")
    if ist_pro:
        st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 **Pro freischalten (2€)**](https://buy.stripe.com)")

# 4. ANALYSE
upload = st.file_uploader("Dokument hochladen (PDF, JPG, PNG)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_doc_text = ""
        if upload.type == "application/pdf":
            with st.spinner('📑 Scanne PDF...'):
                pdf_pages = convert_from_bytes(upload.read())
                for i, page in enumerate(pdf_pages):
                    full_doc_text += f"\n--- SEITE {i+1} ---\n" + pytesseract.image_to_string(page, lang='deu')
        else:
            full_doc_text = pytesseract.image_to_string(Image.open(upload), lang='deu')

        if full_doc_text and st.button("🚀 Analyse starten"):
            with st.spinner('🧠 KI arbeitet...'):
                user_msg = f"Analysiere:\n{full_doc_text}\n\nFormat:\nERKLÄRUNG_START\n[Text]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Text]\nANTWORT_ENDE\n\nFRISTEN_START\n[Aufgabe] | [Datum]\nFRISTEN_ENDE\n\nSTEUER_START\n[Betrag] | [Kategorie] | [Grund]\nSTEUER_ENDE"
                
                # Update auf neue OpenAI Syntax (v1.0.0+)
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Du bist ein Experte für Behördendeutsch."},
                              {"role": "user", "content": user_msg}]
                )
                
                res_content = response.choices[0].message.content

                def extract(start, end, source):
                    pattern = f"{start}(.*?){end}"
                    match = re.search(pattern, source, re.DOTALL)
                    return match.group(1).strip() if match else ""

                erk = extract("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", res_content)
                ant = extract("ANTWORT_START", "ANTWORT_ENDE", res_content)
                fri = extract("FRISTEN_START", "FRISTEN_ENDE", res_content)
                ste = extract("STEUER_START", "STEUER_ENDE", res_content)

                st.subheader("💡 Ergebnis")
                st.info(erk if erk else "Text erkannt, aber keine Zusammenfassung möglich.")

                if ist_pro:
                    st.divider()
                    df_steuer = None
                    df_fristen = None

                    # Spalten für Layout
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.subheader("💰 Steuer-Check")
                        if ste:
                            lines = [l.split("|") for l in ste.split("\n") if "|" in l]
                            if lines:
                                df_steuer = pd.DataFrame(lines, columns=["Betrag", "Kategorie", "Begründung"])
                                st.dataframe(df_steuer)
                        else: st.write("Keine Beträge gefunden.")

                        st.subheader("🗓️ Fristen")
                        if fri:
                            f_lines = [l.split("|") for l in fri.split("\n") if "|" in l]
                            if f_lines:
                                df_fristen = pd.DataFrame(f_lines, columns=["Aufgabe", "Datum"])
                                st.table(df_fristen)

                    with c2:
                        st.subheader("📝 Export")
                        final_ant = st.text_area("Antwort-Vorschlag:", value=ant, height=150)
                        
                        # PDF
                        pdf_data = create_full_pdf(erk, fri, final_ant, ste, full_doc_text)
                        st.download_button("📥 PDF Download", data=pdf_data, file_name="Analyse.pdf")
                        
                        # EXCEL (Der neue Teil)
                        if df_steuer is not None:
                            try:
                                buf = io.BytesIO()
                                with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                                    df_steuer.to_excel(writer, index=False, sheet_name='Steuer')
                                    if df_fristen is not None:
                                        df_fristen.to_excel(writer, index=False, sheet_name='Fristen')
                                
                                st.download_button(
                                    label="📊 Excel Export",
                                    data=buf.getvalue(),
                                    file_name="Amtsschimmel_Daten.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            except Exception as e:
                                st.error(f"Excel-Fehler: {e}. Hast du 'xlsxwriter' installiert?")

                else:
                    st.warning("🔒 PRO-Status erforderlich für alle Details.")

    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {e}")

st.divider()
st.caption("Keine Rechtsberatung.")
