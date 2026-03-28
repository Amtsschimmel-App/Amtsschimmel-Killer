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

# FUNKTION: PDF ERSTELLEN
def create_full_pdf(erk, fri, ant, ste, meta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    logo_path = "icon_final_blau.png"
    if os.path.exists(logo_path):
        try: pdf.image(logo_path, x=10, y=8, w=25)
        except: pass
    
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(0, 10, f"Erstellt am: {zeit}", ln=1, align='R')
    pdf.ln(5)
    
    # Header Info (Metadaten)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, f"Behörde: {meta.get('behoerde', '-')}", ln=1)
    pdf.cell(0, 8, f"Aktenzeichen: {meta.get('az', '-')}", ln=1)
    pdf.ln(5)
    
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

# 4. UI & SIDEBAR
st.title("Amtsschimmel-Killer 📄🚀")
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    st.header("Einstellungen")
    if ist_pro: st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 Pro freischalten](https://buy.stripe.com)")
    st.divider()
    st.caption("v9.1 - Meta-Extraction & Auto-Excel")

# 5. HAUPT-LOGIK
upload = st.file_uploader("Dokument hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_img, col_ana = st.columns([1, 1])
    
    with col_img:
        st.subheader("📸 Dein Dokument")
        if upload.type == "application/pdf":
            preview_images = convert_from_bytes(upload.getvalue(), first_page=1, last_page=1, dpi=100)
            st.image(preview_images, use_container_width=True)
        else:
            st.image(upload, use_container_width=True)

    with col_ana:
        st.subheader("🧠 KI-Analyse")
        if st.button("🚀 Vollanalyse starten", use_container_width=True):
            with st.status("Verarbeite Dokument...", expanded=True) as status:
                try:
                    # Schritt 1: OCR
                    status.write("📑 Extrahiere Text...")
                    full_text = ""
                    if upload.type == "application/pdf":
                        pages = convert_from_bytes(upload.getvalue(), dpi=150)
                        for page in pages:
                            full_text += pytesseract.image_to_string(page, lang='deu') + "\n"
                    else:
                        full_text = pytesseract.image_to_string(Image.open(upload), lang='deu')
                    
                    # Schritt 2: KI-Analyse (Erweitert um Metadaten)
                    status.write("🤖 Suche Aktenzeichen & Fristen...")
                    prompt = f"""Analysiere diesen Text:
                    {full_text}
                    
                    Extrahiere folgende Felder:
                    BEHOERDE: [Name der Behörde]
                    AKTENZEICHEN: [Aktenzeichen/Referenznummer]
                    BETREFF: [Thema des Schreibens]
                    
                    Format für den Rest:
                    ERKLÄRUNG_START
                    [Zusammenfassung]
                    ERKLÄRUNG_ENDE
                    
                    ANTWORT_START
                    [Briefentwurf]
                    ANTWORT_ENDE
                    
                    FRISTEN_START
                    [Alle Termine]
                    FRISTEN_ENDE
                    
                    STEUER_START
                    [Betrag] | [Kategorie] | [Grund]
                    STEUER_ENDE"""
                    
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "Du bist ein präziser Behörden-Experte."},
                                  {"role": "user", "content": prompt}]
                    )
                    raw = res.choices[0].message.content

                    # Extraktions-Helfer
                    def ext(s, e, src):
                        m = re.search(rf"{s}(.*?){e}", src, re.DOTALL | re.IGNORECASE)
                        return m.group(1).strip() if m else ""

                    # Metadaten-Extraktion
                    meta = {
                        "behoerde": ext("BEHOERDE:", "\n", raw),
                        "az": ext("AKTENZEICHEN:", "\n", raw),
                        "betreff": ext("BETREFF:", "\n", raw)
                    }
                    
                    erk = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw)
                    ant = ext("ANTWORT_START", "ANTWORT_ENDE", raw)
                    fri = ext("FRISTEN_START", "FRISTEN_ENDE", raw)
                    ste = ext("STEUER_START", "STEUER_ENDE", raw)
                    
                    status.update(label="✅ Analyse fertig!", state="complete", expanded=False)

                    # ANZEIGE
                    st.success(f"**{meta['behoerde']}**")
                    st.code(f"Betreff: {meta['betreff']}\nAZ: {meta['az']}")
                    
                    with st.expander("📝 Was bedeutet das?", expanded=True):
                        st.write(erk)

                    if ist_pro:
                        st.divider()
                        st.warning(f"🗓️ **Fristen:** {fri}")
                        final_a = st.text_area("Vorgeschlagene Antwort:", value=ant, height=250)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            pdf_data = create_full_pdf(erk, fri, final_a, ste, meta)
                            st.download_button("📥 PDF speichern", data=pdf_data, file_name="Analyse.pdf", mime="application/pdf", use_container_width=True)
                        with c2:
                            if ste:
                                buf = io.BytesIO()
                                with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                                    lines = [l.strip() for l in ste.split("\n") if "|" in l]
                                    rows = [line.split("|") for line in lines]
                                    if rows:
                                        df = pd.DataFrame(rows, columns=["Betrag", "Kategorie", "Grund"])
                                        df.to_excel(wr, index=False, sheet_name='Steuer')
                                        # AUTOMATISCHE SPALTENBREITE
                                        ws = wr.sheets['Steuer']
                                        for i, col in enumerate(df.columns):
                                            column_len = max(df[col].astype(str).str.len().max(), len(col)) + 5
                                            ws.set_column(i, i, column_len)
                                st.download_button("📊 Excel (Auto-Spalten)", data=buf.getvalue(), file_name="Steuer.xlsx", use_container_width=True)
                    else:
                        st.info("🔒 Pro freischalten für Antwort-Entwurf & Export.")

                except Exception as e:
                    st.error(f"Fehler: {e}")

