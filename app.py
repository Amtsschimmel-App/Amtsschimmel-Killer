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
    st.error("⚠️ OpenAI API-Key fehlt!")

# HILFSFUNKTION: Emojis entfernen (für PDF-Stabilität)
def remove_emojis(text):
    if not text: return ""
    return text.encode('latin-1', 'ignore').decode('latin-1')

# FUNKTION: PDF ERSTELLEN
def create_full_pdf(erk, fri, ant, ste, meta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    logo_path = "icon_final_blau.png"
    header_y = 20
    if os.path.exists(logo_path):
        try: 
            pdf.image(logo_path, x=10, y=8, w=20)
            header_y = 35 
        except: pass

    pdf.set_font("Arial", size=8)
    pdf.set_xy(150, 10)
    zeit = datetime.now().strftime("%d.%m.%Y %H:%M")
    pdf.cell(50, 10, f"Erstellt am: {zeit}", ln=1, align='R')

    pdf.set_xy(10, header_y)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 6, f"Behoerde: {remove_emojis(meta.get('behoerde', '-'))}", ln=1)
    pdf.cell(0, 6, f"Referenz/AZ: {remove_emojis(meta.get('az', '-'))}", ln=1)
    
    pdf.set_draw_color(30, 58, 138)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=1, align='C')
    pdf.ln(5)
    pdf.set_text_color(0, 0, 0)

    sections = [("Zusammenfassung", erk), ("Fristen", fri), ("Steuer", ste), ("Antwort", ant)]
    for title, content in sections:
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(240, 240, 245)
        pdf.cell(0, 8, title, ln=1, fill=True)
        pdf.set_font("Arial", size=10)
        pdf.ln(2)
        pdf.multi_cell(0, 6, txt=remove_emojis(content))
        pdf.ln(6)

    return pdf.output(dest='S').encode('latin-1')

# 4. UI & SIDEBAR
st.title("Amtsschimmel-Killer 📄🚀")
ist_pro = st.query_params.get("payment") == "success"

with st.sidebar:
    st.image("icon_final_blau.png", width=100) if os.path.exists("icon_final_blau.png") else None
    st.header("Menü")
    if ist_pro: st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown("[👉 Pro freischalten](https://buy.stripe.com)")
    st.divider()
    st.caption("v9.5 - Dashboard-Design Update")

# 5. HAUPT-LOGIK
upload = st.file_uploader("Behördenbrief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_img, col_ana = st.columns(2)
    
    with col_img:
        st.subheader("📸 Dokument")
        if upload.type == "application/pdf":
            preview = convert_from_bytes(upload.getvalue(), first_page=1, last_page=1, dpi=100)
            st.image(preview, use_container_width=True)
        else:
            st.image(upload, use_container_width=True)

    with col_ana:
        st.subheader("🧠 Analyse-Dashboard")
        if st.button("🚀 Vollanalyse starten", use_container_width=True):
            with st.status("Verarbeite Dokument...", expanded=True) as status:
                try:
                    status.write("📑 Text-Extraktion...")
                    full_text = ""
                    if upload.type == "application/pdf":
                        pages = convert_from_bytes(upload.getvalue(), dpi=150)
                        for page in pages:
                            full_text += pytesseract.image_to_string(page, lang='deu') + "\n"
                    else:
                        full_text = pytesseract.image_to_string(Image.open(upload), lang='deu')
                    
                    status.write("🤖 KI-Analyse...")
                    prompt = f"Analysiere:\n{full_text}\n\nBEHOERDE: [Name]\nAKTENZEICHEN: [Nummer]\nBETREFF: [Thema]\n\nERKLÄRUNG_START\n[Zusammenfassung]\nERKLÄRUNG_ENDE\n\nANTWORT_START\n[Briefentwurf]\nANTWORT_ENDE\n\nFRISTEN_START\n[Datum/Frist]\nFRISTEN_ENDE\n\nSTEUER_START\n[Betrag] | [Kategorie] | [Grund]\nSTEUER_ENDE"
                    
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "Du bist Behörden-Experte. Antworte ohne Emojis."}, 
                                  {"role": "user", "content": prompt}]
                    )
                    raw = res.choices[0].message.content

                    def ext(s, e, src):
                        m = re.search(rf"{s}(.*?){e}", src, re.DOTALL | re.IGNORECASE)
                        return m.group(1).strip() if m else ""

                    meta = {"behoerde": ext("BEHOERDE:", "\n", raw), "az": ext("AKTENZEICHEN:", "\n", raw), "betreff": ext("BETREFF:", "\n", raw)}
                    erk, ant, fri, ste = ext("ERKLÄRUNG_START", "ERKLÄRUNG_ENDE", raw), ext("ANTWORT_START", "ANTWORT_ENDE", raw), ext("FRISTEN_START", "FRISTEN_ENDE", raw), ext("STEUER_START", "STEUER_ENDE", raw)
                    
                    status.update(label="✅ Fertig!", state="complete", expanded=False)

                    # --- DASHBOARD LAYOUT ---
                    st.header(meta['behoerde'] if meta['behoerde'] else "Behörde erkannt")
                    
                    m1, m2 = st.columns(2)
                    m1.metric("Aktenzeichen", meta['az'][:20] + "..." if len(meta['az']) > 20 else meta['az'])
                    # Frist-Extraktion für Metric (nur Datum suchen)
                    frist_clean = re.search(r"(\d{2}\.\d{2}\.\d{4})", fri)
                    m2.metric("Nächste Frist", frist_clean.group(1) if frist_clean else "Nicht gefunden")

                    st.markdown(f"**Betreff:** {meta['betreff']}")
                    
                    with st.container(border=True):
                        st.subheader("💡 Was ist zu tun?")
                        st.write(erk)

                    if ist_pro:
                        st.divider()
                        st.subheader("✍️ Briefentwurf")
                        final_a = st.text_area("Vorschlag (kann editiert werden):", value=ant, height=250)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            pdf_data = create_full_pdf(erk, fri, final_a, ste, meta)
                            st.download_button("📥 PDF Gutachten", data=pdf_data, file_name="Analyse.pdf", mime="application/pdf", use_container_width=True)
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
                                st.download_button("📊 Steuer-Export (Excel)", data=buf.getvalue(), file_name="Steuer.xlsx", use_container_width=True)
                    else:
                        st.warning("🔒 PRO freischalten für Antwort-Entwurf & Export.")
                except Exception as e:
                    st.error(f"Fehler: {e}")
