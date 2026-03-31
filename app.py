import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document
import base64

# --- 1. SETUP ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. DOWNLOAD-LOGIK (HOCHKOMPATIBEL) ---
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
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 80) # Automatische Breite simulieren
    return output.getvalue()

def create_docx(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Entwurf', 0)
    for line in text.split('\n'):
        doc.add_paragraph(line)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_pdf(text):
    # Sicherer PDF-Export für Streamlit Cloud
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. CSS (PAKETE & STRIPE) ---
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    .header-text { font-size: 16px; font-weight: bold; margin-bottom: 10px; display: block; color: #333; }
    .price-tag { font-size: 28px; font-weight: bold; color: #1E3A8A; margin: 15px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link {
        display: inline-block; padding: 12px 20px; background-color: #1E3A8A; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 95%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. RECHTSTEXTE (1:1 ÜBERNAHME) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\n\nBetreiberin:\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich...\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet...\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI übertragen...\n\n4. Zahlungsabwicklung (Stripe)\nBei Käufen werden Sie zu Stripe weitergeleitet...\n\n5. Ihre Rechte\nKontaktieren Sie uns unter amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.\n\nWie sicher sind meine Dokumente?\nIhre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.\n\nErsetzt die App eine Rechtsberatung?\nNein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.\n\nWas passiert, wenn der Scan fehlschlägt?\nEin Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.\n\nWie erreiche ich Elisabeth Reinecke?\nNutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung...\n\nWiderspruch einlegen (Fristwahrend)\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum]...\n\nAkteneinsicht einfordern:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts beantrage ich Akteneinsicht.")

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
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")
    ]
    for style, name, docs, price, link in p_conf:
        st.markdown(f'<div class="paket-container {style}"><span style="font-weight:bold">{name}</span><br>{docs}<div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_main:
    c_preview, c_res = st.columns([1.8, 1.4])
    
    with c_preview:
        st.subheader("📄 Dokument")
        u_file = st.file_uploader("Datei hochladen", type=["pdf", "jpg", "png"])
        if u_file:
            if u_file.type == "application/pdf":
                st.info("PDF geladen (Smartphone-Sicher).")
                st.markdown("<h1>📄</h1>", unsafe_allow_html=True)
                st.download_button("📥 PDF anzeigen/laden", u_file, file_name="upload.pdf")
            else: st.image(u_file, use_container_width=True)

    with c_res:
        st.subheader("🔍 Auswertung")
        if u_file:
            st.error("📅 **FRIST-CHECK: 30.04.2026**")
            
            with st.expander("📖 Ausgiebiges Glossar", expanded=True):
                glossar_full = "Rechtsbehelfsbelehrung: Erklärt den Weg des Widerspruchs.\nVerwaltungsakt: Amtliche Entscheidung.\nErmessen: Handlungsspielraum der Behörde."
                st.markdown(glossar_full)

            # --- TEXTE ---
            antwort_voll = "[NAME]\n[STRASSE]\n[PLZ ORT]\n\nAn: [BEHÖRDE]\n\nBetreff: Antwort auf Ihr Schreiben\nAktenzeichen: [AKTENZEICHEN]\n\nSehr geehrte Damen und Herren,\n\nin der Angelegenheit [AKTENZEICHEN] nehme ich Bezug auf Ihr Schreiben vom [DATUM].\n\n[HIER KOMMT DIE BEGRÜNDUNG DER KI HIN]\n\nIch bitte um Bestätigung.\n\nMit freundlichen Grüßen,\n[UNTERSCHRIFT]"
            
            widerspruch_voll = "[NAME]\n[STRASSE]\n[PLZ ORT]\n\nAn: [BEHÖRDE]\n\nWIDERSPRUCH\n\nSehr geehrte Damen und Herren,\n\ngegen Ihren Bescheid vom [DATUM], erhalten am [DATUM], lege ich hiermit fristwahrend WIDERSPRUCH ein.\n\nEine Begründung erfolgt nach Akteneinsicht.\n\nMit freundlichen Grüßen,\n[UNTERSCHRIFT]"

            with st.expander("✉️ Antwort-Entwurf", expanded=True):
                st.text_area("Inhalt:", antwort_voll, height=150)
            
            with st.expander("⚖️ Widerspruch", expanded=True):
                st.text_area("Inhalt:", widerspruch_voll, height=150)

            # --- ZENTRALE DOWNLOADS UNTEN ---
            st.write("---")
            st.subheader("📥 Downloads")
            d1, d2, d3 = st.columns(3)
            with d1:
                st.download_button("📊 Excel (Komplett)", create_excel_report(antwort_voll, widerspruch_voll, glossar_full), "Analyse.xlsx")
            with d2:
                st.download_button("📄 Word (Entwürfe)", create_docx(antwort_voll + "\n\n---\n\n" + widerspruch_voll), "Briefe.docx")
            with d3:
                st.download_button("📕 PDF (Widerspruch)", create_pdf(widerspruch_voll), "Widerspruch.pdf")
        else: st.info("Bitte Dokument hochladen.")
