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

# DEINE STRIPE LINKS
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

# Admin-Backdoor für Tests (wie im Screenshot: ?admin=GeheimAmt2024!)
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
# 3. DESIGN & STYLING (EXAKT WIE IM BILD)
# ==========================================
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; }
        .paket-card { 
            border: 1px solid #dee2e6; padding: 15px; border-radius: 10px; 
            background-color: #ffffff; margin-bottom: 10px; text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .price-tag { font-size: 16px; font-weight: bold; color: #0d47a1; margin: 5px; }
        .no-abo-text { font-size: 11px; color: #d32f2f; font-weight: bold; text-transform: uppercase; }
        .result-box { 
            background-color: #f0f7ff; padding: 15px; border-radius: 10px; 
            border-left: 5px solid #0d47a1; margin-bottom: 15px; 
        }
        .box-title { font-weight: bold; color: #0d47a1; margin-bottom: 5px; text-transform: uppercase; }
        .stLinkButton a {
            background-color: #0d47a1 !important; color: white !important;
            border-radius: 5px !important; width: 100% !important; display: block;
            text-decoration: none; text-align: center; padding: 8px; font-weight: bold;
        }
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
        st.write("Wir behandeln Ihre Daten vertraulich (DSGVO).")
        st.write("")
        st.write("**2. Hosting**")
        st.write("Streamlit Cloud erfasst Logfiles (IP/Browser). Wir nutzen diese nicht.")
        st.write("")
        st.write("**3. Dokumente**")
        st.write("TLS-Übertragung an OpenAI. Keine dauerhafte Speicherung der Briefe.")
        st.write("")
        st.write("**4. Stripe**")
        st.write("Daten zur Abrechnung bei Stripe. Wir sehen nur die Bestätigung.")
        st.write("")
        st.write("**5. Ihre Rechte**")
        st.write("Auskunft & Löschung via E-Mail.")

with t3:
    with st.expander("❓ FAQ"):
        st.write("**Abonnement?**")
        st.write("Nein. Jede Zahlung ist einmalig. Wir hassen Abos!")
        st.write("")
        st.write("**Sicherheit?**")
        st.write("Verschlüsselte Verarbeitung, Löschung nach dem Scan.")
        st.write("")
        st.write("**Rechtsberatung?**")
        st.write("Nein. Nur Formulierungshilfe & Textverständnis.")
        st.write("")
        st.write("**Fehlgeschlagen?**")
        st.write("Nur erfolgreiche Analysen verbrauchen Guthaben.")

with t4:
    with st.expander("📝 Vorlagen"):
        st.info("Fristverlängerung")
        st.code("...bitte ich um Verlängerung der gesetzten Frist bis zum [Datum]...")
        st.info("Widerspruch")
        st.code("...lege ich hiermit Widerspruch ein. Begründung folgt...")
        st.info("Akteneinsicht")
        st.code("...beantrage ich gemäß § 25 SGB X Akteneinsicht.")

st.divider()

# ==========================================
# 5. HAUPTBEREICH (DREI-SPALTEN-LAYOUT)
# ==========================================
col_links, col_mitte, col_rechts = st.columns([1, 1.2, 1.3])

# --- SPALTE LINKS: SPRACHEN & PAKETE ---
with col_links:
    st.subheader("🌐 Sprachen")
    lang = st.selectbox("Wahl", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇸🇦 العربية", "🇪🇸 Español", "🇫🇷 Français", "🇮🇹 Italiano", "🇺🇦 Ukrainska"], label_visibility="collapsed")
    
    st.write("")
    if os.path.exists("icon_final_blau.png"):
        st.image("icon_final_blau.png", width=120)
    
    st.write("---")
    
    pakete = [
        ("Amtsschimmel Killer: Analyse (1 Dokument)", "3,99 €", STRIPE_1),
        ("Amtsschimmel Killer: Spar Paket (3 Dokumente)", "9,99 €", STRIPE_2),
        ("Amtsschimmel Killer: Sorglos Paket (10 Dokumente)", "19,99 €", STRIPE_3)
    ]
    
    for titel, preis, link in pakete:
        st.markdown(f"""
            <div class="paket-card">
                <div style="font-size: 13px; font-weight: 500;">{titel}</div>
                <div class="price-tag">Einmalpreis {preis}</div>
                <div class="no-abo-text">❌ KEIN ABO</div>
            </div>
        """, unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", link, use_container_width=True)
        st.write("")

# --- SPALTE MITTE: UPLOAD & VORSCHAU ---
with col_mitte:
    st.subheader("📑 Upload & Vorschau")
    st.info(f"Guthaben: **{st.session_state.credits} Dokumente**")
    
    upped = st.file_uploader("Upload", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if upped:
        extracted_text = ""
        try:
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
                    with st.spinner("Amtsschimmel wird bekämpft..."):
                        # Stabiler Prompt mit Markern
                        prompt = f"Analysiere diesen Text auf {lang}. Trenne exakt so:\n###SUM###\n(Zusammenfassung)\n###FRIST###\n(Fristen)\n###ANTWORT###\n(Entwurf)\n\nText: {extracted_text}"
                        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
                        full = res.choices[0].message.content
                        
                        # Sicherer Split
                        st.session_state.full_res = {
                            "Zusammenfassung": full.split("###SUM###")[-1].split("###FRIST###")[0].strip(),
                            "Fristen": full.split("###FRIST###")[-1].split("###ANTWORT###")[0].strip(),
                            "Antwort-Entwurf": full.split("###ANTWORT###")[-1].strip()
                        }
                        st.session_state.credits -= 1
                        st.balloons() # Bunte Luftballons!
                        st.rerun()
                else:
                    st.error("Kein Guthaben! Bitte links Paket wählen.")
        except Exception as e:
            st.error(f"Fehler: {e}")

# --- SPALTE RECHTS: ANALYSE & ANTWORT ---
with col_rechts:
    st.subheader("🔍 Analyse & Antwort")
    if st.session_state.full_res:
        for title, text in st.session_state.full_res.items():
            st.markdown(f'<div class="result-box"><div class="box-title">{title}</div>{text}</div>', unsafe_allow_html=True)
        
        pdf_data = generate_pdf_bytes(st.session_state.full_res)
        st.download_button("📥 PDF herunterladen", data=pdf_data, file_name="Analyse.pdf", mime="application/pdf", use_container_width=True)
        
        if st.button("🔄 Neuer Scan", use_container_width=True):
            st.session_state.full_res = None
            st.rerun()
    else:
        st.info("Hier erscheint das Ergebnis nach dem Scan.")
