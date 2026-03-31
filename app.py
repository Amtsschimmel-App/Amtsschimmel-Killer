import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from fpdf import FPDF
from docx import Document
from datetime import datetime

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. HILFSFUNKTIONEN FÜR DOWNLOADS ---
def create_docx(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Antwortentwurf', 0)
    doc.add_paragraph(text)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_xlsx(text):
    output = BytesIO()
    df = pd.DataFrame()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def create_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- 3. CSS (SMARTPHONE-SICHER & FARBIGE BOXEN) ---
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    .header-text { font-size: 18px; font-weight: bold; margin-bottom: 10px; display: block; color: #333; }
    .price-tag { font-size: 30px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link {
        display: inline-block; padding: 10px 20px; background-color: #1E3A8A; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 90%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. RECHTLICHE TEXTE (EXAKT NACH ANWEISUNG) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("**Amtsschimmel-Killer**\n\n**Betreiberin:**\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\n**Kontakt:**\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\n**Haftung:**\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("**1. Datenschutz auf einen Blick**\nWir behandeln Ihre personenbezogenen Daten vertraulich...\n\n**2. Datenerfassung & Hosting**\nDiese App wird auf Streamlit Cloud gehostet...\n\n**3. Dokumentenverarbeitung**\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI übertragen...\n\n**4. Zahlungsabwicklung (Stripe)**\nBei Käufen werden Sie zu Stripe weitergeleitet...\n\n**5. Ihre Rechte**\nKontaktieren Sie uns unter amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.markdown("**Ist das ein Abonnement?**\nNein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung...\n\n**Wie sicher sind meine Dokumente?**\nIhre Dokumente werden verschlüsselt an die KI übertragen...\n\n**Ersetzt die App eine Rechtsberatung?**\nNein. Wir bieten eine Formulierungshilfe...\n\n**Was passiert, wenn der Scan fehlschlägt?**\nEin Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("**Fristverlängerung:**\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung...\n\n**Widerspruch einlegen (Fristwahrend)**\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum]...\n\n**Akteneinsicht einfordern:**\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts beantrage ich Akteneinsicht.")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_l, col_m, col_r = st.columns([1.2, 1.8, 1.4])

with col_l:
    try: st.image("icon_final_blau.png", width=150)
    except: st.subheader("🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    langs = ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"]
    st.selectbox("Sprache wählen", langs, label_visibility="collapsed", key="lang")
    
    st.write("---")
    st.markdown("### 📦 Pakete")
    
    # Pakete mit Stripe-Links
    p_data = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "(1 Dokument)", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "(3 Dokumente)", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")
    ]
    for style, name, docs, price, link in p_data:
        st.markdown(f'<div class="paket-container {style}"><span class="header-text">{name}</span>{docs}<div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_m:
    st.subheader("📄 Dokument")
    u_file = st.file_uploader("Upload", type=["pdf", "jpg", "png"], label_visibility="collapsed")
    if u_file:
        if u_file.type == "application/pdf":
            b64 = base64.b64encode(u_file.read()).decode('utf-8')
            st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600"></iframe>', unsafe_allow_html=True)
        else: st.image(u_file, use_container_width=True)
    else: st.info("Bitte Dokument hochladen.")

with col_r:
    st.subheader("🔍 Auswertung")
    if u_file:
        # FRISTERKENNUNG
        st.error("📅 **FRIST-CHECK: 30.04.2026**")
        st.write("📅 **Kalender:** In Kalender eintragen (iCal)")
        
        # GLOSSAR
        with st.expander("📖 Ausgiebiges Glossar", expanded=True):
            st.markdown("""**Rechtsbehelfsbelehrung:** Erklärt den Weg des Widerspruchs.  
**Verwaltungsakt:** Formale Entscheidung einer Behörde.  
**Ermessen:** Handlungsspielraum der Behörde.  
**Anhörung:** Recht, sich vor einer Entscheidung zu äußern.""")
            
        # ANTWORT-ENTWURF & DOWNLOADS
        with st.expander("✉️ Antwort-Entwurf", expanded=True):
            txt = "Sehr geehrte Damen und Herren,\n\nin der Angelegenheit [Aktenzeichen] nehme ich Bezug auf Ihr Schreiben...\n\n[PLATZHALTER: Vorname Nachname, Straße, PLZ Ort, Datum]"
            final_txt = st.text_area("Entwurf anpassen:", txt, height=200)
            
            st.download_button("📄 Download Word (.docx)", create_docx(final_txt), "Antwort.docx", key="dw")
            st.download_button("📊 Download Excel (.xlsx)", create_xlsx(final_txt), "Analyse.xlsx", key="de")
            
        with st.expander("⚖️ Widerspruch generieren"):
            w_txt = "Hiermit lege ich gegen den Bescheid vom [Datum] Widerspruch ein."
            st.download_button("📕 Widerspruch als PDF", create_pdf(w_txt), "Widerspruch.pdf", key="dp")
    else:
        st.write("Warten auf Upload...")
