import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document
import re

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# CSS für bunte Boxen, Stripe-Buttons und Abstände
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; background-color: #f0f7ff; }
    .green-box { border-color: #28a745; background-color: #f6fff0; }
    .gold-box { border-color: #fcc419; background-color: #fffbf0; }
    .price-tag { font-size: 28px; font-weight: bold; color: #1E3A8A; margin: 15px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link {
        display: inline-block; padding: 12px 20px; background-color: #1E3A8A !important; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 95%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DOWNLOAD-FUNKTIONEN (DOCX, EXCEL, PDF) ---
def create_docx(antwort, widerspruch, glossar):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer: Komplette Analyse', 0)
    doc.add_heading('Glossar', level=1); doc.add_paragraph(glossar)
    doc.add_heading('Antwortentwurf', level=1); doc.add_paragraph(antwort)
    doc.add_heading('Widerspruchsentwurf', level=1); doc.add_paragraph(widerspruch)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_excel_report(antwort, widerspruch, glossar, frist):
    output = BytesIO()
    df = pd.DataFrame([{
        "KRITISCHE FRIST": frist,
        "ERKLÄRTES GLOSSAR": glossar,
        "ANTWORTENTWURF": antwort,
        "WIDERSPRUCHS-ENTWURF": widerspruch
    }])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 100) # Spaltenbreite fixiert
    return output.getvalue()

def create_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return bytes(pdf.output(dest='S'))

# --- 3. RECHTSTEXTE (1:1 MIT EXAKTEN ABSTÄNDEN) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\n\nBetreiberin:\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
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

# --- 4. HAUPT-LAYOUT (3 SPALTEN) ---
col_pak, col_upload, col_result = st.columns([1.2, 1.8, 1.4])

with col_pak:
    st.subheader("🏛️ Amtsschimmel-Killer")
    st.selectbox("Sämtliche Sprachen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], key="lang")
    st.write("---")
    p_conf = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse (1 Dokument)", "", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket (3 Dokumente)", "", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket (10 Dokumente)", "", "19,99", "https://stripe.com")
    ]
    for style, name, docs, price, link in p_conf:
        st.markdown(f'<div class="paket-container {style}"><span style="font-weight:bold">{name}</span><div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_upload:
    st.subheader("📄 Dokument")
    u_file = st.file_uploader("Datei hier ablegen (PDF, JPG, PNG)", type=["pdf", "jpg", "png", "jpeg"])
    # Simuliertes Auslesen für Fristerkennung (2026 Logik)
    demo_text = "Fristende am 25.05.2026." 

with col_result:
    st.subheader("🔍 Auswertung")
    if u_file:
        # FRISTERKENNUNG
        found_date = re.search(r'(\d{2}\.\d{2}\.2026)', demo_text)
        detected_frist = found_date.group(1) if found_date else "Prüfung läuft..."
        st.error(f"🚨 **KRITISCHE FRIST ERKANNT: {detected_frist}**")
        
        # VOLLSTÄNDIGE TEXTE
        glossar_txt = "Verwaltungsakt: Amtliche Entscheidung einer Behörde.\nErmessen: Handlungsspielraum der Behörde.\nRechtsbehelfsbelehrung: Hinweis am Ende des Briefes über Widerspruchsmöglichkeiten."
        antwort_txt = "Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nAn die Behörde...\n\nBetreff: Rückfragen zum Bescheid\n\nSehr geehrte Damen und Herren,\nich beziehe mich auf Ihr Schreiben und habe dazu einige Rückfragen zur Berechnungsgrundlage. Bitte erläutern Sie mir diese gemäß den gesetzlichen Vorgaben. Da die Frist am " + detected_frist + " abläuft, bitte ich um zeitnahe Antwort.\n\nMit freundlichen Grüßen,\nElisabeth Reinecke"
        widerspruch_txt = "Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nWIDERSPRUCH\n\nSehr geehrte Damen und Herren,\nhiermit lege ich gegen Ihren Bescheid form- und fristgerecht WIDERSPRUCH ein. Die Begründung folgt in einem separaten Schreiben nach erfolgter Akteneinsicht.\n\nMit freundlichen Grüßen,\nElisabeth Reinecke"

        with st.expander("📖 Glossar", expanded=True): st.text(glossar_txt)
        with st.expander("✉️ Antwortentwurf"): st.text(antwort_txt)
        with st.expander("⚔️ Widerspruch"): st.text(widerspruch_txt)
        
        st.divider()
        st.subheader("📥 Downloads")
        st.download_button("📊 Excel Analyse (Komplett)", create_excel_report(antwort_txt, widerspruch_txt, glossar_txt, detected_frist), "Analyse.xlsx", use_container_width=True)
        st.download_button("📝 Word Export", create_docx(antwort_txt, widerspruch_txt, glossar_txt), "Analyse_Komplett.docx", use_container_width=True)
        st.download_button("📄 PDF Export", create_pdf(antwort_txt), "Antwortentwurf.pdf", use_container_width=True)
    else:
        st.info("Bitte Dokument hochladen.")

if st.query_params.get("admin") == "GeheimAmt2024!":
    st.sidebar.success("🔑 Admin-Modus Aktiv")
