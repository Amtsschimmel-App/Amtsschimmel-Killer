import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
from fpdf import FPDF 
from datetime import datetime

# ==========================================
# 1. SETUP & GUTHABEN-LOGIK
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

if "credits" not in st.session_state:
    st.session_state.credits = 0
if "full_res" not in st.session_state:
    st.session_state.full_res = None
if "processed_sessions" not in st.session_state:
    st.session_state.processed_sessions = set()

# STRIPE LINKS
STRIPE_1 = "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" 
STRIPE_2 = "https://buy.stripe.com/8x228retRbj50paalq1gs03" 
STRIPE_3 = "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04" 

# ZAHLUNGSERKENNUNG (Stripe Return Check)
params = st.query_params
sid = params.get("session_id", "")
if "pack" in params and sid not in st.session_state.processed_sessions:
    val = params["pack"]
    if val == "1": st.session_state.credits += 1
    elif val == "2": st.session_state.credits += 3
    elif val == "3": st.session_state.credits += 10
    if sid: st.session_state.processed_sessions.add(sid)
    st.toast("✅ Zahlung erfolgreich verbucht!", icon="💰")

# Admin-Backdoor für Tests
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

# ==========================================
# 2. PDF-EXPORT FUNKTION
# ==========================================
def generate_pdf_bytes(data_dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=True, align='C')
    pdf.ln(10)
    for title, content in data_dict.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, title.upper(), ln=True)
        pdf.set_font("Arial", size=11)
        txt_safe = str(content).encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, txt=txt_safe)
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 3. DESIGN & STYLING
# ==========================================
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; }
        .paket-card { border: 1px solid #0d47a1; padding: 10px; border-radius: 10px; background-color: #f8fbff; margin-bottom: 5px; text-align: center; }
        .price-tag { font-size: 15px; font-weight: bold; color: #0d47a1; margin: 2px; }
        .no-abo-text { font-size: 10px; color: #d32f2f; font-weight: bold; text-transform: uppercase; }
        .result-box { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #0d47a1; margin-bottom: 15px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); }
        .box-title { font-weight: bold; color: #0d47a1; margin-bottom: 5px; text-transform: uppercase; font-size: 13px; border-bottom: 1px solid #eee; padding-bottom: 3px; }
    </style>
    """, unsafe_allow_html=True)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# 4. INFOS & RECHTLICHES (MIT ABSTÄNDEN)
# ==========================================
st.title("Amtsschimmel-Killer 🪓")

t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.write("**Amtsschimmel-Killer**")
        st.write("Betreiberin: Elisabeth Reinecke")
        st.write("Ringelsweide 9")
        st.write("40223 Düsseldorf")
        st.write("")
        st.write("**Kontakt:**")
        st.write("Telefon: +49 211 15821329")
        st.write("E-Mail: amtsschimmel-killer@proton.me")
        st.write("Web: amtsschimmel-killer.streamlit.app")
        st.write("")
        st.write("**Haftung:**")
        st.write("Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.write("**1. Datenschutz auf einen Blick**")
        st.write("Wir behandeln Ihre personenbezogenen Daten vertraulich (DSGVO).")
        st.write("")
        st.write("**2. Datenerfassung & Hosting**")
        st.write("Hosting auf Streamlit Cloud. Logfiles werden automatisch vom Hoster erfasst.")
        st.write("")
        st.write("**3. Dokumentenverarbeitung**")
        st.write("Übertragung via TLS an OpenAI (USA). Keine Speicherung der Briefe auf unseren Servern.")
        st.write("")
        st.write("**4. Zahlungsabwicklung**")
        st.write("Erfolgt über Stripe. Wir erhalten nur die Zahlungsbestätigung.")
        st.write("")
        st.write("**5. Ihre Rechte**")
        st.write("Recht auf Auskunft & Löschung via amtsschimmel-killer@proton.me.")

with t3:
    with st.expander("❓ FAQ"):
        st.write("**Ist das ein Abonnement?**")
        st.write("Nein. Jede Zahlung ist eine Einmalzahlung. Kein Abo!")
        st.write("")
        st.write("**Wie sicher sind meine Dokumente?**")
        st.write("Verschlüsselte Verarbeitung im Arbeitsspeicher, keine dauerhafte Speicherung.")
        st.write("")
        st.write("**Ersetzt die App eine Rechtsberatung?**")
        st.write("Nein. Wir bieten eine Formulierungshilfe und Textverständnis.")
        st.write("")
        st.write("**Was passiert bei Fehlern?**")
        st.write("Ein Scan wird nur bei erfolgreicher Analyse berechnet.")

with t4:
    with st.expander("📝 Vorlagen"):
        st.write("**Fristverlängerung:**")
        st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen.")
        st.write("")
        st.write("**Widerspruch:**")
        st.code("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum] lege ich hiermit Widerspruch ein. Begründung folgt.")
        st.write("")
        st.write("**Akteneinsicht:**")
        st.code("Sehr geehrte Damen und Herren, zur Prüfung beantrage ich gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht.")

st.divider()

# ==========================================
# 5. HAUPTBEREICH
# ==========================================
c_pak, c_up, c_res = st.columns([0.9, 1.2, 1.5])

with c_pak:
    st.subheader("🌐 Sprachen")
    lang = st.selectbox("Wahl", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇸🇦 العربية", "🇪🇸 Español", "🇫🇷 Français", "🇮🇹 Italiano", "🇺🇦 Українська"], label_visibility="collapsed")
    st.write("---")
    for t, p, l in [("Analyse (1 Dok)", "3,99 €", STRIPE_1), ("Spar-Paket (3 Dok)", "9,99 €", STRIPE_2), ("Sorglos-Paket (10 Dok)", "19,99 €", STRIPE_3)]:
        st.markdown(f'<div class="paket-card"><div class="paket-title">{t}</div><div class="price-tag">{p}</div><div class="no-abo-text">❌ KEIN ABO</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", l)

with c_up:
    st.subheader("📄 Upload")
    st.info(f"Guthaben: **{st.session_state.credits} Scans**")
    upped = st.file_uploader("Datei", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if upped:
        extracted_text = ""
        if upped.type == "application/pdf":
            raw = upped.read()
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                for page in pdf.pages: extracted_text += (page.extract_text() or "") + "\n"
            st.image(convert_from_bytes(raw, first_page=1, last_page=1), caption="Vorschau", use_container_width=True)
        else:
            img = Image.open(upped)
            st.image(img, caption="Vorschau", use_container_width=True)
            extracted_text = pytesseract.image_to_string(img)
        
        if st.button("🚀 JETZT ANALYSIEREN", type="primary", use_container_width=True):
            if st.session_state.credits > 0:
                with st.spinner("KI analysiert..."):
                    try:
                        # Verbesserter Prompt für stabiles Splitting
                        prompt = f"Analysiere diesen Text auf {lang}. Antworte NUR in diesem Format:\n###SUM###\n(Zusammenfassung)\n###FRIST###\n(Fristen)\n###ANTWORT###\n(Entwurf)\n\nText: {extracted_text}"
                        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
                        full = res.choices[0].message.content
                        
                        # Sichereres Splitting
                        st.session_state.full_res = {
                            "Zusammenfassung": full.split("###SUM###")[-1].split("###FRIST###")[0].strip(),
                            "Fristen": full.split("###FRIST###")[-1].split("###ANTWORT###")[0].strip(),
                            "Antwort-Entwurf": full.split("###ANTWORT###")[-1].strip()
                        }
                        st.session_state.credits -= 1
                        st.balloons() # <--- Die bunten Luftballons!
                        st.rerun()
                    except Exception as e: st.error(f"Fehler bei der Analyse: {e}")
            else: st.error("Kein Guthaben! Bitte links ein Paket wählen.")

with c_res:
    st.subheader("🔍 Ergebnis")
    if st.session_state.full_res:
        for title, text in st.session_state.full_res.items():
            st.markdown(f'<div class="result-box"><div class="box-title">{title}</div>{text}</div>', unsafe_allow_html=True)
        
        pdf_data = generate_pdf_bytes(st.session_state.full_res)
        st.download_button(label="📥 PDF herunterladen", data=pdf_data, file_name="Analyse.pdf", mime="application/pdf")
        if st.button("🔄 Neuer Scan"):
            st.session_state.full_res = None
            st.rerun()
