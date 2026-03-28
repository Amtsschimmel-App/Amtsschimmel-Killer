import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re
import os
from datetime import datetime
import shutil

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel Killer", page_icon="📄", layout="wide")

# 2. TESSERACT PFAD-FIX
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# 3. API INITIALISIERUNG
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("⚠️ OpenAI API-Key fehlt in den Secrets!")

# FUNKTION: PDF ERSTELLEN (Stabilisierte Version)
def create_full_pdf(erk, fri, ant, ste):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    logo_path = "icon_final_blau.png"
    if os.path.exists(logo_path):
        try: pdf.image(logo_path, x=10, y=8, w=25)
        except: pass
    
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(0, 10, f"Erstellt am: {zeit}", ln=1, align='R')
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 16)
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
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{title}:", ln=1)
        pdf.set_font("Arial", size=11)
        text_clean = str(content if content else "-").encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, txt=text_clean)
        pdf.ln(4)
    
    return pdf.output(dest='S').encode('latin-1')

# 4. UI DESIGN & SIDEBAR
st.title("Amtsschimmel-Killer 📄🚀")
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    st.header("Einstellungen")
    if ist_pro: 
        st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 Pro freischalten](https://buy.stripe.com)")
    
    st.divider()
    st.subheader("Anleitung")
    st.write("1. Behördenbrief hochladen")
    st.write("2. 'Analyse starten' klicken")
    st.write("3. Briefentwurf & Fristen prüfen")
    st.caption("v9.0 - UX & Visual Update")

# 5. HAUPT-LOGIK
upload = st.file_uploader("Dokument hochladen (Bild oder PDF)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    # Vorbereitung der Ansicht (Zwei Spalten)
    col_img, col_ana = st.columns([1, 1])
    
    with col_img:
        st.subheader("📸 Dein Dokument")
        if upload.type == "application/pdf":
            # Erste Seite des PDFs als Vorschau zeigen
            pdf_preview_bytes = upload.getvalue()
            preview_images = convert_from_bytes(pdf_preview_bytes, first_page=1, last_page=1, dpi=100)
            st.image(preview_images[0], use_container_width=True, caption="Vorschau Seite 1")
        else:
            st.image(upload, use_container_width=True, caption="Hochgeladenes Bild")

    with col_ana:
        st.subheader("🧠 KI-Analyse")
        if st.button("🚀 Vollanalyse starten", use_container_width=True):
            # Fortschritts-Status (Neu!)
            with st.status("Verarbeite Dokument...", expanded=True) as status:
                try:
                    # Schritt 1: OCR
                    status.write("📑 Extrahiere Text aus Dokument...")
                    full_text = ""
                    if upload.type == "application/pdf":
                        pages = convert_from_bytes(upload.getvalue(), dpi=150)
                        for page in pages:
                            full_text += pytesseract.image_to_string(page, lang='deu') + "\n"
                    else:
                        full_text = pytesseract.image_to_string(Image.open(upload), lang='deu')
                    
                    if not full_text.strip():
                        st.error("Kein Text erkannt. Bitte Bildqualität prüfen!")
                        st.stop()

                    # Schritt 2: KI Analyse
                    status.write("🤖 KI analysiert Behördendeutsch...")
                    prompt = f"Analysiere diesen Text:\n{full_text}\n\nFormat:\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Termine]\nFRISTEN_ENDE\n\nSTEUER_START\n[Betrag] | [Kategorie] | [Grund]\nSTEUER_ENDE"
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "Du bist Behörden-Experte."},
                                  {"role": "user", "content": prompt}]
                    )
                    raw_res = response.choices[0].message.content

                    def ext(s, e, src):
                        pattern = rf"\*?{s}\*?(.*?)\*?{e}\*?"
                        m = re.search(pattern, src, re.DOTALL | re.IGNORECASE)
                        return m.group(1).strip() if m else ""

                    erk = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw_res)
                    ant = ext("ANTWORT_START", "ANTWORT_ENDE", raw_res)
                    fri = ext("FRISTEN_START", "FRISTEN_ENDE", raw_res)
                    ste = ext("STEUER_START", "STEUER_ENDE", raw_res)
                    
                    status.update(label="✅ Analyse abgeschlossen!", state="complete", expanded=False)

                    # AUSGABE DER ERGEBNISSE
                    st.success("Analyse bereit")
                    with st.expander("📝 Zusammenfassung & Erklärung", expanded=True):
                        st.write(erk if erk else "Inhalt konnte nicht gedeutet werden.")

                    if ist_pro:
                        st.divider()
                        st.warning(f"🗓️ **Fristen:** {fri if fri else 'Keine Fristen gefunden.'}")
                        
                        st.write("📝 **Vorgeschlagene Antwort:**")
                        final_a = st.text_area("Hier bearbeiten:", value=ant, height=250)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            pdf_data = create_full_pdf(erk, fri, final_a, ste)
                            st.download_button("📥 PDF Analyse speichern", data=pdf_data, file_name="Amtsschimmel_Killer.pdf", mime="application/pdf", use_container_width=True)
                        with c2:
                            if ste:
                                buf = io.BytesIO()
                                with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                                    # Einfaches DF-Handling für den Export
                                    raw_lines = [l.strip() for l in ste.split("\n") if "|" in l]
                                    rows = [line.split("|") for line in raw_lines]
                                    if rows:
                                        df_s = pd.DataFrame(rows, columns=["Betrag", "Kategorie", "Grund"])
                                        df_s.to_excel(wr, index=False, sheet_name='Steuer')
                                st.download_button("📊 Excel-Export", data=buf.getvalue(), file_name="Steuer.xlsx", use_container_width=True)
                    else:
                        st.info("🔒 Pro-Modus erforderlich für Briefentwurf und Export.")
                        
                except Exception as e:
                    st.error(f"Fehler während der Verarbeitung: {e}")
