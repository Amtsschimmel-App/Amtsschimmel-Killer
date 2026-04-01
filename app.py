import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- 1. SETUP & LOGO ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. DOWNLOAD-LOGIK ---
def create_docx(text):
    doc = Document(); doc.add_heading('Amtsschimmel-Killer Entwurf', 0)
    for line in text.split('\n'): doc.add_paragraph(line)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return bytes(pdf.output(dest='S'))

def create_ical():
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nDTSTART:20260430T080000Z\nDTEND:20260430T090000Z\nSUMMARY:Fristende Amtsschimmel-Killer\nDESCRIPTION:Widerspruch einlegen!\nEND:VEVENT\nEND:VCALENDAR"
    return ics.encode('utf-8')

# --- 3. CSS (PAKETE & BUTTONS) ---
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    .price-tag { font-size: 28px; font-weight: bold; color: #1E3A8A; margin: 15px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link {
        display: inline-block; padding: 12px 20px; background-color: #1E3A8A !important; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 90%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. EXAKTE TEXTE (IMPRESSUM, DATENSCHUTZ, FAQ, VORLAGEN) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""Amtsschimmel-Killer<br><br>Betreiberin:<br><br>Elisabeth Reinecke<br><br>Ringelsweide 9<br>40223 Düsseldorf<br><br>Kontakt:<br>Telefon: +49 211 15821329<br>E-Mail: amtsschimmel-killer@proton.me<br>Web: amtsschimmel-killer.streamlit.app<br><br>Haftung:<br>Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""", unsafe_allow_html=True)
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""1. Datenschutz auf einen Blick<br>Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).<br><br>2. Datenerfassung & Hosting<br>Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.<br><br>3. Dokumentenverarbeitung<br>Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.<br><br>4. Zahlungsabwicklung (Stripe)<br>Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.<br><br>5. Ihre Rechte<br>Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.""", unsafe_allow_html=True)
with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""Ist das ein Abonnement?<br>Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.<br><br>Wie sicher sind meine Dokumente?<br>Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.<br><br>Ersetzt die App eine Rechtsberatung?<br>Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.<br><br>Was passiert, wenn der Scan fehlschlägt?<br>Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.<br><br>Wie erreiche ich Elisabeth Reinecke?<br>Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.""", unsafe_allow_html=True)
with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""Fristverlängerung:<br>Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]<br><br>Widerspruch einlegen (Fristwahrend)<br>Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]<br><br>Akteneinsicht einfordern:<br>Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]""", unsafe_allow_html=True)

st.divider()

# --- 5. HAUPT-LAYOUT (3 SPALTEN WIE AUF BILD) ---
col_pak, col_upload, col_result = st.columns([1.2, 1.8, 1.4])

with col_pak:
    st.subheader("🏛️ Amtsschimmel-Killer")
    st.selectbox("Sämtliche Sprachen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], key="lang")
    st.write("---")
    
    # Pakete strikt nach Grundanweisung
    p_conf = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "(1 Dokument)", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "(3 Dokumente)", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://stripe.com")
    ]
    for style, name, docs, price, link in p_conf:
        st.markdown(f'<div class="paket-container {style}"><span style="font-weight:bold">{name}</span><br>{docs}<div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_upload:
    st.subheader("📄 Dokument")
    u_file = st.file_uploader("Datei hier ablegen", type=["pdf", "jpg", "png"])
    if u_file:
        if u_file.type == "application/pdf": st.info("PDF geladen.")
        else: st.image(u_file, use_container_width=True)

with col_result:
    st.subheader("🔍 Auswertung")
    if u_file:
        st.error("📅 **FRIST-CHECK: 30.04.2026**")
        with st.expander("📖 Glossar", expanded=True):
            st.text("Verwaltungsakt: Amtliche Entscheidung.\nErmessen: Handlungsspielraum.")
        
        beispiel_text = "Analyse für Elisabeth Reinecke..."
        st.write("---")
        st.download_button("📄 PDF Export", create_pdf(beispiel_text), "Analyse.pdf", use_container_width=True)
        st.download_button("📅 Termin (iCal)", create_ical(), "Frist.ics", use_container_width=True)
    else:
        st.info("Bitte Dokument hochladen.")

if __name__ == "__main__":
    main()
