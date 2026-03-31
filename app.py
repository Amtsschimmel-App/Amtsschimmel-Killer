import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document
import openai
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# OpenAI API Key aus den Secrets laden
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- 2. DOWNLOAD-LOGIK ---
def create_docx(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Entwurf', 0)
    for line in text.split('\n'):
        doc.add_paragraph(line)
    out = BytesIO()
    doc.save(out)
    return out.getvalue()

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return bytes(pdf.output(dest='S'))

def create_ical():
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nDTSTART:20260430T080000Z\nDTEND:20260430T090000Z\nSUMMARY:Fristende Amtsschimmel-Killer\nDESCRIPTION:Widerspruch einlegen!\nEND:VEVENT\nEND:VCALENDAR"
    return ics.encode('utf-8')

# --- 3. CSS (PAKETE & STRIPE) ---
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; background-color: #f0f7ff; }
    .green-box { border-color: #28a745; background-color: #f1f9f1; }
    .gold-box { border-color: #fcc419; background-color: #fffdf5; }
    .header-text { font-size: 16px; font-weight: bold; margin-bottom: 10px; display: block; color: #333; }
    .price-tag { font-size: 28px; font-weight: bold; color: #1E3A8A; margin: 15px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link {
        display: inline-block; padding: 12px 20px; background-color: #1E3A8A !important; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 95%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. RECHTSTEXTE (EXAKTE 1:1 ÜBERNAHME) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\n\nBetreiberin:\nElisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.\n\n4. Zahlungsabwicklung (Stripe)\nBei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.\n\n5. Ihre Rechte\nSie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.\n\nWie sicher sind meine Dokumente?\nIhre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.\n\nErsetzt die App eine Rechtsberatung?\nNein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.\n\nWas passiert, wenn der Scan fehlschlägt?\nEin Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.\n\nWie erreiche ich Elisabeth Reinecke?\nNutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]\n\nWiderspruch einlegen (Fristwahrend)\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]\n\nAkteneinsicht einfordern:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_pak, col_main = st.columns([1.2, 3.2])

with col_pak:
    try: st.image("icon_final_blau.png", width=120)
    except: st.subheader("🏛️ Amtsschimmel-Killer")
    
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], key="lang")
    st.write("---")
    
    p_conf = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "(1 Dokument)", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "(3 Dokumente)", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://stripe.com")
    ]
    for style, name, docs, price, link in p_conf:
        st.markdown(f'''
        <div class="paket-container {style}">
            <span class="header-text">{name}</span>
            <span>{docs}</span>
            <div class="price-tag">{price} €</div>
            <div class="no-abo">Einmalzahlung kein Abo</div>
            <a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a>
        </div>''', unsafe_allow_html=True)

with col_main:
    c_preview, c_res = st.columns([1.8, 1.4])
    
    with c_preview:
        st.subheader("📄 Dokument")
        u_file = st.file_uploader("Datei hier ablegen", type=["pdf", "jpg", "png", "jpeg"])
        if u_file:
            if u_file.type == "application/pdf":
                st.info("PDF geladen.")
                st.download_button("📥 Original PDF öffnen", u_file, file_name="upload.pdf")
            else: st.image(u_file, use_container_width=True)

    with c_res:
        st.subheader("🔍 Auswertung")
        if u_file:
            if st.button("Jetzt Dokument killen"):
                with st.spinner('KI analysiert den Amtsschimmel...'):
                    u_file.seek(0)
                    base64_image = base64.b64encode(u_file.read()).decode('utf-8')
                    
                    try:
                        # --- OPENAI AUFRUF (SYNTAX DEFINITIV KORRIGIERT) ---
                        msg_system = "Du bist der Amtsschimmel-Killer. Analysiere den Brief. Behalte Platzhalter [VORNAME NACHNAME] etc. strikt bei."
                        msg_user = [
                            {"type": "text", "text": "Analysiere diesen Brief. Extrahiere die Frist, erstelle ein Glossar und schreibe einen Antwortentwurf sowie einen Widerspruch."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                        
                        response = openai.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": msg_system},
                                {"role": "user", "content": msg_user}
                            ]
                        )
                        st.session_state.resultat_ki = response.choices.message.content
                    except Exception as e:
                        st.error(f"Fehler bei der Analyse: {e}")

            if 'resultat_ki' in st.session_state:
                st.error("📅 **FRIST-CHECK: ANALYSIERT**")
                with st.expander("📖 Glossar & Analyse", expanded=True):
                    st.write(st.session_state.resultat_ki)
                
                st.write("---")
                st.subheader("📥 Downloads & Kalender")
                st.download_button("📂 Als PDF (Entwurf)", create_pdf(st.session_state.resultat_ki), "Antwort_Amtsschimmel.pdf")
                st.download_button("📂 Als DOCX (Entwurf)", create_docx(st.session_state.resultat_ki), "Antwort_Amtsschimmel.docx")
                st.download_button("📅 Termin (iCal)", create_ical(), "Frist_Erinnerung.ics")
