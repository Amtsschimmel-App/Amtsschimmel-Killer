import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- 1. SETUP ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. DOWNLOAD-LOGIK (MAXIMALE STABILITÄT) ---
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
    # Sonderzeichen-Fix für latin-1
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

# --- 4. RECHTSTEXTE (OBEN ZUSAMMENGEKLAPPT) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\n\nBetreiberin:\nElisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\n+49 211 15821329\namtsschimmel-killer@proton.me")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. DSGVO konform.\n2. Hosting: Streamlit Cloud.\n3. Keine Speicherung von Briefen.\n4. TLS-Verschlüsselung zu OpenAI.\n5. Stripe für Zahlungen.")
with t3:
    with st.expander("❓ FAQ"):
        st.text("Kein Abo! Einmalzahlung.\nSichere Dokumentenverarbeitung.\nKeine Rechtsberatung.\nSupport: amtsschimmel-killer@proton.me")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung\nWiderspruch\nAkteneinsicht")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_pak, col_main = st.columns([1.2, 3.2])

with col_pak:
    st.subheader("🏛️ Amtsschimmel-Killer")
    st.selectbox("Sämtliche Sprachen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "AR العربية"], key="lang")
    st.write("---")
    
    # Pakete mit exakten Stripe-Links
    p_conf = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "(1 Dokument)", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "(3 Dokumente)", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://stripe.com")
    ]
    for style, name, docs, price, link in p_conf:
        st.markdown(f'<div class="paket-container {style}"><span style="font-weight:bold">{name}</span><br>{docs}<div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_main:
    c_preview, c_res = st.columns([1.8, 1.4])
    
    with c_preview:
        st.subheader("📄 Dokument")
        u_file = st.file_uploader("Brief hier hochladen", type=["pdf", "jpg", "png"])
        if u_file:
            if u_file.type == "application/pdf":
                st.info("PDF geladen.")
            else: st.image(u_file, use_container_width=True)

    with c_res:
        st.subheader("🔍 Auswertung")
        if u_file:
            st.error("📅 **FRIST-CHECK: 30.04.2026**")
            
            with st.expander("📖 Glossar", expanded=True):
                st.text("Verwaltungsakt: Amtliche Entscheidung.\nErmessen: Handlungsspielraum.")

            # Beispieltexte für Export
            beispiel_text = "Sehr geehrte Damen und Herren,\nhiermit lege ich Widerspruch ein..."
            
            st.write("---")
            st.subheader("📥 Downloads")
            st.download_button("📄 PDF Export", create_pdf(beispiel_text), "Amtsschimmel_Killer.pdf", "application/pdf", use_container_width=True)
            st.download_button("📝 Word Export", create_docx(beispiel_text), "Amtsschimmel_Killer.docx", use_container_width=True)
            st.download_button("📅 Termin (iCal)", create_ical(), "Frist.ics", "text/calendar", use_container_width=True)
        else:
            st.info("Laden Sie ein Dokument hoch oder wählen Sie ein Paket.")

if __name__ == "__main__":
    main()
