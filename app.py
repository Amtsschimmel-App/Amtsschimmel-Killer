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

# --- 3. FUNKTIONEN (KI, EXCEL, WORD, PDF) ---
def get_ai_analysis(text):
    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        sys_msg = (
            "Du bist ein Experte für deutsches Verwaltungsrecht. Erstelle SEHR AUSFÜHRLICHE Entwürfe. "
            "Antwortschreiben und Widerspruch müssen detailliert sein und folgende Platzhalter am Ende enthalten: "
            "[Vorname Nachname], [Straße Hausnummer], [PLZ Ort], [Datum]. "
            "Antworte NUR im JSON-Format: {'analyse': '...', 'antwort': '...', 'widerspruch': '...', 'frist': 'DD.MM.YYYY'}"
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": text}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices.message.content)
    except:
        return {"analyse": "Fehler bei der Analyse", "antwort": "Fehler", "widerspruch": "Fehler"}

def create_excel_pro(ana, ant, wid):
    output = BytesIO()
    df = pd.DataFrame([{"Kategorie": "Analyse", "Inhalt": ana}, {"Kategorie": "Antwort", "Inhalt": ant}, {"Kategorie": "Widerspruch", "Inhalt": wid}])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Ergebnis')
        worksheet = writer.sheets['Ergebnis']
        wrap = writer.book.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
        worksheet.set_column(0, 0, 20, wrap)
        worksheet.set_column(1, 1, 120, wrap)
    return output.getvalue()

def create_word_complete(ana, ant, wid):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Analyse-Report', 0)
    for t, c in [("1. Analyse", ana), ("2. Antwortschreiben", ant), ("3. Widerspruch", wid)]:
        doc.add_heading(t, level=1)
        doc.add_paragraph(str(c))
    target = BytesIO()
    doc.save(target)
    return target.getvalue()

def create_pdf_adobe_ready(ana, ant, wid):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Report", ln=True, align='C')
    for title, content in [("1. Analyse", ana), ("2. Antwort", ant), ("3. Widerspruch", wid)]:
        pdf.ln(10); pdf.set_font("helvetica", 'B', 14); pdf.cell(0, 10, title, ln=True)
        pdf.set_font("helvetica", '', 11)
        pdf.multi_cell(0, 6, str(content).encode('latin-1', 'replace').decode('latin-1'))
    return bytes(pdf.output())

def perform_ocr_preview(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.getvalue())
            return "".join([pytesseract.image_to_string(img, lang='deu') + "\n" for img in images])
        return pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    except: return "Texterkennung fehlgeschlagen."

# --- 4. TOP-BAR: RECHTLICHES (VOLLSTÄNDIG & MIT GROSSEN ABSTÄNDEN) ---
t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""
**Amtsschimmel-Killer**

**Betreiberin:**

Elisabeth Reinecke

Ringelsweide 9
40223 Düsseldorf

<br>

**Kontakt:**
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

<br>

**Haftung:**
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        """, unsafe_allow_html=True)

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""
**Datenschutz:**

**1. Datenschutz auf einen Blick**
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

<br>

**2. Datenerfassung & Hosting**
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

<br>

**3. Dokumentenverarbeitung**
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

<br>

**4. Zahlungsabwicklung (Stripe)**
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

<br>

**5. Ihre Rechte**
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me. 
        """, unsafe_allow_html=True)

with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""
**FAQ**

**Ist das ein Abonnement?**
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

<br>

**Wie sicher sind meine Dokumente?**
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

<br>

**Ersetzt die App eine Rechtsberatung?**
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

<br>

**Was passiert, wenn der Scan fehlschlägt?**
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

<br>

**Wie erreiche ich Elisabeth Reinecke?**
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
        """, unsafe_allow_html=True)

with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""
**Vorlagen:**

**Fristverlängerung:**
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

<br><br>

**Widerspruch einlegen (Fristwahrend)**
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

<br><br>

**Akteneinsicht einfordern:**
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
        """, unsafe_allow_html=True)

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

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
        st.markdown('<div style="background-color: #ebf5fb; padding: 10px; border-radius: 10px;"><div class="pkg-icon">🥈</div>**Spar-Paket (3 Dokumente)**<div class="pkg-price">9,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)

    with st.container(border=True):
        st.markdown('<div style="background-color: #fef9e7; padding: 10px; border-radius: 10px;"><div class="pkg-icon">🥇</div>**Sorglos-Paket (10 Dokumente)**<div class="pkg-price">19,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04", use_container_width=True)

with col_mid:
    st.subheader("1. Brief hochladen")
    up_file = st.file_uploader("Datei wählen", type=['pdf', 'png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    # --- AUTOMATISCHE VORSCHAU NACH UPLOAD ---
    if up_file:
        if up_file.type.startswith("image"):
            st.image(up_file, caption="Vorschau Ihres Dokuments", use_container_width=True)
        elif up_file.type == "application/pdf":
            st.info("PDF-Dokument hochgeladen. Bereit zur Analyse.")
            
        if st.button("Analyse starten ✨", use_container_width=True):
            with st.spinner("Amtsschimmel wird vertrieben..."):
                txt = perform_ocr_preview(up_file)
                st.session_state['res'] = get_ai_analysis(txt)

with col_right:
    st.subheader("2. Ergebnisse")
    if 'res' in st.session_state:
        r = st.session_state['res']
        
        # --- FRIST-CHECKER MIT KALENDER.ICO ---
        st.markdown("### 📅 Frist-Checker")
        erhalt = st.date_input("Wann kam der Brief offiziell an?", datetime.now())
        frist_calc = erhalt + timedelta(days=30)
        st.info(f"Ihre Frist endet voraussichtlich am: **{frist_calc.strftime('%d.%m.%Y')}**")
        
        st.write("---")
        t1, t2, t3 = st.tabs(["Analyse", "Antwortbrief", "Widerspruch"])
        with t1: st.write(r['analyse'])
        with t2: st.text_area("Entwurf Antwort:", r['antwort'], height=350)
        with t3: st.text_area("Entwurf Widerspruch:", r['widerspruch'], height=350)
        
        st.divider()
        st.download_button("📥 Excel Download", create_excel_pro(r['analyse'], r['antwort'], r['widerspruch']), "Analyse.xlsx", use_container_width=True)
        st.download_button("📥 Word Download", create_word_complete(r['analyse'], r['antwort'], r['widerspruch']), "Analyse.docx", use_container_width=True)
        st.download_button("📥 PDF Download", create_pdf_adobe_ready(r['analyse'], r['antwort'], r['widerspruch']), "Analyse.pdf", use_container_width=True)
    else:
        st.info("Bitte Dokument hochladen und Analyse starten.")
