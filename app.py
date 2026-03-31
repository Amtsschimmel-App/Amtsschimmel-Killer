import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from fpdf import FPDF
from docx import Document

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CSS (PAKETE & BUTTONS) ---
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    .header-text { font-size: 16px; font-weight: bold; margin-bottom: 10px; display: block; color: #333; }
    .price-tag { font-size: 28px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link {
        display: inline-block; padding: 12px 20px; background-color: #1E3A8A; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 90%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DOWNLOAD LOGIK (EXCEL AUTO-WIDTH & FULL TEXTS) ---
def create_excel(content_list):
    output = BytesIO()
    df = pd.DataFrame([content_list])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 70) # Breite Spalten für viel Text
    return output.getvalue()

def create_full_docx(title, text):
    doc = Document()
    doc.add_heading(title, 0)
    for line in text.split('\n'):
        doc.add_paragraph(line)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_full_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- 4. RECHTSTEXTE (1:1 ÜBERNOMMEN) ---
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

# --- 5. HAUPT-LAYOUT (DRAG & DROP RECHTS NEBEN PAKETEN) ---
col_pakete, col_main = st.columns([1.2, 3.2])

with col_pakete:
    try: st.image("icon_final_blau.png", width=120)
    except: st.subheader("🏛️ Amtsschimmel-Killer")
    
    langs = ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"]
    st.selectbox("Sprache", langs, key="lang_box")
    st.write("---")
    
    p_data = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "(1 Dokument)", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "(3 Dokumente)", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")
    ]
    for style, name, docs, price, link in p_data:
        st.markdown(f'<div class="paket-container {style}"><span class="header-text">{name}</span>{docs}<div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_main:
    col_view, col_res = st.columns([1.8, 1.4])
    
    with col_view:
        st.subheader("📄 Dokument")
        u_file = st.file_uploader("Drag and drop file here", type=["pdf", "jpg", "png"], key="file_drop")
        if u_file:
            if u_file.type == "application/pdf":
                st.info("PDF geladen. Falls die Vorschau blockiert wird, nutzen Sie den Download-Button unten.")
                b64 = base64.b64encode(u_file.read()).decode('utf-8')
                st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="700"></iframe>', unsafe_allow_html=True)
            else: st.image(u_file, use_container_width=True)
            
    with col_res:
        st.subheader("🔍 Auswertung")
        if u_file:
            st.error("📅 **FRIST-CHECK: 30.04.2026**")
            st.markdown("📅 **Kalender:** [📅 In Kalender eintragen (iCal)](#)")
            
            with st.expander("📖 Ausgiebiges Glossar", expanded=True):
                st.markdown("""**Rechtsbehelfsbelehrung:** Erklärt den Weg des Widerspruchs.  
**Verwaltungsakt:** Formale Entscheidung einer Behörde.  
**Ermessen:** Handlungsspielraum der Behörde.  
**Anhörung:** Ihr Recht, sich vor einer Entscheidung zu äußern.  
**Frist:** Der Zeitraum, in dem eine Antwort erfolgen muss.  
**Aktenzeichen:** Die Kennnummer Ihres Vorgangs beim Amt.""")
            
            # --- TEXTE FÜR DOWNLOADS ---
            full_response = "Sehr geehrte Damen und Herren,\n\nin der Angelegenheit [Aktenzeichen] nehme ich Bezug auf Ihr Schreiben vom [Datum].\n\n\n\nMit freundlichen Grüßen,\n\n[VORNAME NACHNAME]\n[STRASSE HAUSNUMMER]\n[PLZ ORT]\n[DATUM]"
            widerspruch_txt = "Sehr geehrte Damen und Herren,\n\ngegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit fristwahrend\n\nWIDERSPRUCH\n\nein. Eine detaillierte Begründung folgt in einem separaten Schreiben.\n\nMit freundlichen Grüßen,\n[UNTERSCHRIFT]"

            with st.expander("✉️ Antwort-Entwurf", expanded=True):
                final_txt = st.text_area("Entwurf (mit Platzhaltern):", full_response, height=250)
                st.download_button("📄 Download Word (.docx)", create_full_docx("Antwortbrief", final_txt), "Antwort_Amtsschimmel.docx")
                
                # Excel Download
                ex_data = {"Dokument": u_file.name, "Frist": "30.04.2026", "Entwurf": final_txt, "Glossar": "Rechtsbehelfsbelehrung, Verwaltungsakt, Ermessen"}
                st.download_button("📊 Download Excel (.xlsx)", create_excel(ex_data), "Analyse_Ergebnis.xlsx")
            
            with st.expander("⚖️ Widerspruch generieren", expanded=False):
                st.text_area("Vorschau Widerspruch:", widerspruch_txt, height=150)
                st.download_button("📕 Widerspruch als PDF speichern", create_full_pdf(widerspruch_txt), "Widerspruch.pdf")
        else:
            st.info("Warten auf Upload...")
