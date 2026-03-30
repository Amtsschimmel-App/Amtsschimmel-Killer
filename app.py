import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (PAKET-BOXEN & BUTTONS) ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 25px; border: 2px solid; background: white; }
    .blue-header { background-color: #e3f2fd; padding: 10px; border-radius: 8px; font-weight: bold; color: #007bff; margin-bottom: 10px; }
    .green-header { background-color: #e8f5e9; padding: 10px; border-radius: 8px; font-weight: bold; color: #28a745; margin-bottom: 10px; }
    .gold-header { background-color: #fff9e6; padding: 10px; border-radius: 8px; font-weight: bold; color: #fcc419; margin-bottom: 10px; }
    .price-tag { font-size: 24px; font-weight: bold; color: #1E3A8A; margin: 5px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .stExpander { border: none !important; box-shadow: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. TECHNISCHE FUNKTIONEN (REPARIERTE VORSCHAU) ---
def render_preview(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
        # PDF Embed mit Fallback-Höhe
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf" style="border:1px solid #ccc;"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.image(uploaded_file, use_container_width=True)

# --- 4. TOP-BAR: RECHTLICHES (EXAKTE TEXTE) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("**Amtsschimmel-Killer**")
        st.markdown("Betreiberin:<br>Elisabeth Reinecke<br>Ringelsweide 9<br>40223 Düsseldorf", unsafe_allow_html=True)
        st.markdown("Kontakt:<br>Telefon: +49 211 15821329<br>E-Mail: amtsschimmel-killer@proton.me<br>Web: amtsschimmel-killer.streamlit.app", unsafe_allow_html=True)
        st.markdown("Haftung:<br>Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.", unsafe_allow_html=True)
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.write("1. Datenschutz auf einen Blick: Wir behandeln Ihre personenbezogenen Daten vertraulich...")
        st.write("2. Datenerfassung & Hosting: Diese App wird auf Streamlit Cloud gehostet...")
        st.write("3. Dokumentenverarbeitung: Ihre hochgeladenen Briefe werden per TLS-verschlüsselt an OpenAI übertragen...")
        st.write("4. Zahlungsabwicklung (Stripe): Bei Käufen werden Sie zu Stripe weitergeleitet...")
        st.write("5. Ihre Rechte: Kontakt unter amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.write("**Ist das ein Abonnement?**\nNein. Wir hassen Abos. Jede Zahlung ist eine Einmalzahlung.")
        st.write("**Wie sicher sind meine Dokumente?**\nVerschlüsselt an OpenAI, keine dauerhafte Speicherung.")
        st.write("**Ersetzt die App eine Rechtsberatung?**\nNein. Wir bieten Formulierungshilfe.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.code("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung...")
        st.code("Widerspruch:\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum] lege ich Widerspruch ein...")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1.1, 1.6, 1.2])

with col_left:
    # Logo & Sprachen
    try: st.image("icon_final_blau.png", width=140)
    except: st.subheader("🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], label_visibility="collapsed")
    
    st.write("---")
    st.markdown("### 📦 Pakete")
    
    # Paket 1: Analyse
    st.markdown('<div class="paket-container" style="border-color: #007bff;"><div class="blue-header">🛡️ Amtsschimmel-Killer Analyse</div>(1 Dokument)<p class="price-tag">3,99 €</p><p class="no-abo">Einmalzahlung kein Abo</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    st.markdown('</div>', unsafe_allow_html=True)

    # Paket 2: Spar
    st.markdown('<div class="paket-container" style="border-color: #28a745;"><div class="green-header">⚔️ Amtsschimmel-Killer Spar-Paket</div>(3 Dokumente)<p class="price-tag">9,99 €</p><p class="no-abo">Einmalzahlung kein Abo</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    st.markdown('</div>', unsafe_allow_html=True)

    # Paket 3: Sorglos
    st.markdown('<div class="paket-container" style="border-color: #fcc419;"><div class="gold-header">🚀 Amtsschimmel-Killer Sorglos-Paket</div>(10 Dokumente)<p class="price-tag">19,99 €</p><p class="no-abo">Einmalzahlung kein Abo</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    st.subheader("📄 Dokument & Vorschau")
    uploaded_file = st.file_uploader("Datei hier ablegen", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded_file:
        render_preview(uploaded_file)
    else:
        st.info("Bitte laden Sie ein Dokument hoch, um die Vorschau zu sehen.")

with col_right:
    st.subheader("🔍 Auswertung")
    if uploaded_file:
        st.success("Dokument erkannt. Bitte wählen Sie ein Paket zur vollständigen Analyse.")
    else:
        st.write("Warten auf Upload...")
