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
import stripe

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# 2. API INITIALISIERUNG
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    stripe.api_key = st.secrets["STRIPE_API_KEY"]
except Exception:
    st.error("⚠️ API-Keys fehlen in den Secrets! Bitte unter Settings -> Secrets eintragen.")

# TESSERACT PFAD-FIX
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# --- HILFSFUNKTIONEN ---
def remove_emojis(text):
    if not text: return ""
    return text.encode('latin-1', 'ignore').decode('latin-1')

def create_full_pdf(erk, fri, ant, ste, meta, fehler):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=1, align='C')
    pdf.ln(10)
    
    sections = [
        ("Behoerde", meta.get('behoerde', '-')),
        ("Aktenzeichen", meta.get('az', '-')),
        ("Zusammenfassung", erk),
        ("Fristen & Termine", fri),
        ("Formfehler-Check", fehler),
        ("Antwortentwurf", ant)
    ]
    
    for title, content in sections:
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(240, 240, 245)
        pdf.cell(0, 8, title, ln=1, fill=True)
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        pdf.multi_cell(0, 6, txt=remove_emojis(content))
        pdf.ln(4)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 3. ZAHLUNGSPRÜFUNG (STRIPE SICHERHEIT) ---
session_id = st.query_params.get("session_id")
ist_pro = False

if session_id:
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        if checkout_session.payment_status == "paid":
            ist_pro = True
            st.toast("✨ PRO-Modus aktiv!", icon="✅")
    except:
        st.sidebar.warning("Zahlungsverifizierung fehlgeschlagen.")

# --- 4. UI & SIDEBAR ---
with st.sidebar:
    logo_file = "icon_final_blau.png"
    if os.path.exists(logo_file):
        st.image(logo_file, width=150)
    
    st.header("Dein Status")
    if ist_pro: 
        st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        # DEIN EINGEBAUTER STRIPE-LINK
        st.markdown(f'''
            <a href="https://buy.stripe.com" target="_blank">
                <button style="width:100%; border-radius:5px; background-color:#303a8a; color:white; border:none; padding:12px; cursor:pointer; font-weight:bold;">
                    👉 JETZT PRO FREISCHALTEN
                </button>
            </a>
        ''', unsafe_allow_html=True)
   
    st.divider()
    if "kosten" not in st.session_state: st.session_state.kosten = 0.0
    st.caption(f"Verbrauch: ${st.session_state.kosten:.4f}")

# --- 5. HAUPT-LOGIK ---
st.title("Amtsschimmel-Killer 📄🚀")
upload = st.file_uploader("Behördenbrief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_img, col_ana = st.columns(2)
    
    with col_img:
        st.subheader("📸 Dokument")
        if upload.type == "application/pdf":
            try:
                preview = convert_from_bytes(upload.getvalue(), first_page=1, last_page=1, dpi=100)
                st.image(preview, use_container_width=True)
            except: st.info("Analyse bereit.")
        else:
            st.image(upload, use_container_width=True)

    with col_ana:
        st.subheader("🧠 KI-Analyse")
        if st.button("🚀 Analyse starten", use_container_width=True):
            with st.status("Verarbeite...", expanded=True) as status:
                # OCR
                if upload.type == "application/pdf":
                    pages = convert_from_bytes(upload.getvalue(), dpi=150)
                    full_text = "".join([pytesseract.image_to_string(p, lang='deu') for p in pages])
                else:
                    full_text = pytesseract.image_to_string(Image.open(upload), lang='deu')

                # KI PROMPT
                prompt = f"""Analysiere den Text: {full_text}
                FORMAT:
                BEHOERDE: [Name]
                AZ: [Nummer]
                ERKLÄRUNG: [Zusammenfassung]
                FRISTEN: [Wichtige Daten]
                FORMFEHLER: [Prüfe auf fehlende Unterschrift, fehlende Rechtsbehelfsbelehrung oder Fristfehler!]
                ANTWORT: [Briefentwurf]
                STEUER: [Betrag | Grund]"""
                
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "Du bist Behörden-Experte."}, 
                              {"role": "user", "content": prompt}]
                )
                
                st.session_state.kosten += (res.usage.total_tokens / 1000) * 0.00015
                raw = res.choices[0].message.content

                def ext(tag, src):
                    m = re.search(rf"{tag}:(.*?)(?=\n[A-Z]+:|$)", src, re.DOTALL | re.IGNORECASE)
                    return m.group(1).strip() if m else "Nicht gefunden"

                meta = {"behoerde": ext("BEHOERDE", raw), "az": ext("AZ", raw)}
                erk, fri, fehler, ant, ste = ext("ERKLÄRUNG", raw), ext("FRISTEN", raw), ext("FORMFEHLER", raw), ext("ANTWORT", raw), ext("STEUER", raw)
                
                status.update(label="✅ Fertig!", state="complete")

                st.header(meta['behoerde'])
                with st.expander("💡 Was will die Behörde?", expanded=True):
                    st.write(erk)
                
                if "Keine" not in fehler and "nicht gefunden" not in fehler.lower():
                    st.error(f"🚨 **FORMFEHLER-WARNUNG:** {fehler}")
                
                st.warning(f"📅 **Fristen:** {fri}")

                if ist_pro:
                    st.subheader("✍️ Pro-Antwortbrief")
                    final_a = st.text_area("Anpassen:", value=ant, height=200)
                    pdf_data = create_full_pdf(erk, fri, final_a, ste, meta, fehler)
                    st.download_button("📥 PDF-Gutachten laden", data=pdf_data, file_name="Analyse.pdf", use_container_width=True)
                else:
                    st.info("🔓 Schalte PRO frei für den Antwortbrief & PDF-Download.")

st.divider()
st.caption("Keine Rechtsberatung. v10.7 - Fixed Indentation & Link")
