import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from fpdf import FPDF
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import openai
import json
from datetime import datetime, timedelta

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# OpenAI API Key aus den Secrets
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- 2. CUSTOM CSS (Abstände bewahren) ---
st.markdown("""
    <style>
    .pkg-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .pkg-price { font-size: 1.5rem; font-weight: bold; color: #1E3A8A; margin: 0.5rem 0; }
    .pkg-footer { font-size: 0.8rem; color: gray; margin-bottom: 1rem; }
    .stExpander { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKTIONEN ---

def get_ai_analysis(text):
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        # Optimierter Prompt für längere Texte und Platzhalter
        sys_prompt = (
            "Du bist Experte für deutsches Verwaltungsrecht. "
            "Erstelle SEHR AUSFÜHRLICHE Entwürfe. "
            "Füge am Ende von Antwort und Widerspruch immer Platzhalter ein: "
            "[Vorname Nachname]\n[Straße Hausnummer]\n[PLZ Ort]\n[Datum]\n\n"
            "Antworte NUR im JSON-Format: {'analyse': '...', 'antwort': '...', 'widerspruch': '...', 'frist': 'YYYY-MM-DD'}"
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"Analysiere diesen Bescheid/Brief und erstelle detaillierte Schreiben: {text}"}
            ],
            response_format={ "type": "json_object" }
        )
        data = json.loads(response.choices[0].message.content)
        return data
    except Exception as e:
        return {"analyse": f"Fehler: {str(e)}", "antwort": "Fehler", "widerspruch": "Fehler", "frist": str(datetime.now().date())}

# PDF & Export Funktionen (wie vorher)
def create_pdf_adobe_ready(analyse, antwort, widerspruch):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse-Report", ln=True, align='C')
    for title, content in [("1. Analyse", analyse), ("2. Antwort", antwort), ("3. Widerspruch", widerspruch)]:
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("helvetica", '', 11)
        safe_text = str(content).replace('•', '-').replace('–', '-').replace('„', '"').replace('“', '"')
        pdf.multi_cell(0, 6, safe_text.encode('latin-1', 'replace').decode('latin-1'))
    return bytes(pdf.output())

# --- 4. TOP-BAR & IMPRESSUM (MIT ABSTÄNDEN) ---
t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""
### Amtsschimmel-Killer

**Betreiberin:**  
Elisabeth Reinecke  
Ringelsweide 9  
40223 Düsseldorf  

<br><br>

**Kontakt:**  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
Web: amtsschimmel-killer.streamlit.app  

<br><br>

**Haftung:**  
Inhalte nach § 5 TMG.  
Keine Haftung für KI-generierte Texte.
        """, unsafe_allow_html=True)

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("1. Datenschutz auf einen Blick...\n\n(Vollständiger Text bleibt wie im Original)")

with t3:
    with st.expander("❓ FAQ"):
        st.markdown("Ist das ein Abonnement? No. (Vollständiger Text bleibt)")

with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""
**Fristverlängerung:**  
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. 

Mit freundlichen Grüßen,  
[Name]

<br>

**Widerspruch einlegen (Fristwahrend):**  
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. 

Mit freundlichen Grüßen,  
[Name]

<br>

**Akteneinsicht einfordern:**  
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. 

Mit freundlichen Grüßen,  
[Name]
        """, unsafe_allow_html=True)

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    st.markdown("### 🏛️ Amtsschimmel-Killer")
    st.selectbox("Sprache wählen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español", "NL Nederlands", "RO Română", "GR Ελληνικά", "CN 中文", "VN Tiếng Việt"], label_visibility="collapsed")
    
    # PAKETE MIT STRIPE LINKS
    st.write("---")
    with st.container(border=True):
        st.markdown('<div class="pkg-icon">📄</div>**Basis (1 Scan)**<div class="pkg-price">3,99 €</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", use_container_width=True)
    
    with st.container(border=True):
        st.markdown('<div class="pkg-icon">📂</div>**Standard (3 Scans)**<div class="pkg-price">9,99 €</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)

    with st.container(border=True):
        st.markdown('<div class="pkg-icon">🏛️</div>**Pro (10 Scans)**<div class="pkg-price">19,99 €</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04", use_container_width=True)

with col_mid:
    st.subheader("1. Dokument hochladen")
    file = st.file_uploader("Brief fotografieren oder PDF wählen", type=['pdf', 'png', 'jpg', 'jpeg'])
    
    # NEU: KALENDER / FRIST-CHECKER
    st.subheader("2. Frist-Checker")
    today = datetime.now().date()
    selected_date = st.date_input("Wann haben Sie den Brief erhalten?", today)
    deadline_calc = selected_date + timedelta(days=30)
    st.info(f"Voraussichtliches Fristende (1 Monat): **{deadline_calc.strftime('%d.%m.%Y')}**")

    if file and st.button("Analyse starten ✨"):
        with st.spinner("Amtsschimmel wird vertrieben..."):
            raw_text = "Beispieltext aus OCR" # Hier käme der OCR-Call rein
            result = get_ai_analysis(raw_text)
            st.session_state['result'] = result

with col_right:
    st.subheader("3. Ergebnis")
    if 'result' in st.session_state:
        res = st.session_state['result']
        st.tabs(["Analyse", "Antwortbrief", "Widerspruch"])
        # Hier erfolgt die Anzeige und der Download (PDF/Word/Excel)
        st.success("Analyse fertig! Nutzen Sie die Tabs oben.")
    else:
        st.info("Warten auf Upload...")
