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

# HILFSFUNKTION: Emojis entfernen (verhindert Latin-1 Fehler)
def remove_emojis(text):
    if not text:
        return ""
    # Entfernt alle Zeichen, die nicht im Latin-1 Bereich liegen (inkl. Emojis)
    return text.encode('latin-1', 'ignore').decode('latin-1')

# FUNKTION: PDF ERSTELLEN (v9.3 - Emoji-Safe)
def create_full_pdf(erk, fri, ant, ste, meta):
    pdf = FPDF()
    pdf.add_page()
    
    # --- HEADER ---
    logo_path = "icon_final_blau.png"
    header_y = 20
    if os.path.exists(logo_path):
        try: 
            pdf.image(logo_path, x=10, y=8, w=20)
            header_y = 35 
        except: pass

    # Zeitstempel
    pdf.set_font("Arial", size=8)
    pdf.set_xy(150, 10)
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(50, 10, f"Erstellt am: {zeit}", ln=1, align='R')

    # Behörden-Infos (Gereinigt von Emojis)
    pdf.set_xy(10, header_y)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(50, 50, 50)
    behoerde = remove_emojis(meta.get('behoerde', '-'))
    az = remove_emojis(meta.get('az', '-'))
    pdf.cell(0, 6, f"Behoerde: {behoerde}", ln=1)
    pdf.cell(0, 6, f"Referenz/AZ: {az}", ln=1)
    
    # Trennlinie
    pdf.set_draw_color(30, 58, 138)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(10)

    # --- TITEL ---
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=1, align='C')
    pdf.ln(5)
    pdf.set_text_color(0, 0, 0)

    # --- SEKTIONEN (Icons nur im Label, nicht im Content) ---
    sections = [
        ("Zusammenfassung", erk),
        ("Fristen und Termine", fri),
        ("Steuer-Informationen", ste),
        ("Antwort-Entwurf", ant)
    ]

    for title, content in sections:
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(240, 240, 245)
        pdf.cell(0, 8, title, ln=1, fill=True)
        
        pdf.set_font("Arial", size=10)
        # Inhalt radikal von Emojis säubern
        clean_content = remove_emojis(content)
        pdf.ln(2)
        pdf.multi_cell(0, 6, txt=clean_content)
        pdf.ln(6)

    return pdf.output(dest='S').encode('latin-1')

# 4. UI & SIDEBAR
st.title("Amtsschimmel-Killer 📄🚀")
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    st.header("Menü")
    if ist_pro: st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 Pro freischalten](https://buy.stripe.com)")
    st.divider()
    st.caption("v9.3 - Emoji-Crash-Fix")

# 5. HAUPT-LOGIK
upload = st.file_uploader("Brief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_img, col_ana = st.columns()
    
    with col_img:
        st.subheader("📸 Dokument")
        if upload.type == "application/pdf":
            preview = convert_from_bytes(upload.getvalue(), first_page=1, last_page=1, dpi=100)
            st.image(preview, use_container_width=True)
        else:
            st.image(upload, use_container_width=True)

    with col_ana:
        st.subheader("🧠 Analyse")
        if st.button("🚀 Jetzt analysieren", use_container_width=True):
            with st.status("Verarbeite...", expanded=True) as status:
                try:
                    status.write("📑 Lese Text...")
                    full_text = ""
                    if upload.type == "application/pdf":
                        pages = convert_from_bytes(upload.getvalue(), dpi=150)
                        for page in pages:
                            full_text += pytesseract.image_to_string(page, lang='deu') + "\n"
                    else:
                        full_text = pytesseract.image_to_string(Image.open(upload), lang='deu')
                    
                    status.write("🤖 KI-Experte wird befragt...")
                    prompt = f"Analysiere diesen Text:\n{full_text}\n\nBEHOERDE: [Name]\nAKTENZEICHEN: [Nummer]\nBETREFF: [Thema]\n\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Entwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Daten]\nFRISTEN_ENDE\n\nSTEUER_START\n[Betrag] | [Kategorie] | [Grund]\nSTEUER_ENDE"
                    
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "Du bist Behörden-Experte. Antworte ohne Emojis."}, {"role": "user", "content": prompt}]
                    )
                    raw = res.choices[0].message.content

                    def ext(s, e, src):
                        m = re.search(rf"{s}(.*?){e}", src, re.DOTALL | re.IGNORECASE)
                        return m.group(1).strip() if m else ""

                    meta = {"behoerde": ext("BEHOERDE:", "\n", raw), "az": ext("AKTENZEICHEN:", "\n", raw)}
                    erk = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw)
                    ant = ext("ANTWORT_START", "ANTWORT_ENDE", raw)
                    fri = ext("FRISTEN_START", "FRISTEN_ENDE", raw)
                    ste = ext("STEUER_START", "STEUER_ENDE", raw)
                    
                    status.update(label="✅ Fertig!", state="complete", expanded=False)

                    st.info(f"**{meta['behoerde']}** (AZ: {meta['az']})")
                    with st.expander("📝 Erklärung", expanded=True): st.write(erk)

                    if ist_pro:
                        st.divider()
                        st.warning(f"🗓️ **Fristen:** {fri}")
                        final_a = st.text_area("✍️ Antwort bearbeiten:", value=ant, height=200)
                        
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
                                        ws = wr.sheets['Steuer']
                                        for i, col in enumerate(df.columns):
                                            ws.set_column(i, i, max(df[col].astype(str).str.len().max(), len(col)) + 5)
                                st.download_button("📊 Excel speichern", data=buf.getvalue(), file_name="Steuer.xlsx", use_container_width=True)
                except Exception as e:
                    st.error(f"Fehler: {e}")
