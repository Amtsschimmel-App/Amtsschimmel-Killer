import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from fpdf import FPDF
from docx import Document
from pdf2image import convert_from_bytes
import pdfplumber

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (BOXEN, BUTTONS INNEN & LAYOUT) ---
st.markdown("""
<style>
    /* Paket-Boxen Styling */
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 2px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    
    .header-text { font-size: 18px; font-weight: bold; margin-bottom: 10px; display: block; }
    .price-tag { font-size: 24px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }

    /* Button-Styling zwingend innerhalb der Box */
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; }
    
    .auswertung-box { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# --- 3. DOWNLOAD-FUNKTIONEN ---
def create_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 100) # Spaltenbreite für viel Text
    return output.getvalue()

def create_word(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Antwortentwurf', 0)
    doc.add_paragraph(text)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_pdf_report(data):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    for k, v in data.items(): pdf.multi_cell(0, 10, f"{k}: {v}\n")
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. TOP-BAR: RECHTLICHES (EXAKTE TEXTE & ABSTÄNDE) ---
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

# --- 5. HAUPT-LAYOUT (PAKETE LINKS | VORSCHAU | AUSWERTUNG) ---
col_l, col_m, col_r = st.columns([1.2, 1.8, 1.4])

with col_l:
    st.image("icon_final_blau.png", width=140) if "icon" else st.markdown("🏛️ **Amtsschimmel-Killer**")
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], label_visibility="collapsed")
    st.write("---")
    st.markdown("### 📦 Pakete")
    
    # Pakete mit Kaufbuttons INNERHALB der Boxen
    for box_style, name, docs, price, link in [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "1 Dokument", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "3 Dokumente", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "10 Dokumente", "19,99", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")
    ]:
        st.markdown(f'<div class="paket-container {box_style}"><span class="header-text">{name}</span>({docs})<div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", link)
        st.markdown('</div>', unsafe_allow_html=True)

with col_m:
    st.subheader("📄 Dokument & Vorschau")
    uploaded_file = st.file_uploader("Upload", type=["pdf", "jpg", "png"], label_visibility="collapsed")
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            try:
                images = convert_from_bytes(uploaded_file.getvalue())
                for img in images: st.image(img, use_container_width=True)
            except: st.error("PDF-Vorschau lädt... (Stellen Sie sicher, dass Poppler installiert ist)")
        else: st.image(uploaded_file, use_container_width=True)
    else: st.info("Warten auf Upload...")

with col_r:
    st.subheader("🔍 Auswertung")
    if uploaded_file:
        # --- DATEN-STRUKTUR ---
        res = {
            "Frist": "30.04.2026",
            "Glossar": "Rechtsbehelfsbelehrung: Erklärt den Widerspruchsweg.\nVerwaltungsakt: Amtliche Entscheidung.\nErmessen: Handlungsspielraum der Behörde.",
            "Antwort": "Sehr geehrte Damen und Herren,\n\nin der Angelegenheit [Aktenzeichen] beziehe ich mich auf Ihr Schreiben...\n\n[PLATZHALTER: Vorname Nachname, Straße Hausnummer, PLZ Ort, Datum]",
            "Widerspruch": "Gegen den Bescheid vom [Datum] lege ich hiermit Widerspruch ein...\n\n[PLATZHALTER: Aktenzeichen, Name, Unterschrift]"
        }
        
        # Säuberliche Trennung der Blöcke
        st.error(f"📅 **FRIST-CHECK:** {res['Frist']}")
        
        st.markdown('<div class="auswertung-box"><b>📚 AUSFÜHRLICHES GLOSSAR:</b><br>' + res['Glossar'].replace('\n', '<br>') + '</div>', unsafe_allow_html=True)
        
        with st.expander("✍️ Antwortschreiben (Lang)", expanded=False):
            st.text_area("Vorschau Antwort:", res['Antwort'], height=300, key="key_antwort_schreiben")
            
        with st.expander("⚖️ Widerspruchsschreiben (Lang)", expanded=False):
            st.text_area("Vorschau Widerspruch:", res['Widerspruch'], height=300, key="key_widerspruch_schreiben")
            
        st.write("---")
        st.subheader("💾 Downloads")
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("📊 Excel-Analyse", create_excel(res), "Analyse.xlsx")
            st.download_button("📄 PDF-Bericht", create_pdf_report(res), "Bericht.pdf")
        with d2:
            st.download_button("📝 Word-Antwort", create_word(res['Antwort']), "Antwort.docx")
            st.button("📅 Termin (Kalender.ico)")
    else: st.write("Dokument hochladen.")
