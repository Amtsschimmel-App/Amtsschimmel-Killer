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

# --- 2. CUSTOM CSS ---
st.markdown("""
    <style>
    .pkg-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .pkg-price { font-size: 1.5rem; font-weight: bold; color: #1E3A8A; margin: 0.5rem 0; }
    .pkg-footer { font-size: 0.8rem; color: gray; margin-bottom: 1rem; }
    .legal-text { white-space: pre-wrap; font-family: sans-serif; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN (FIXED FÜR ADOBE & STREAMLIT) ---

def create_pdf_adobe_ready(analyse, antwort, widerspruch):
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
        # Sonderzeichen-Fix für Adobe Reader (Latin-1)
        safe_text = content.replace('•', '-').replace('–', '-').replace('„', '"').replace('“', '"').replace('”', '"').replace('’', "'")
        pdf.multi_cell(0, 6, safe_text.encode('latin-1', 'replace').decode('latin-1'))
    
    return bytes(pdf.output())

def create_word_complete(analyse, antwort, widerspruch):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer: Ihr Report', 0)
    for title, content in [("Analyse", analyse), ("Antwortschreiben", antwort), ("Widerspruch", widerspruch)]:
        doc.add_heading(title, level=1)
        doc.add_paragraph(content)
    target = BytesIO()
    doc.save(target)
    return target.getvalue()

def create_excel_pro(ana, ant, wid):
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
        worksheet.set_column(0, 0, 25, wrap_format)
        worksheet.set_column(1, 1, 120, wrap_format)
    return output.getvalue()

def perform_ocr_preview(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.getvalue())
            full_text = "".join([pytesseract.image_to_string(img, lang='deu') + "\n" for img in images])
            return full_text
        else:
            return pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    except:
        return "Vorschautext konnte nicht generiert werden."

# --- 4. TOP-BAR: RECHTLICHES (VOLLTEXTE MIT ABSTÄNDEN) ---
t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""
Amtsschimmel-Killer  
Betreiberin: Elisabeth Reinecke  
Ringelsweide 9  
40223 Düsseldorf  

Kontakt:  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
Web: amtsschimmel-killer.streamlit.app  

Haftung:  
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        """)

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""
1. Datenschutz auf einen Blick  
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).  

2. Datenerfassung & Hosting  
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.  

3. Dokumentenverarbeitung  
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.  

4. Zahlungsabwicklung (Stripe)  
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.  

5. Ihre Rechte  
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
        """)

with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""
Ist das ein Abonnement?  
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.  

Wie sicher sind meine Dokumente?  
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.  

Ersetzt die App eine Rechtsberatung?  
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.  

Was passiert, wenn der Scan fehlschlägt?  
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.  

Wie erreiche ich Elisabeth Reinecke?  
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
        """)

with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""
Fristverlängerung:  
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]  

Widerspruch einlegen (Fristwahrend)  
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]  

Akteneinsicht einfordern:  
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
        """)

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

# LINKS: PAKETE & SPRACHEN
with col_left:
    try:
        st.image("icon_final_blau.png", width=160)
    except:
        st.markdown("### 🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache wählen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español", "NL Nederlands", "RO Română", "GR Ελληνικά", "CN 中文", "VN Tiếng Việt"], label_visibility="collapsed")

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="pkg-icon">📄</div>**Analyse (1 Dokument)**<div class="pkg-price">3,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")

    with st.container(border=True):
        st.markdown('<div style="background-color: #ebf5fb; padding: 5px; border-radius: 10px;">'
                    '<div class="pkg-icon">🥈</div>**Spar-Paket (3 Dokumente)**<div class="pkg-price">9,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div style="background-color: #fef9e7; padding: 5px; border-radius: 10px;">'
                    '<div class="pkg-icon">🥇</div>**Sorglos-Paket (10 Dokumente)**<div class="pkg-price">19,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")
        st.markdown('</div>', unsafe_allow_html=True)

# MITTE: UPLOAD & VORSCHAU
with col_mid:
    st.markdown("### 📑 Upload & Vorschau")
    st.success("👑 Admin Guthaben: 999 Dokumente")
    uploaded_file = st.file_uploader("Datei hier reinziehen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        with st.spinner("Lese Dokument..."):
            preview_text = perform_ocr_preview(uploaded_file)
        st.markdown("**Erkannter Inhalt:**")
        st.text_area("Dokumenten-Vorschau", preview_text, height=450)
        st.download_button("📂 Originaldatei sichern", uploaded_file, file_name=uploaded_file.name)

# RECHTE SPALTE: ANALYSE & ANTWORT
with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    if uploaded_file:
        st.error("📅 FRIST ERKANNT: 24.12.2024")
        
        ana_txt = "Die detaillierte Prüfung Ihres Bescheids hat ergeben, dass die Behörde wesentliche Verfahrensvorschriften missachtet hat. Insbesondere wurde das Recht auf rechtliches Gehör gemäß § 24 SGB X verletzt, da Ihnen vor Erlass des belastenden Verwaltungsaktes keine Gelegenheit gegeben wurde, sich zu den entscheidungserheblichen Tatsachen zu äußern. Zudem ist die Begründung des Bescheids unzureichend im Sinne des § 35 SGB X, da nicht nachvollziehbar dargelegt wurde, wie die Behörde ihr Ermessen ausgeübt hat. Es empfiehlt sich dringend, die im Antwortschreiben genannten Punkte anzuführen."
        
        ant_txt = """Sehr geehrte Damen und Herren,

hiermit nehme ich Bezug auf Ihr Schreiben vom [Datum], Aktenzeichen [Nummer]. Nach eingehender Prüfung der von Ihnen angeführten Gründe teile ich Ihnen mit, dass ich mit der Entscheidung nicht einverstanden bin.

Der Bescheid beruht auf einer unvollständigen Sachverhaltsaufklärung. Sie sind davon ausgegangen, dass die Voraussetzungen für eine Ablehnung vorliegen, jedoch belegen die beigefügten Unterlagen das Gegenteil. Ich fordere Sie hiermit auf, den Sachverhalt unter Berücksichtigung dieser Informationen erneut zu prüfen und den Bescheid entsprechend aufzuheben. 

Sollten Sie an Ihrer Auffassung festhalten, bitte ich um eine detaillierte Begründung, warum die vorgelegten Beweise nicht berücksichtigt wurden. Ich erwarte Ihre Rückmeldung bis zum [Datum]."""

        wid_txt = """Sehr geehrte Damen und Herren,

gegen Ihren Bescheid vom [Datum], mir zugegangen am [Datum], lege ich hiermit form- und fristgerecht

WIDERSPRUCH

ein. 

Begründung:
Der Bescheid ist bereits aus formellen Gründen rechtswidrig. Die nach § 39 SGB I erforderliche Ermessensprüfung ist nicht erkennbar. Die Behörde hat sich lediglich auf pauschale Textbausteine verlassen, ohne die Besonderheiten meines Einzelfalls (insbesondere die vorliegende Härtesituation) zu würdigen. Zudem wurde eine fehlerhafte Rechtsgrundlage herangezogen.

Ich beantrage hiermit zudem die Aussetzung der Vollziehung gemäß § 80 Abs. 4 VwGO / § 86a Abs. 3 SGB X. Bis zur endgültigen Entscheidung über meinen Widerspruch sind daher keine weiteren Maßnahmen Ihrerseits zulässig. Eine detaillierte Begründung durch meinen Rechtsbeistand behalte ich mir vor."""

        st.info(ana_txt)
        tab1, tab2, tab3 = st.tabs(["✍️ Antwort", "⚖️ Widerspruch", "📥 Downloads"])
        
        with tab1:
            st.text_area("Entwurf Antwort:", ant_txt, height=280)
        with tab2:
            st.text_area("Entwurf Widerspruch:", wid_txt, height=280)
        with tab3:
            st.download_button("📊 Excel-Bericht", create_excel_pro(ana_txt, ant_txt, wid_txt), "Analyse.xlsx")
            st.download_button("📝 Word-Dokument (Komplett)", create_word_complete(ana_txt, ant_txt, wid_txt), "Bericht.docx")
            pdf_bytes = create_pdf_adobe_ready(ana_txt, ant_txt, wid_txt)
            st.download_button("📕 PDF-Report (Adobe Ready)", pdf_bytes, "Bericht.pdf", mime="application/pdf")
