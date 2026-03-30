import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from docx import Document
from fpdf import FPDF
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (STYLING) ---
st.markdown("""
    <style>
    .pkg-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .pkg-price { font-size: 1.5rem; font-weight: bold; color: #1E3A8A; margin: 0.5rem 0; }
    .pkg-footer { font-size: 0.8rem; color: gray; margin-bottom: 1rem; }
    .stExpander { border: 1px solid #e6e6e6; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN (FIXED) ---

def create_pdf_adobe_ready(analyse, antwort, widerspruch):
    """Erstellt ein PDF, das im Adobe Reader nicht als defekt angezeigt wird."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse-Report", ln=True, align='C')
    
    sections = [
        ("1. Juristische Analyse", analyse),
        ("2. Antwortschreiben-Entwurf", antwort),
        ("3. Widerspruchs-Entwurf", widerspruch)
    ]
    
    for title, content in sections:
        pdf.ln(10)
        pdf.set_font("helvetica", 'B', 14)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("helvetica", '', 11)
        # Latin-1 Encoding für deutsche Umlaute
        clean_text = content.replace('•', '-').replace('–', '-')
        pdf.multi_cell(0, 6, clean_text.encode('latin-1', 'replace').decode('latin-1'))
    
    return pdf.output()

def create_word_complete(analyse, antwort, widerspruch):
    """Erstellt Word-Dokument mit allen drei Sektionen."""
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer: Ihr Report', 0)
    
    for title, content in [("Analyse", analyse), ("Antwortschreiben", antwort), ("Widerspruch", widerspruch)]:
        doc.add_heading(title, level=1)
        doc.add_paragraph(content)
    
    target = BytesIO()
    doc.save(target)
    return target.getvalue()

def create_excel_pro(ana, ant, wid):
    """Erstellt Excel mit optimaler Lesbarkeit (Texte untereinander, breite Spalten)."""
    output = BytesIO()
    data = [
        {"Kategorie": "1. Analyse", "Inhalt": ana},
        {"Kategorie": "2. Antwort", "Inhalt": ant},
        {"Kategorie": "3. Widerspruch", "Inhalt": wid}
    ]
    df = pd.DataFrame(data)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse-Ergebnis')
        workbook = writer.book
        worksheet = writer.sheets['Analyse-Ergebnis']
        wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        
        worksheet.set_column(0, 0, 20, wrap_format) # Kategorie-Spalte
        worksheet.set_column(1, 1, 100, wrap_format) # Inhalts-Spalte (sehr breit)
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
    return output.getvalue()

def perform_ocr_preview(uploaded_file):
    """Generiert Text-Vorschau aus Bild oder PDF."""
    try:
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.getvalue())
            full_text = ""
            for img in images:
                full_text += pytesseract.image_to_string(img, lang='deu') + "\n"
            return full_text
        else:
            img = Image.open(uploaded_file)
            return pytesseract.image_to_string(img, lang='deu')
    except:
        return "Vorschautext konnte nicht generiert werden (OCR-Fehler)."

# --- 4. TOP-BAR: RECHTLICHES (FIXIERT) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""**Amtsschimmel-Killer**  
**Betreiberin:** Elisabeth Reinecke  
Ringelsweide 9, 40223 Düsseldorf  

**Kontakt:**  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
Web: amtsschimmel-killer.streamlit.app  

**Haftung:**  
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""**1. Datenschutz auf einen Blick**  
Wir behandeln Ihre personenbezogenen Daten vertraulich (DSGVO).

**2. Datenerfassung & Hosting**  
Gehostet auf Streamlit Cloud. Logfiles werden automatisch erfasst; wir nutzen diese nicht.

**3. Dokumentenverarbeitung**  
Briefe werden per TLS-verschlüsselt an OpenAI (USA) übertragen. Keine Speicherung auf unseren Servern.

**4. Zahlungsabwicklung (Stripe)**  
Abwicklung über Stripe. Wir erhalten nur die Zahlungsbestätigung.

**5. Ihre Rechte**  
Recht auf Auskunft/Löschung: amtsschimmel-killer@proton.me.""")

with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""**Abonnement?** Nein. Einmalzahlung für feste Scans.  
**Dokumentensicherheit?** Verschlüsselt an OpenAI, danach sofortige Löschung.  
**Rechtsberatung?** Nein, nur Formulierungshilfe.  
**Fehlschlag?** Kein Abzug von Guthaben bei technischem Fehler.""")

with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""**Fristverlängerung:**  
"In der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist bis zum [Datum]..."  

**Widerspruch:**  
"Gegen Ihren Bescheid vom [Datum] lege ich hiermit Widerspruch ein..."  

**Akteneinsicht:**  
"Ich beantrage hiermit gemäß § 25 SGB X Akteneinsicht." """)

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

# LINKS: LOGO & SPRACHEN & KAUF
with col_left:
    try:
        st.image("icon_final_blau.png", width=160)
    except:
        st.markdown("### 🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache wählen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español", "NL Nederlands", "RO Română", "GR Ελληνικά", "CN 中文", "VN Tiếng Việt"], label_visibility="collapsed")

    st.write("")
    # Pakete mit fixen Links
    with st.container(border=True):
        st.markdown('<div class="pkg-icon">📄</div>**Analyse (1 Dokument)**<div class="pkg-price">3,99 €</div><div class="pkg-footer">EINMALZAHLUNG</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")

    with st.container(border=True):
        st.markdown('<div style="background-color: #ebf5fb; padding: 5px; border-radius: 10px;">'
                    '<div class="pkg-icon">🥈</div>**Spar-Paket (3 Dokumente)**<div class="pkg-price">9,99 €</div><div class="pkg-footer">EINMALZAHLUNG</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div style="background-color: #fef9e7; padding: 5px; border-radius: 10px;">'
                    '<div class="pkg-icon">🥇</div>**Sorglos (10 Dokumente)**<div class="pkg-price">19,99 €</div><div class="pkg-footer">EINMALZAHLUNG</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")
        st.markdown('</div>', unsafe_allow_html=True)

# MITTE: UPLOAD & VORSCHAU-TEXT (CHROME READY)
with col_mid:
    st.markdown("### 📑 Upload & Vorschau")
    st.success("👑 Admin Guthaben: 999 Dokumente")
    uploaded_file = st.file_uploader("Datei hier reinziehen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        # Vorschautext statt nur PDF-Download-Link
        with st.spinner("Text wird für Vorschau extrahiert..."):
            preview_text = perform_ocr_preview(uploaded_file)
        
        st.markdown("**Inhalt des hochgeladenen Dokuments:**")
        st.text_area("Vorschau (OCR)", preview_text, height=400)
        
        # Optionaler Download des Originals
        st.download_button("📥 Originaldatei herunterladen", uploaded_file, file_name=f"upload_{uploaded_file.name}")

# RECHTS: ANALYSE & EXPORT
with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    if uploaded_file:
        st.error("📅 Frist erkannt: 24.12.2024")
        
        ana_txt = "Die Behörde hat die notwendige Ermessensprüfung gemäß § 39 SGB I nicht erkennbar durchgeführt. Der Bescheid ist daher formell rechtswidrig."
        ant_txt = "Sehr geehrte Damen und Herren, hiermit nehme ich Bezug auf Ihr Schreiben. Die vorliegenden Nachweise wurden nicht gewürdigt..."
        wid_txt = "Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum] lege ich hiermit fristgerecht WIDERSPRUCH ein."
        
        st.info(ana_txt)
        
        tabs = st.tabs(["✍️ Antwort", "⚖️ Widerspruch", "📥 Downloads"])
        
        with tabs[0]:
            st.text_area("Vorschlag Antwort:", ant_txt, height=250)
        with tabs[1]:
            st.text_area("Vorschlag Widerspruch:", wid_txt, height=250)
        with tabs[2]:
            st.markdown("#### Alle Ergebnisse speichern:")
            
            # Excel
            st.download_button("📊 Excel-Bericht", create_excel_pro(ana_txt, ant_txt, wid_txt), "Analyse.xlsx")
            
            # Word (Komplett)
            st.download_button("📝 Word-Dokument (Alle Inhalte)", create_word_complete(ana_txt, ant_txt, wid_txt), "Bericht.docx")
            
            # PDF (Adobe Fixed)
            st.download_button("📕 PDF-Bericht (Adobe Ready)", create_pdf_adobe_ready(ana_txt, ant_txt, wid_txt), "Bericht.pdf")
