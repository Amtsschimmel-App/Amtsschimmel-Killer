import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

st.markdown("""
<style>
    .paket-box { border-radius: 10px; padding: 15px; margin-bottom: 15px; border: 2px solid; background: #fff; text-align: center; }
    .blue { border-color: #007bff; background-color: #f0f7ff; }
    .green { border-color: #28a745; background-color: #f1f9f1; }
    .gold { border-color: #fcc419; background-color: #fffdf5; }
    .price-tag { font-size: 24px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 13px; color: #d32f2f; font-weight: bold; margin-bottom: 10px; }
    .buy-btn {
        display: inline-block; padding: 12px; background-color: #1E3A8A; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 100%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CREDIT-ZÄHLER LOGIK (URL PARAMETER) ---
if 'credits' not in st.session_state:
    st.session_state.credits = 0

params = st.query_params
if "pack" in params:
    if params["pack"] == "1": st.session_state.credits += 1
    elif params["pack"] == "3": st.session_state.credits += 3
    elif params["pack"] == "10": st.session_state.credits += 10
    st.query_params.clear()

# --- 3. LAYOUT: SEITENLEISTE (PAKETE & SPRACHE) ---
with st.sidebar:
    st.header("🏛️ Amtsschimmel-Killer")
    # Platzhalter für Logo beibehalten
    st.image("https://placeholder.com", width=150) 
    
    st.selectbox("Sprache / Language", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "AR العربية"], key="lang")
    st.write("---")
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    # Paket 1
    st.markdown(f'''<div class="paket-box blue">
        <strong>Amtsschimmel-Killer Analyse</strong><br>(1 Dokument)
        <div class="price-tag">3,99 €</div>
        <div class="no-abo">Einmalzahlung kein Abo</div>
        <a href="https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" target="_blank" class="buy-btn">Jetzt kaufen</a>
    </div>''', unsafe_allow_html=True)

    # Paket 3
    st.markdown(f'''<div class="paket-box green">
        <strong>Amtsschimmel-Killer Spar-Paket</strong><br>(3 Dokumente)
        <div class="price-tag">9,99 €</div>
        <div class="no-abo">Einmalzahlung kein Abo</div>
        <a href="https://buy.stripe.com/8x228retRbj50paalq1gs03" target="_blank" class="buy-btn">Jetzt kaufen</a>
    </div>''', unsafe_allow_html=True)

    # Paket 10
    st.markdown(f'''<div class="paket-box gold">
        <strong>Amtsschimmel-Killer Sorglos-Paket</strong><br>(10 Dokumente)
        <div class="price-tag">19,99 €</div>
        <div class="no-abo">Einmalzahlung kein Abo</div>
        <a href="https://stripe.com" target="_blank" class="buy-btn">Jetzt kaufen</a>
    </div>''', unsafe_allow_html=True)

# --- 4. HAUPTBEREICH (ANALYSE & RECHTSINFOS) ---
col_main, col_info = st.columns([2, 1.2])

with col_main:
    st.title("Dokumenten-Check")
    if st.session_state.credits > 0:
        u_file = st.file_uploader("Brief hier hochladen (PDF, JPG, PNG)", type=["pdf", "jpg", "png"])
        if u_file and st.button("Analyse starten"):
            st.info("KI-Analyse wird ausgeführt...")
    else:
        st.warning("Bitte wähle ein Paket in der Seitenleiste aus, um Guthaben aufzuladen.")

    st.divider()
    
    st.subheader("📝 Vorlagen")
    st.text("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")
    st.text("Widerspruch einlegen (Fristwahrend):\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]")
    st.text("Akteneinsicht einfordern:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

with col_info:
    with st.expander("❓ FAQ", expanded=True):
        st.write("""**Ist das ein Abonnement?**
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

**Wie sicher sind meine Dokumente?**
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert.

**Ersetzt die App eine Rechtsberatung?**
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis.

**Was passiert, wenn der Scan fehlschlägt?**
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat.""")

    with st.expander("⚖️ Impressum"):
        st.write("""Amtsschimmel-Killer
Betreiberin: Elisabeth Reinecke
Ringelsweide 9, 40223 Düsseldorf
Kontakt: Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Haftung: Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")

    with st.expander("🛡️ Datenschutz"):
        st.write("""1. Datenschutz auf einen Blick: Wir behandeln Ihre Daten vertraulich (DSGVO).
2. Hosting: Streamlit Cloud. Logfiles werden nicht von uns genutzt.
3. Dokumentenverarbeitung: Verschlüsselte Übertragung an OpenAI (USA). Keine Speicherung.
4. Stripe: Abrechnungsdaten werden bei Stripe erhoben.
5. Ihre Rechte: Auskunft & Löschung unter amtsschimmel-killer@proton.me.""")
