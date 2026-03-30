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

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .pkg-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .pkg-price { font-size: 1.5rem; font-weight: bold; color: #1E3A8A; margin: 0.5rem 0; }
    .pkg-footer { font-size: 0.8rem; color: gray; margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNKTIONEN ---

def get_ai_analysis(text):
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """Du bist ein Experte für deutsches Verwaltungsrecht. 
                Erstelle SEHR AUSFÜHRLICHE, rechtlich fundierte und sauber formatierte Entwürfe. 
                Die Antwortschreiben und Widersprüche müssen lang genug sein, um professionell zu wirken.
                Füge UNTEN in jedem Schreiben (Antwort & Widerspruch) zwingend Platzhalter für die Adresse ein:
                [Vorname Nachname]
                [Straße Hausnummer]
                [PLZ Ort]
                [Datum]
                
                Antworte NUR im JSON-Format: {'analyse': '...', 'antwort': '...', 'widerspruch': '...', 'frist': 'DD.MM.YYYY'}"""},
                {"role": "user", "content": text}
            ],
            response_format={ "type": "json_object" }
        )
        data = json.loads(response.choices[0].message.content)
        for key in ['analyse', 'antwort', 'widerspruch']:
            data[key] = data[key].replace('\\n', '\n')
        return data
    except Exception as e:
        return {"analyse": f"Fehler: {str(e)}", "antwort": "Fehler", "widerspruch": "Fehler", "frist": "Nicht erkannt"}

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

def create_word_complete(analyse, antwort, widerspruch):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Report', 0)
    for title, content in [("Analyse", analyse), ("Antwort", antwort), ("Widerspruch", widerspruch)]:
        doc.add_heading(title, level=1)
        doc.add_paragraph(str(content))
    target = BytesIO()
    doc.save(target)
    return target.getvalue()

def create_excel_pro(ana, ant, wid):
    output = BytesIO()
    df = pd.DataFrame([{"Kategorie": "1. Analyse", "Inhalt": ana}, {"Kategorie": "2. Antwort", "Inhalt": ant}, {"Kategorie": "3. Widerspruch", "Inhalt": wid}])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        wrap = writer.book.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
        worksheet.set_column(0, 0, 25, wrap)
        worksheet.set_column(1, 1, 120, wrap)
    return output.getvalue()

def perform_ocr_preview(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.getvalue())
            return "".join([pytesseract.image_to_string(img, lang='deu') + "\n" for img in images])
        return pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    except: return "Vorschau nicht möglich."

# --- 4. TOP-BAR: RECHTLICHES (MIT DEN GEWÜNSCHTEN ABSTÄNDEN) ---
t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""
### Amtsschimmel-Killer

**Betreiberin:**  
Elisabeth Reinecke  
Ringelsweide 9  
40223 Düsseldorf  

<br><br><br>

**Kontakt:**  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
Web: amtsschimmel-killer.streamlit.app  

<br><br><br>

**Haftung:**  
Inhalte nach § 5 TMG.  
Keine Haftung für KI-generierte Texte.
        """, unsafe_allow_html=True)

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""
**1. Datenschutz auf einen Blick**  
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

**2. Datenerfassung & Hosting**  
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

**3. Dokumentenverarbeitung**  
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

**4. Zahlungsabwicklung (Stripe)**  
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

**5. Ihre Rechte**  
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
        """)

with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""
**Ist das ein Abonnement?**  
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

**Wie sicher sind meine Dokumente?**  
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

**Ersetzt die App eine Rechtsberatung?**  
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

**Was passiert, wenn der Scan fehlschlägt?**  
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

**Wie erreiche ich Elisabeth Reinecke?**  
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
        """)

with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""
**Fristverlängerung:**  
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen.  
<br>
Mit freundlichen Grüßen,  
[Name]

<br><br>

**Widerspruch einlegen (Fristwahrend):**  
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben.  
<br>
Mit freundlichen Grüßen,  
[Name]

<br><br>

**Akteneinsicht einfordern:**  
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht.  
<br>
Mit freundlichen Grüßen,  
[Name]
        """, unsafe_allow_html=True)

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

# LINKS: PAKETE & STRIPE LINKS
with col_left:
    try: st.image("icon_final_blau.png", width=160)
    except: st.markdown("### 🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache wählen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español", "NL Nederlands", "RO Română", "GR Ελληνικά", "CN 中文", "VN Tiếng Việt"], label_visibility="collapsed")
    st.write("")
    
    with st.container(border=True):
        st.markdown('<div class="pkg-icon">📄</div>**Analyse (1 Dokument)**<div class="pkg-price">3,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", use_container_width=True)

    with st.container(border=True):
        st.markdown('<div style="background-color: #ebf5fb; padding: 10px; border-radius: 10px;">'
                    '<div class="pkg-icon">🥈</div>**Spar-Paket (3 Dokumente)**<div class="pkg-price">9,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="pkg-icon">🏛️</div>**Pro-Paket (10 Dokumente)**<div class="pkg-price">19,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com", use_container_width=True)

with col_mid:
    st.subheader("1. Dokument hochladen")
    uploaded_file = st.file_uploader("Brief fotografieren oder PDF wählen", type=['pdf', 'png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    # NEU: KALENDER / FRIST-CHECKER
    st.write("")
    st.subheader("📅 Frist-Checker")
    erhalt_datum = st.date_input("Wann haben Sie den Brief erhalten?", datetime.now())
    frist_ende = erhalt_datum + timedelta(days=30)
    st.info(f"Die gesetzliche Frist endet voraussichtlich am: **{frist_ende.strftime('%d.%m.%Y')}**")

    if uploaded_file is not None:
        if st.button("Analyse starten ✨", use_container_width=True):
            with st.spinner("Amtsschimmel wird vertrieben..."):
                text_content = perform_ocr_preview(uploaded_file)
                st.session_state['analysis_results'] = get_ai_analysis(text_content)

with col_right:
    st.subheader("2. Ergebnisse")
    if 'analysis_results' in st.session_state:
        res = st.session_state['analysis_results']
        
        tab1, tab2, tab3 = st.tabs(["Analyse", "Antwortbrief", "Widerspruch"])
        with tab1:
            st.write(res['analyse'])
        with tab2:
            st.text_area("Ihr Antwortbrief-Entwurf:", res['antwort'], height=300)
        with tab3:
            st.text_area("Ihr Widerspruch-Entwurf:", res['widerspruch'], height=300)
            
        st.divider()
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            pdf_data = create_pdf_adobe_ready(res['analyse'], res['antwort'], res['widerspruch'])
            st.download_button("📥 PDF Download", pdf_data, "Analyse.pdf", "application/pdf", use_container_width=True)
        with col_dl2:
            word_data = create_word_complete(res['analyse'], res['antwort'], res['widerspruch'])
            st.download_button("📥 Word Download", word_data, "Analyse.docx", use_container_width=True)
    else:
        st.info("Bitte laden Sie links ein Dokument hoch und starten Sie die Analyse.")
