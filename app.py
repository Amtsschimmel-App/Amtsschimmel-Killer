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
st.set_page_config(page_title="Amtsschimmel Killer", page_icon="📄", layout="wide")

# 2. API INITIALISIERUNG (Daten aus Secrets laden)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    stripe.api_key = st.secrets["STRIPE_API_KEY"]
except Exception as e:
    st.error("⚠️ API-Keys fehlen in den Secrets! Bitte in Streamlit Cloud unter Settings -> Secrets eintragen.")

# TESSERACT PFAD-FIX (Für Cloud-Server)
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# --- HILFSFUNKTIONEN ---
def remove_emojis(text):
    if not text: return ""
    # FPDF kann keine Emojis/Sonderzeichen, daher filtern wir sie für das PDF
    return text.encode('latin-1', 'ignore').decode('latin-1')

def create_full_pdf(erk, fri, ant, ste, meta, fehler):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(30, 58, 138) # Dunkelblau
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=1, align='C')
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    sections = [
        ("Behoerde", meta.get('behoerde', '-')),
        ("Aktenzeichen", meta.get('az', '-')),
        ("Zusammenfassung", erk),
        ("Fristen & Termine", fri),
        ("Formfehler-Analyse", fehler),
        ("Antwortentwurf", ant)
    ]
    
    for title, content in sections:
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(240, 240, 245)
        pdf.cell(0, 8, title, ln=1, fill=True)
        pdf.set_font("Arial", size=10)
        pdf.ln(2)
        pdf.multi_cell(0, 6, txt=remove_emojis(content))
        pdf.ln(4)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 3. ZAHLUNGSPRÜFUNG (SICHERHEIT) ---
# Wir schauen in die URL, ob Stripe eine session_id mitgeschickt hat
session_id = st.query_params.get("session_id")
ist_pro = False

if session_id:
    try:
        # Prüfung direkt bei Stripe, ob diese Session bezahlt wurde
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        if checkout_session.payment_status == "paid":
            ist_pro = True
            st.toast("✨ PRO-Modus erfolgreich aktiviert!", icon="✅")
    except Exception:
        st.sidebar.warning("Zahlungsverifizierung fehlgeschlagen.")

# --- 4. UI & SIDEBAR ---
with st.sidebar:
    logo_file = "icon_final_blau.png"
    if os.path.exists(logo_file):
        st.image(logo_file, width=150)
    
    st.header("Dein Account")
    if ist_pro: 
        st.success("✨ PRO-Modus aktiv")
    else:
        st.info("🔓 Basis-Modus")
        # Hier ist dein Bezahl-Link
        st.markdown(f'''
            <a href="https://buy.stripe.com" target="_blank">
                <button style="width:100%; border-radius:5px; background-color:#303a8a; color:white; border:none; padding:10px; cursor:pointer;">
                    👉 Pro freischalten
                </button>
            </a>
        ''', unsafe_allow_html=True)
    
    st.divider()
    if "kosten" not in st.session_state: st.session_state.kosten = 0.0
    st.caption(f"KI-Verbrauch: ${st.session_state.kosten:.4f}")
    st.caption("v10.0 - Secure Payment & Signature Check")

# --- 5. HAUPT-LOGIK ---
st.title("Amtsschimmel-Killer 📄🚀")
st.markdown("Lade deinen Behördenbrief hoch. Wir checken Fristen, Formfehler und schreiben die Antwort.")

upload = st.file_uploader("Datei hochladen (PDF, JPG, PNG)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_img, col_ana = st.columns([1, 1])
    
    with col_img:
        st.subheader("📸 Dokument-Vorschau")
        if upload.type == "application/pdf":
            try:
                preview = convert_from_bytes(upload.getvalue(), first_page=1, last_page=1, dpi=100)
                st.image(preview[0], use_container_width=True)
            except:
                st.info("PDF-Vorschau nicht verfügbar, Analyse bereit.")
        else:
            st.image(upload, use_container_width=True)

    with col_ana:
        st.subheader("🧠 Analyse-Zentrale")
        if st.button("🚀 Vollanalyse starten", use_container_width=True):
            with st.status("Dokument wird gelesen...", expanded=True) as status:
                
                # Schritt 1: OCR (Texterkennung)
                full_text = ""
                if upload.type == "application/pdf":
                    pages = convert_from_bytes(upload.getvalue(), dpi=150)
                    for page in pages:
                        full_text += pytesseract.image_to_string(page, lang='deu') + "\n"
                else:
                    full_text = pytesseract.image_to_string(Image.open(upload), lang='deu')
                
                if len(full_text.strip()) < 10:
                    st.error("Kein Text erkannt. Bitte ein schärferes Foto hochladen!")
                    st.stop()

                # Schritt 2: KI-Analyse (Prompt mit Killer-Feature)
                status.write("🤖 KI prüft Formfehler und Fristen...")
                prompt = f"""
                Verhalte dich wie ein Experte für deutsches Verwaltungsrecht.
                Analysiere diesen Text:
                ---
                {full_text}
                ---
                GIB DEINE ANTWORT STRENG IN DIESEM FORMAT:
                BEHOERDE: [Name der Behörde]
                AZ: [Aktenzeichen/Referenz]
                ERKLÄRUNG: [Einfache Zusammenfassung des Inhalts]
                FRISTEN: [Wichtige Daten und Fristende]
                FORMFEHLER: [Prüfe: Fehlt die Unterschrift? Fehlt die Rechtsbehelfsbelehrung? Ist die Frist falsch berechnet? Antworte konkret!]
                ANTWORT: [Höflicher, rechtssicherer Antwortentwurf]
                STEUER: [Falls Beträge genannt werden: Betrag | Grund]
                """
                
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "Du bist der Amtsschimmel-Killer. Hilf Bürgern, Behördenbriefe zu verstehen."}, 
                              {"role": "user", "content": prompt}]
                )
                
                # Kosten-Tracker
                st.session_state.kosten += (res.usage.total_tokens / 1000) * 0.00015
                raw = res.choices[0].message.content

                # Hilfsfunktion zum Zerlegen der KI-Antwort
                def ext(tag, src):
                    m = re.search(rf"{tag}:(.*?)(?=\n[A-Z]+:|$)", src, re.DOTALL | re.IGNORECASE)
                    return m.group(1).strip() if m else "Nicht gefunden"

                meta = {"behoerde": ext("BEHOERDE", raw), "az": ext("AZ", raw)}
                erk, fri, fehler, ant, ste = ext("ERKLÄRUNG", raw), ext("FRISTEN", raw), ext("FORMFEHLER", raw), ext("ANTWORT", raw), ext("STEUER", raw)
                
                status.update(label="✅ Analyse abgeschlossen!", state="complete")

                # ERGEBNIS-ANZEIGE
                st.header(meta['behoerde'])
                st.info(f"**Aktenzeichen:** {meta['az']}")
                
                with st.expander("💡 Zusammenfassung (Was wollen die?)", expanded=True):
                    st.write(erk)
                
                # Das Killer-Feature: Formfehler-Warnung
                if "Keine" not in fehler and "nicht gefunden" not in fehler.lower():
                    st.error(f"🚨 **MÖGLICHER FORMFEHLER ENTDECKT:**\n\n{fehler}")
                else:
                    st.success("✅ Formale Prüfung: Keine offensichtlichen Fehler bei Unterschrift oder Belehrung gefunden.")

                st.warning(f"📅 **Fristen:** {fri}")

                # PRO-Bereich
                st.divider()
                if ist_pro:
                    st.subheader("✍️ Dein Pro-Antwortentwurf")
                    final_a = st.text_area("Du kannst den Brief hier noch anpassen:", value=ant, height=250)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        pdf_data = create_full_pdf(erk, fri, final_a, ste, meta, fehler)
                        st.download_button("📥 PDF-Gutachten speichern", data=pdf_data, file_name=f"Analyse_{meta['az']}.pdf", mime="application/pdf", use_container_width=True)
                    with c2:
                        st.button("✉️ Per E-Mail senden (Coming Soon)", disabled=True, use_container_width=True)
                else:
                    st.subheader("🔒 Pro-Features")
                    st.text_area("Antwortentwurf (Vorschau)", value="Bezahle Pro, um den fertigen Antwortentwurf zu sehen und als PDF zu laden.", height=100, disabled=True)
                    st.info("Schalte PRO frei, um den kompletten Antwortbrief und das PDF-Gutachten zu erhalten.")

# FUSSZEILE
st.divider()
st.caption("Rechtlicher Hinweis: Diese KI-Analyse ersetzt keine Rechtsberatung durch einen Anwalt.")
