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
    st.error("⚠️ OpenAI API-Key fehlt in den Secrets!")

# FUNKTION: PDF-TEXT REINIGUNG (Löst den Encoding-Fehler endgültig)
def clean_for_pdf(text):
    if not text:
        return "Nicht verfügbar"
    # Bekannte Problemzeichen ersetzen
    repls = {
        '€': 'Euro', '„': '"', '“': '"', '”': '"', '‘': "'", '’': "'",
        '–': '-', '—': '-', '…': '...', '•': '*', '·': '*'
    }
    t = str(text)
    for old, new in repls.items():
        t = t.replace(old, new)
    # ALLES entfernen, was nicht in Latin-1 passt (Crash-Schutz)
    return t.encode('latin-1', 'ignore').decode('latin-1')

# FUNKTION: PDF ERSTELLEN
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
        ("Antwort-Vorschlag", ant)
    ]
    
    for title, content in sections:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"{title}:", ln=1)
        pdf.set_font("helvetica", size=11)
        # Hier wird der Text vor dem Schreiben "gewaschen"
        pdf.multi_cell(0, 8, txt=clean_for_pdf(content))
        pdf.ln(5)
    
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

        if full_text and st.button("🚀 Vollanalyse starten"):
            with st.spinner('🧠 KI analysiert Dokument...'):
                # Verschärfter Prompt für längere Entwürfe
                prompt = f"Analysiere diesen Text:\n{full_text}\n\nFormat:\nERKLÄRUNG_START\n[Ausführliche Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Ein vollständiger, förmlicher Briefentwurf als Antwort]\nANTWORT_ENDE\n\nFRISTEN_START\n[Alle Termine]\nFRISTEN_ENDE\n\nSTEUER_START\n[Betrag] | [Kategorie] | [Grund]\nSTEUER_ENDE"
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "Du bist ein erfahrener Experte für Behördenkorrespondenz. Schreibe hilfreiche, ausführliche Briefentwürfe."},
                              {"role": "user", "content": prompt}]
                )
                raw_res = response.choices[0].message.content

                # Robuste Extraktion
                def ext(s, e, src):
                    pattern = f"{s}(.*?){e}"
                    m = re.search(pattern, src, re.DOTALL | re.IGNORECASE)
                    return m.group(1).strip() if m else ""

                erk = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw_res)
                ant = ext("ANTWORT_START", "ANTWORT_ENDE", raw_res)
                fri = ext("FRISTEN_START", "FRISTEN_ENDE", raw_res)
                ste = ext("STEUER_START", "STEUER_ENDE", raw_res)

                st.subheader("💡 Analyse")
                st.info(erk if erk else "Text erkannt, aber keine Analyse möglich.")

                if ist_pro:
                    st.divider()
                    df_s = None
                    if ste:
                        raw_lines = [l.strip() for l in ste.split("\n") if "|" in l]
                        rows = [line.split("|") for line in raw_lines]
                        if rows:
                            rows = [r + ["-"] * (3 - len(r)) for r in rows]
                            df_s = pd.DataFrame([r[:3] for r in rows], columns=["Betrag", "Kategorie", "Grund"])

                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("💰 **Steuer-Check**")
                        if df_s is not None: st.dataframe(df_s, use_container_width=True)
                        else: st.write("Keine Beträge erkannt.")
                        
                        st.write("🗓️ **Wichtige Fristen**")
                        st.info(fri if fri else "Keine Fristen gefunden.")

                    with c2:
                        st.write("📝 **Antwort-Entwurf**")
                        # Größeres Textfeld für den nun längeren Entwurf
                        final_a = st.text_area("Vorschlag bearbeiten:", value=ant, height=350)
                        
                        # PDF DOWNLOAD
                        pdf_bytes = create_full_pdf(erk, fri, final_a, ste)
                        st.download_button("📥 PDF Analyse speichern", data=pdf_bytes, file_name="Amtsschimmel_Analyse.pdf", mime="application/pdf")
                        
                        # EXCEL DOWNLOAD
                        if df_s is not None:
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                                df_s.to_excel(wr, index=False, sheet_name='Steuer')
                            st.download_button("📊 Steuer-Daten (Excel)", data=buf.getvalue(), file_name="Steuer.xlsx")
                else:
                    st.warning("🔒 PRO-Status erforderlich für Export & Details.")
    except Exception as e:
        st.error(f"Fehler: {e}")

st.caption("v8.0 - Stable Unicode & AI Prompt Update")
