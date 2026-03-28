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
st.set_page_config(page_title="Amtsschimmel Killer", page_icon="icon_final_blau.png", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #ffffff 0%, #f1f4f9 100%); }
    h1 { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1e3a8a; color: white; font-weight: bold; }
    .stCard { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. SICHERHEIT
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("⚠️ API-Key fehlt!")

# FUNKTION: PDF ERSTELLEN
def create_full_pdf(erklaerung, fristen_text, antwort_text, steuer_text, original_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer: Vollstaendige Analyse", ln=True, align='C')
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
        text = content.replace('€', 'Euro').replace('„', '"').replace('“', '"').replace('–', '-')
        pdf.multi_cell(0, 8, txt=text.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "5. Analysierter Originaltext:", ln=True)
    pdf.set_font("Helvetica", size=8)
    pdf.multi_cell(0, 5, txt=original_text.replace('€', 'Euro').encode('latin-1', 'replace').decode('latin-1'))
    return bytes(pdf.output())

# 3. UI
col1, col2 = st.columns([1, 4])
with col1:
    try: st.image("icon_final_blau.png", width=120)
    except: st.write("📄")
with col2:
    st.title("Amtsschimmel-Killer")
    st.write("_Behörden-Check & Steuer-Optimierung für PRO-Nutzer._")

st.divider()
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    st.markdown("### 🛠️ Status")
    if ist_pro:
        st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 **Pro freischalten (2€)**](https://buy.stripe.com)")
    st.divider()
    st.caption("v2.6 - Excel Export Ready")

# 4. ANALYSE
upload = st.file_uploader("Dokument oder Steuer-Beleg hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    try:
        full_doc_text = ""
        if upload.type == "application/pdf":
            with st.spinner('📑 Scanne Seiten...'):
                pdf_pages = convert_from_bytes(upload.read())
                for i, page in enumerate(pdf_pages):
                    full_doc_text += f"\n--- SEITE {i+1} ---\n" + pytesseract.image_to_string(page, lang='deu')
        else:
            full_doc_text = pytesseract.image_to_string(Image.open(upload), lang='deu')

        if full_doc_text and st.button("🚀 Vollanalyse & Steuer-Check starten"):
            with st.spinner('🧠 KI analysiert Steuer-Relevanz...'):
                user_msg = f"Analysiere diesen Text:\n{full_doc_text}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Aufgabe] | [Datum]\nFRISTEN_ENDE\n\nSTEUER_START\n[Betrag] | [Kategorie (z.B. Werbungskosten)] | [Begründung]\nSTEUER_ENDE"
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Du bist der Amtsschimmel-Killer. Prüfe auch die steuerliche Absetzbarkeit."},
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

                st.subheader("💡 Die Analyse")
                st.info(erk if erk else "Dokument erfolgreich verarbeitet.")

                if ist_pro:
                    st.divider()
                    
                    # STEUER-CHECK
                    st.subheader("💰 Steuer-Check (PRO)")
                    df_steuer = None
                    if ste:
                        lines = [l.split("|") for l in ste.split("\n") if "|" in l]
                        if lines:
                            df_steuer = pd.DataFrame(lines, columns=["Betrag", "Kategorie", "Begründung"])
                            st.dataframe(df_steuer, use_container_width=True)
                            st.success("✅ Dieser Beleg könnte steuerlich absetzbar sein!")
                        else: st.write("Keine direkten Steuer-Informationen gefunden.")
                    else: st.write("Keine steuerlich relevanten Beträge erkannt.")
                    
                    st.divider()
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("🗓️ Fristen")
                        df_fristen = None
                        if fri:
                            f_lines = [l.split("|") for l in fri.split("\n") if "|" in l]
                            if f_lines: 
                                df_fristen = pd.DataFrame(f_lines, columns=["Aufgabe", "Datum"])
                                st.table(df_fristen)
                            else: st.write(fri)
                        else: st.write("Keine Fristen gefunden.")
                    
                    with c2:
                        st.subheader("📝 Export & Antwort")
                        final_ant = st.text_area("Entwurf:", value=ant, height=200)
                        
                        # PDF DOWNLOAD
                        pdf_data = create_full_pdf(erk, fri, final_ant, ste, full_doc_text)
                        st.download_button(label="📥 Analyse als PDF speichern", data=pdf_data, file_name="Amtsschimmel_Analyse.pdf", mime="application/pdf")
                        
                        # EXCEL DOWNLOAD
                        if df_steuer is not None:
                            excel_buffer = io.BytesIO()
                            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                                df_steuer.to_excel(writer, index=False, sheet_name='Steuer_Check')
                                if df_fristen is not None:
                                    df_fristen.to_excel(writer, index=False, sheet_name='Fristen')
                            
                            st.download_button(
                                label="📊 Steuer-Export (Excel)",
                                data=excel_buffer.getvalue(),
                                file_name="Amtsschimmel_Steuer_Export.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                else:
                    st.warning("🔒 PRO-Status erforderlich für Steuer-Check, Fristen & Antwortschreiben.")
    except Exception as e:
        st.error(f"Fehler: {e}")

st.divider()
st.caption("HINWEIS: Keine Steuer- oder Rechtsberatung. Nutzung auf eigene Gefahr.")
