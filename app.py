import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- 1. SETUP ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. DOWNLOAD-FUNKTIONEN (BYTES-KAPSELUNG) ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return bytes(pdf.output(dest='S'))

def create_docx(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Entwurf', 0)
    for line in text.split('\n'): doc.add_paragraph(line)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_excel(glossar, antwort):
    out = BytesIO()
    df = pd.DataFrame([{"Bereich": "Glossar", "Inhalt": glossar}, {"Bereich": "Antwort", "Inhalt": antwort}])
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer: df.to_excel(writer, index=False)
    return out.getvalue()

def create_ical():
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:Fristende Amtsschimmel-Killer\nDTSTART:20260430T090000Z\nEND:20260430T100000Z\nEND:VEVENT\nEND:VCALENDAR"
    return ics.encode('utf-8')

# --- 3. CSS FÜR PAKETE & DESIGN ---
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
</style>
""", unsafe_allow_html=True)

# --- 4. RECHTSTEXTE (EXAKTE ÜBERNAHME) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""**Amtsschimmel-Killer**  
**Betreiberin:** Elisabeth Reinecke  
Ringelsweide 9, 40223 Düsseldorf  
**Kontakt:** Telefon: +49 211 15821329 | E-Mail: amtsschimmel-killer@proton.me  
**Web:** amtsschimmel-killer.streamlit.app  
**Haftung:** Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""**1. Datenschutz auf einen Blick**  
Wir behandeln Ihre personenbezogenen Daten vertraulich (DSGVO).  
**2. Datenerfassung & Hosting**  
Streamlit Cloud erfasst Logfiles (IP, Browser). Wir nutzen diese nicht.  
**3. Dokumentenverarbeitung**  
Briefe werden per TLS an OpenAI (USA) übertragen. Keine Speicherung auf unseren Servern.  
**4. Zahlungsabwicklung (Stripe)**  
Stripe erhebt Daten zur Abrechnung. Wir erhalten nur die Bestätigung.  
**5. Ihre Rechte**  
Auskunft/Löschung via amtsschimmel-killer@proton.me.""")
with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""**Ist das ein Abonnement?**  
Nein. Jede Zahlung ist eine Einmalzahlung. Keine automatische Verlängerung.  
**Wie sicher sind meine Dokumente?**  
Verschlüsselt an OpenAI, keine dauerhafte Speicherung.  
**Ersetzt die App eine Rechtsberatung?**  
Nein. Nur Formulierungshilfe.  
**Was passiert, wenn der Scan fehlschlägt?**  
Kein Guthabenabzug bei technischem Scheitern.""")
with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""**Fristverlängerung:** Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum]...  
**Widerspruch:** Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum] lege ich hiermit Widerspruch ein...  
**Akteneinsicht:** ...beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht.""")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_sidebar, col_doc, col_eval = st.columns([1, 1.5, 1.5])

with col_sidebar:
    st.image("https://githubusercontent.com", width=150)
    st.selectbox("Sprache / Language", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"])
    
    # Pakete mit Icons, exakten Namen & Stripe-Links
    st.markdown(f'<div class="paket-container blue-box">🛡️ <b>Amtsschimmel-Killer Analyse</b><br>(1 Dokument)<div class="price-tag">3,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="paket-container green-box">⚔️ <b>Amtsschimmel-Killer Spar-Paket</b><br>(3 Dokumente)<div class="price-tag">9,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="https://buy.stripe.com/8x228retRbj50paalq1gs03" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="paket-container gold-box">🚀 <b>Amtsschimmel-Killer Sorglos-Paket</b><br>(10 Dokumente)<div class="price-tag">19,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="https://buy.stripe.com/28EcN50D1bj52xi8di1gs041" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_doc:
    st.subheader("📄 Dokument")
    u_file = st.file_uploader("Datei hier ablegen", type=["pdf", "jpg", "png"], key="main_u")
    if u_file:
        if u_file.type == "application/pdf":
            st.info("PDF geladen.")
            st.download_button("📥 Original PDF öffnen", u_file, file_name="upload.pdf", key="pdf_dl")
        else: st.image(u_file, use_container_width=True)

with col_eval:
    st.subheader("🔍 Auswertung")
    if u_file:
        st.error("📅 **FRIST-CHECK: 30.04.2026**")
        glo = "Glossar-Inhalt..."; ant = "Brief-Entwurf..."
        with st.expander("📖 Glossar", expanded=True): st.text_area("Erklärung", glo, key="ta_glo")
        with st.expander("📋 Antwort-Entwurf"): st.text_area("Entwurf", ant, height=200, key="ta_ant")
        
        st.markdown("### 📥 Downloads & Kalender")
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("📊 Excel", create_excel(glo, ant), "analyse.xlsx", key="dl_xl")
            st.download_button("📝 Word", create_docx(ant), "brief.docx", key="dl_word")
        with d2:
            st.download_button("📕 PDF", create_pdf(ant), "widerspruch.pdf", key="dl_pdf")
            st.download_button("📅 Termin", create_ical(), "frist.ics", key="dl_ical")
