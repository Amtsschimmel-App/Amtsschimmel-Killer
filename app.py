import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- 1. SETUP & BRANDING ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# CSS für das exakte Layout (Boxen, Farben, Stripe-Buttons)
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    .price-tag { font-size: 28px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link {
        display: inline-block; padding: 12px 20px; background-color: #1E3A8A !important; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 100%; text-align: center;
    }
    [data-testid="column"] { padding: 0 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DOWNLOAD-HELPER (EXCEL MIT SPALTEN-FIX & BYTES) ---
def create_excel_report(frist, glossar, antwort, widerspruch):
    output = BytesIO()
    df = pd.DataFrame([{
        "Fristende": frist,
        "Glossar / Begriffe": glossar,
        "Antwortschreiben (Entwurf)": antwort,
        "Widerspruchsschreiben (Entwurf)": widerspruch
    }])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse-Bericht')
        worksheet = writer.sheets['Analyse-Bericht']
        # Automatische Spaltenanpassung (Breite 80)
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 80)
    return output.getvalue()

def create_pdf_bytes(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return bytes(pdf.output(dest='S'))

def create_docx_bytes(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Entwurf', 0)
    for line in text.split('\n'): doc.add_paragraph(line)
    out = BytesIO(); doc.save(out); return out.getvalue()

# --- 3. RECHTSTEXTE (EXAKT NACH GRUNDANWEISUNG) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""Amtsschimmel-Killer\n\nBetreiberin:\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.\n\n4. Zahlungsabwicklung (Stripe)\nBei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.\n\n5. Ihre Rechte\nSie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.""")
with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""Ist das ein Abonnement?\nNein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.\n\nWie sicher sind meine Dokumente?\nIhre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.\n\nErsetzt die App eine Rechtsberatung?\nNein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.\n\nWas passiert, wenn der Scan fehlschlägt?\nEin Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.\n\nWie erreiche ich Elisabeth Reinecke?\nNutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.""")
with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]\n\nWiderspruch einlegen (Fristwahrend)\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]\n\nAkteneinsicht einfordern:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]""")

st.divider()

# --- 4. 3-SPALTEN LAYOUT (NACH SCREENSHOT) ---
col_sidebar, col_doc, col_eval = st.columns([1, 1.5, 1.5])

with col_sidebar:
    st.subheader("🏛️ Amtsschimmel-Killer")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], key="lang")
    
    # Pakete mit Icons & Stripe-Links
    p_data = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "(1 Dokument)", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "(3 Dokumente)", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")
    ]
    for style, name, docs, price, link in p_data:
        st.markdown(f'<div class="paket-container {style}"><span style="font-weight:bold">{name}</span><br>{docs}<div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_doc:
    st.subheader("📄 Dokument")
    u_file = st.file_uploader("Datei hier ablegen", type=["pdf", "png", "jpg"], key="uploader")
    if u_file:
        if u_file.type == "application/pdf":
            st.info("PDF geladen.")
            st.download_button("📥 Original PDF öffnen", u_file, file_name="upload.pdf", key="dl_orig")
        else: st.image(u_file, use_container_width=True)

with col_eval:
    st.subheader("🔍 Auswertung")
    if u_file:
        st.error("📅 **FRIST-CHECK: 30.04.2026**")
        
        # Platzhalter-Texte wie gewünscht
        glo_val = "Rechtsbehelfsbelehrung: Erklärt den Weg des Widerspruchs.\nVerwaltungsakt: Behördliche Entscheidung.\nErmessen: Handlungsspielraum der Behörde."
        ant_val = "[VORNAME NACHNAME]\n[STRASSE]\n[PLZ ORT]\n\nAn: [BEHÖRDE]\n\nSehr geehrte Damen und Herren,\nbezüglich Ihres Schreibens..."
        wid_val = "Sehr geehrte Damen und Herren,\ngegen den Bescheid vom [DATUM] lege ich hiermit WIDERSPRUCH ein.\nBegründung folgt."

        with st.expander("📖 Glossar", expanded=True):
            glo_txt = st.text_area("Fachbegriffe", glo_val, height=100, key="ta_glo")
        with st.expander("📋 Antwort-Entwurf"):
            ant_txt = st.text_area("Dein Brief", ant_val, height=150, key="ta_ant")
        with st.expander("⚖️ Widerspruch"):
            wid_txt = st.text_area("Formulierungshilfe", wid_val, height=150, key="ta_wid")

        st.markdown("### 📥 Download-Zentrum (2x2)")
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("📊 Excel (Komplett)", create_excel_report("30.04.2026", glo_txt, ant_txt, wid_txt), "analyse.xlsx", key="dl_xl")
            st.download_button("📝 Word (Briefe)", create_docx_bytes(ant_txt), "briefe.docx", key="dl_doc")
        with d2:
            st.download_button("📕 PDF (Widerspruch)", create_pdf_bytes(wid_txt), "widerspruch.pdf", key="dl_pdf")
            st.download_button("📅 Termin (iCal)", b"Dummy", "frist.ics", key="dl_ical")
