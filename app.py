import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- 1. SETUP ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CSS FÜR PAKETE (BUNT & EINZELBOXEN) ---
st.markdown("""
<style>
    .paket-container { border-radius: 15px; padding: 20px; margin-bottom: 25px; border: 4px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; background-color: #f0f7ff; }
    .green-box { border-color: #28a745; background-color: #f3fff5; }
    .gold-box { border-color: #fcc419; background-color: #fffdf0; }
    .price-tag { font-size: 30px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 15px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link {
        display: inline-block; padding: 12px 20px; background-color: #1E3A8A !important; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 100%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DOWNLOAD-LOGIK (BYTES-FIX) ---
def get_pdf_bytes(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return bytes(pdf.output(dest='S'))

# --- 4. RECHTSTEXTE (EXAKTE ÜBERNAHME MIT ABSTÄNDEN) ---
t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""
Amtsschimmel-Killer

Betreiberin:

Elisabeth Reinecke

Ringelsweide 9
40223 Düsseldorf

Kontakt:
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

Haftung:
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        """)

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""
1. Datenschutz auf einen Blick
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

2. Datenerfassung & Hosting
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

3. Dokumentenverarbeitung
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

4. Zahlungsabwicklung (Stripe)
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

5. Ihre Rechte
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
        """)

with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""
Ist das ein Abonnement?
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

Wie sicher sind meine Dokumente?
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

Ersetzt die App eine Rechtsberatung?
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

Was passiert, wenn der Scan fehlschlägt?
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

Wie erreiche ich Elisabeth Reinecke?
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
        """)

with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""
**Fristverlängerung:**
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

**Widerspruch einlegen (Fristwahrend)**
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

**Akteneinsicht einfordern:**
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
        """)

st.divider()

# --- 5. HAUPT-LAYOUT (3 SPALTEN) ---
col_pak, col_doc, col_eval = st.columns([1, 1.5, 1.5])

with col_pak:
    # Logo & Sprache
    try: st.image("logo.png", width=120)
    except: st.subheader("🏛️ Amtsschimmel-Killer")
    
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], key="lang_box")
    st.write("---")

    # Pakete exakt nach Vorgabe
    # Paket 1: Analyse
    st.markdown(f'''<div class="paket-container blue-box">
        🛡️ <b>Amtsschimmel-Killer Analyse</b><br>(1 Dokument)
        <div class="price-tag">3,99 €</div>
        <div class="no-abo">Einmalzahlung kein Abo</div>
        <a href="https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" target="_blank" class="st-button-link">Jetzt kaufen</a>
    </div>''', unsafe_allow_html=True)

    # Paket 2: Spar-Paket
    st.markdown(f'''<div class="paket-container green-box">
        ⚔️ <b>Amtsschimmel-Killer Spar-Paket</b><br>(3 Dokumente)
        <div class="price-tag">9,99 €</div>
        <div class="no-abo">Einmalzahlung kein Abo</div>
        <a href="https://buy.stripe.com/8x228retRbj50paalq1gs03" target="_blank" class="st-button-link">Jetzt kaufen</a>
    </div>''', unsafe_allow_html=True)

    # Paket 3: Sorglos-Paket
    st.markdown(f'''<div class="paket-container gold-box">
        🚀 <b>Amtsschimmel-Killer Sorglos-Paket</b><br>(10 Dokumente)
        <div class="price-tag">19,99 €</div>
        <div class="no-abo">Einmalzahlung kein Abo</div>
        <a href="https://buy.stripe.com/28EcN50D1bj52xi8di1gs041" target="_blank" class="st-button-link">Jetzt kaufen</a>
    </div>''', unsafe_allow_html=True)

with col_doc:
    st.subheader("📄 Dokument")
    u_file = st.file_uploader("Brief hier hochladen", type=["pdf", "png", "jpg"], key="main_u")
    if u_file:
        if u_file.type == "application/pdf":
            st.info("PDF geladen.")
            st.download_button("📥 Original PDF öffnen", u_file, file_name="upload.pdf", key="pdf_o")
        else:
            st.image(u_file, use_container_width=True)

with col_eval:
    st.subheader("🔍 Auswertung")
    if u_file:
        st.error("📅 **FRIST-CHECK: 30.04.2026**")
        
        # Hier greift deine bestehende KI-Analyse-Logik
        with st.expander("📖 Glossar", expanded=True):
            st.text_area("Analyse", "KI Ergebnisse...", key="ta_glo")
        
        with st.expander("📋 Antwort-Entwurf"):
            ant = st.text_area("Entwurf", "Brieftext...", height=200, key="ta_ant")

        st.markdown("### 📥 Download-Zentrum")
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📊 Excel", b"xlsx", "analyse.xlsx", key="d_xl")
            st.download_button("📝 Word", b"docx", "brief.docx", key="d_doc")
        with c2:
            st.download_button("📕 PDF", get_pdf_bytes(ant), "widerspruch.pdf", key="d_pdf")
            st.download_button("📅 Termin", b"ics", "frist.ics", key="d_ics")
