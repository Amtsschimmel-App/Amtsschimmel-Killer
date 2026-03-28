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
import numpy as np
import cv2

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# 2. API INITIALISIERUNG
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    stripe.api_key = st.secrets["STRIPE_API_KEY"]
except Exception:
    st.error("⚠️ API-Keys fehlen in den Secrets!")

# TESSERACT PFAD-FIX
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# --- HILFSFUNKTIONEN ---
def check_image_quality(image):
    img_array = np.array(image.convert('L'))
    brightness = np.mean(img_array)
    laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()
    if brightness < 40: return False, "Bild zu dunkel."
    if laplacian_var < 70: return False, "Bild unscharf."
    return True, "OK"

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
        ("Behörde", meta.get('behoerde', '-')),
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

def create_excel(data_dict):
    """Erstellt Excel mit automatischer Spaltenbreite und Textumbruch."""
    df = pd.DataFrame([data_dict])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
        workbook  = writer.book
        worksheet = writer.sheets['Analyse']
        
        # Format für Textumbruch
        wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
        
        # Spaltenbreiten automatisch setzen
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            # Begrenzung der Breite auf max 60 Zeichen, damit es nicht zu riesig wird
            width = min(column_len, 60)
            worksheet.set_column(i, i, width, wrap_format)
            
    return output.getvalue()

# --- 3. ZAHLUNGSPRÜFUNG & ADMIN-LOGIK ---
session_id = st.query_params.get("session_id")
is_admin = st.query_params.get("admin") == "ja" 
ist_pro = False

if is_admin:
    ist_pro = True 
elif session_id:
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        if checkout_session.payment_status == "paid":
            ist_pro = True
    except:
        st.sidebar.warning("Zahlung nicht verifiziert.")

# --- 4. UI & SIDEBAR ---
with st.sidebar:
    logo_file = "icon_final_blau.png"
    if os.path.exists(logo_file):
        st.image(logo_file, width=150)
    
    st.header("Dein Status")
    if is_admin:
        st.success("🛠️ ADMIN-MODUS")
    elif ist_pro: 
        st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        st.markdown(f'''<a href="https://buy.stripe.com" target="_blank"><button style="width:100%; border-radius:5px; background-color:#303a8a; color:white; border:none; padding:12px; cursor:pointer; font-weight:bold;">👉 JETZT PRO FREISCHALTEN</button></a>''', unsafe_allow_html=True)
   
    st.divider()
    if "kosten" not in st.session_state: st.session_state.kosten = 0.0
    if is_admin:
        with st.expander("📊 API-Verbrauch (Nur Admin)"):
            st.metric("Gesamtkosten OpenAI", f"${st.session_state.kosten:.4f}")

# --- 5. HAUPT-LOGIK ---
st.title("Amtsschimmel-Killer 📄🚀")
upload = st.file_uploader("Behördenbrief hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_img, col_ana = st.columns(2)
    current_img = None
    
    with col_img:
        st.subheader("📸 Dokument")
        if upload.type == "application/pdf":
            try:
                pages_prev = convert_from_bytes(upload.getvalue(), first_page=1, last_page=1, dpi=100)
                current_img = pages_prev[0] if isinstance(pages_prev, list) else pages_prev
                st.image(current_img, use_container_width=True)
            except: st.info("PDF zur Analyse bereit.")
        else:
            current_img = Image.open(upload)
            st.image(current_img, use_container_width=True)

    with col_ana:
        st.subheader("🧠 KI-Analyse")
        if st.button("🚀 Analyse starten", use_container_width=True):
            with st.status("Verarbeite...", expanded=True) as status:
                if upload.type == "application/pdf":
                    pages = convert_from_bytes(upload.getvalue(), dpi=150)
                    full_text = "".join([pytesseract.image_to_string(p, lang='deu') for p in pages])
                else:
                    full_text = pytesseract.image_to_string(current_img, lang='deu')

                if len(full_text.strip()) < 15:
                    status.update(label="❌ Fehler: Kein Text", state="error")
                    st.error("Text unleserlich.")
                else:
                    # VERBESSERTER PROMPT FÜR AUSFÜHRLICHE ENTWÜRFE
                    prompt = f"""Analysiere diesen Behördentext gründlich: {full_text}
                    
                    Erstelle eine detaillierte Analyse im folgenden Format:
                    BEHOERDE: [Name der Behörde]
                    AZ: [Aktenzeichen/Referenznummer]
                    ERKLÄRUNG: [Was genau wird gefordert? Erkläre es einfach für einen Laien in ca. 3-4 Sätzen.]
                    FRISTEN: [Wann ist die Deadline? Was passiert bei Versäumnis?]
                    FORMFEHLER: [Suche nach fehlenden Unterschriften, fehlenden Rechtsbehelfsbelehrungen oder unklaren Fristangaben.]
                    ANTWORT: [Erstelle einen VOLLSTÄNDIGEN, förmlichen Antwortbrief oder Widerspruch. Nutze Platzhalter wie [Name], [Datum], [Ort]. Der Text muss fundiert, höflich und juristisch präzise klingen. Mindestens 2-3 Absätze!]
                    STEUER: [Falls relevant: Steuerbetrag und Zahlungsziel.]"""
                    
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "system", "content": "Du bist ein erfahrener Experte für deutsches Verwaltungsrecht und Behördenkorrespondenz."}, {"role": "user", "content": prompt}]
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
                    with st.expander("💡 Was will die Behörde von mir?", expanded=True):
                        st.write(erk)
                    
                    if "Keine" not in fehler and "nicht gefunden" not in fehler.lower():
                        st.error(f"🚨 **Potenzieller Formfehler entdeckt:** {fehler}")
                    
                    st.warning(f"📅 **Wichtige Fristen:** {fri}")

                    if ist_pro:
                        st.subheader("📥 Deine Profi-Dokumente")
                        
                        # Textbereich für den Antwortbrief (Nutzer kann ihn hier noch bearbeiten)
                        final_a = st.text_area("Vorschau & Bearbeitung des Antwortbriefs:", value=ant, height=300)
                        
                        col_pdf, col_xls = st.columns(2)
                        
                        # PDF Download
                        pdf_data = create_full_pdf(erk, fri, final_a, ste, meta, fehler)
                        col_pdf.download_button("📥 PDF-Gutachten laden", data=pdf_data, file_name=f"Analyse_{meta['behoerde']}.pdf", use_container_width=True)
                        
                        # Excel Download
                        excel_data = create_excel({
                            "Datum der Analyse": datetime.now().strftime("%d.%m.%Y"),
                            "Behörde": meta['behoerde'],
                            "Aktenzeichen": meta['az'],
                            "Zusammenfassung": erk,
                            "Fristen": fri,
                            "Formfehler": fehler,
                            "Steuer-Info": ste,
                            "Antwortentwurf": final_a
                        })
                        col_xls.download_button("📊 Excel-Tabelle laden", data=excel_data, file_name=f"Daten_{meta['behoerde']}.xlsx", use_container_width=True)
                    else:
                        st.info("🔓 Schalte PRO frei, um den ausführlichen Antwortbrief und die Excel-Auswertung zu erhalten.")

st.divider()
st.caption("v11.2 - Profi-Briefe & Auto-Excel Layout")
