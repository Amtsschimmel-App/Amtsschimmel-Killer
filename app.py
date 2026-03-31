import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- 1. SETUP ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. DOWNLOAD-FUNKTIONEN (BYTES-FIX) ---
def create_excel_report(antwort, widerspruch, glossar):
    output = BytesIO()
    df = pd.DataFrame([{
        "Frist": "30.04.2026",
        "Glossar": glossar,
        "Antwortentwurf": antwort,
        "Widerspruchsentwurf": widerspruch
    }])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
    return output.getvalue()

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

# --- 3. CSS FÜR PAKET-BOXEN ---
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    .price-tag { font-size: 24px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 13px; color: #d32f2f; font-weight: bold; margin-bottom: 10px; }
    .st-button-link {
        display: inline-block; padding: 10px 15px; background-color: #1E3A8A !important; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 100%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. RECHTLICHE TOP-EXPANDER ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.write("**Amtsschimmel-Killer**\n\nBetreiberin: Elisabeth Reinecke\n\nRingelsweide 9, 40223 Düsseldorf\n\n+49 211 15821329\namtsschimmel-killer@proton.me")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.write("1. Vertraulichkeit gemäß DSGVO.\n2. Hosting Streamlit Cloud.\n3. TLS-Übertragung zu OpenAI.\n4. Stripe-Zahlung extern.\n5. Rechte: Auskunft/Löschung via E-Mail.")
with t3:
    with st.expander("❓ FAQ"):
        st.write("**Abo?** Nein, Einmalzahlung.\n**Sicher?** Ja, Dokumente werden nach Scan gelöscht.\n**Rechtsberatung?** Nein, nur Formulierungshilfe.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.caption("Fristverlängerung, Widerspruch, Akteneinsicht")

st.divider()

# --- 5. HAUPT-LAYOUT (3 SPALTEN) ---
col_pak, col_doc, col_eval = st.columns([1, 1.5, 1.5])

# LINKER BEREICH: PAKETE & SPRACHEN
with col_pak:
    try: st.image("logo.png", width=100)
    except: st.subheader("🏛️ Logo")
    
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"])
    
    p_conf = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "(1 Dokument)", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "(3 Dokumente)", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")
    ]
    for style, name, docs, price, link in p_conf:
        st.markdown(f'<div class="paket-container {style}"><div style="font-weight:bold; font-size:14px;">{name}</div><div style="font-size:12px;">{docs}</div><div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

# MITTLERER BEREICH: DOKUMENT
with col_doc:
    st.subheader("📄 Dokument")
    u_file = st.file_uploader("Datei hochladen (PDF, PNG, JPG)", type=["pdf", "png", "jpg"])
    if u_file:
        if u_file.type == "application/pdf":
            st.info("PDF hochgeladen.")
            st.download_button("📥 Original öffnen", u_file, file_name="original.pdf")
        else:
            st.image(u_file, use_container_width=True)

# RECHTER BEREICH: AUSWERTUNG & DOWNLOADS
with col_eval:
    st.subheader("🔍 Auswertung")
    if u_file:
        st.error("📅 **FRIST-CHECK: 30.04.2026**")
        
        with st.expander("📖 Glossar", expanded=True):
            st.write("Erklärung wichtiger Begriffe aus dem Brief...")
            
        with st.expander("📋 Antwort-Entwurf"):
            antw_txt = st.text_area("Bearbeitbar:", "Sehr geehrte Damen und Herren...", height=150, key="ta_antw")
            
        with st.expander("⚖️ Widerspruch"):
            wid_txt = st.text_area("Bearbeitbar:", "Gegen Ihren Bescheid...", height=150, key="ta_wid")

        st.markdown("### 📥 Download-Zentrum")
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📊 Excel", create_excel_report(antw_txt, wid_txt, "Glossar"), "analyse.xlsx", key="d_xl")
            st.download_button("📝 Word", create_docx(antw_txt), "brief.docx", key="d_doc")
        with c2:
            st.download_button("📕 PDF", create_pdf(wid_txt), "widerspruch.pdf", key="d_pdf")
            st.download_button("📅 iCal", create_ical(), "frist.ics", key="d_ics")
