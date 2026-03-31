import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- 1. SETUP & LOGO ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# CSS für bunte Boxen, Icons und Stripe-Buttons
st.markdown("""
<style>
    .paket-container { border-radius: 15px; padding: 25px; margin-bottom: 20px; border: 4px solid; background: white; text-align: center; min-height: 350px; }
    .blue-box { border-color: #007bff; background-color: #f0f7ff; }
    .green-box { border-color: #28a745; background-color: #f1f9f1; }
    .gold-box { border-color: #fcc419; background-color: #fffdf5; }
    .header-text { font-size: 18px; font-weight: bold; margin-bottom: 10px; display: block; color: #333; }
    .price-tag { font-size: 32px; font-weight: bold; color: #1E3A8A; margin: 15px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 20px; display: block; }
    .stripe-link {
        display: inline-block; padding: 14px 25px; background-color: #1E3A8A !important; color: white !important;
        text-decoration: none; border-radius: 10px; font-weight: bold; width: 90%; text-align: center; font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Logo Bereich
st.markdown("### 🏛️ Amtsschimmel-Killer")

# --- 2. DOWNLOAD-LOGIK ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return bytes(pdf.output(dest='S'))

# --- 3. SPRACHWAHL ---
st.write("🌍 **Sprache wählen / Choose Language / Dil Seçin / Wybierz język / اختر اللغة**")
lang = st.radio("", ["Deutsch", "English", "Türkçe", "Polski", "عربي"], horizontal=True, label_visibility="collapsed")

# --- 4. CREDIT-ZÄHLER & STRIPE LOGIK ---
if 'credits' not in st.session_state:
    st.session_state.credits = 0

params = st.query_params
if "pack" in params:
    if params["pack"] == "1": st.session_state.credits += 1
    elif params["pack"] == "3": st.session_state.credits += 3
    elif params["pack"] == "10": st.session_state.credits += 10
    st.query_params.clear()

st.info(f"Aktuelles Guthaben: {st.session_state.credits} Dokument(e)")

# --- 5. PAKETE (BUNTE BOXEN) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="paket-container blue-box">
        <span class="header-text">📄 Amtsschimmel-Killer Analyse</span>
        <p>(1 Dokument)</p>
        <div class="price-tag">3,99 €</div>
        <span class="no-abo">Einmalzahlung kein Abo</span>
        <a href="https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" class="stripe-link">Jetzt kaufen</a>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="paket-container green-box">
        <span class="header-text">📦 Amtsschimmel-Killer Spar-Paket</span>
        <p>(3 Dokumente)</p>
        <div class="price-tag">9,99 €</div>
        <span class="no-abo">Einmalzahlung kein Abo</span>
        <a href="https://buy.stripe.com/8x228retRbj50paalq1gs03" class="stripe-link">Jetzt kaufen</a>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="paket-container gold-box">
        <span class="header-text">🚀 Amtsschimmel-Killer Sorglos-Paket</span>
        <p>(10 Dokumente)</p>
        <div class="price-tag">19,99 €</div>
        <span class="no-abo">Einmalzahlung kein Abo</span>
        <a href="https://stripe.com" class="stripe-link">Jetzt kaufen</a>
    </div>
    """, unsafe_allow_html=True)

# --- 6. ANALYSE BEREICH ---
st.divider()
if st.session_state.credits > 0:
    file = st.file_uploader("Brief hier hochladen", type=["pdf", "jpg", "png", "jpeg"])
    if file and st.button("Jetzt Dokument killen"):
        st.success("Analyse läuft...")
else:
    st.warning("Bitte wählen Sie ein Paket aus, um die Analyse zu starten.")

# --- 7. VORLAGEN ---
with st.expander("📄 Vorlagen (Exakte Texte)"):
    st.markdown("**Fristverlängerung:**")
    st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")
    st.markdown("**Widerspruch einlegen (Fristwahrend):**")
    st.code("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]")
    st.markdown("**Akteneinsicht einfordern:**")
    st.code("Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

# --- 8. FAQ, IMPRESSUM, DATENSCHUTZ ---
st.divider()
f1, f2, f3 = st.columns(3)
with f1:
    with st.expander("❓ FAQ"):
        st.write("""**Ist das ein Abonnement?**
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

**Wie sicher sind meine Dokumente?**
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

**Ersetzt die App eine Rechtsberatung?**
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

**Was passiert, wenn der Scan fehlschlägt?**
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

**Wie erreiche ich Elisabeth Reinecke?**
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.""")

with f2:
    with st.expander("⚖️ Impressum"):
        st.write("""**Amtsschimmel-Killer**
Betreiberin: Elisabeth Reinecke
Ringelsweide 9, 40223 Düsseldorf
Kontakt: Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app
Haftung: Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")

with f3:
    with st.expander("🛡️ Datenschutz"):
        st.write("""1. **Datenschutz auf einen Blick**
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).
2. **Datenerfassung & Hosting**
Diese App wird auf Streamlit Cloud gehostet. Wir nutzen Logfiles nicht.
3. **Dokumentenverarbeitung**
TLS-verschlüsselte Übertragung an OpenAI (USA). Keine Speicherung auf unseren Servern.
4. **Zahlungsabwicklung (Stripe)**
Abrechnung über Stripe. Wir erhalten nur die Zahlungsbestätigung.
5. **Ihre Rechte**
Auskunft, Löschung und Sperrung unter amtsschimmel-killer@proton.me.""")
