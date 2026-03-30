import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from pdf2image import convert_from_bytes # Für garantierte Vorschau

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (FARBIGE BOXEN & BUTTONS) ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .paket-container { border-radius: 12px; padding: 15px; margin-bottom: 20px; border: 2px solid; background: white; }
    .blue-header { background-color: #e3f2fd; padding: 10px; border-radius: 8px; font-weight: bold; color: #007bff; margin-bottom: 10px; }
    .green-header { background-color: #e8f5e9; padding: 10px; border-radius: 8px; font-weight: bold; color: #28a745; margin-bottom: 10px; }
    .gold-header { background-color: #fff9e6; padding: 10px; border-radius: 8px; font-weight: bold; color: #fcc419; margin-bottom: 10px; }
    .price-tag { font-size: 22px; font-weight: bold; color: #1E3A8A; margin: 5px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. TECHNISCHE FUNKTIONEN (DOWNLOADS & VORSCHAU) ---
def get_pdf_images(pdf_bytes):
    try:
        images = convert_from_bytes(pdf_bytes)
        return images
    except:
        return None

def create_excel(data_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data_dict])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 80) # Extrem breite Spalten
    return output.getvalue()

# --- 4. TOP-BAR (EXAKTE TEXTE) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\n\nBetreiberin:\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich...\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet...\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI übertragen...\n\n4. Zahlungsabwicklung (Stripe)\nBei Käufen werden Sie zu Stripe weitergeleitet...\n\n5. Ihre Rechte\nKontakt unter amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Wir hassen Abos genauso wie Amtsschimmel...\n\nWie sicher sind meine Dokumente?\nVerschlüsselt an OpenAI, keine dauerhafte Speicherung.\n\nErsetzt die App eine Rechtsberatung?\nNein. Wir bieten eine Formulierungshilfe.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung...")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    try: st.image("icon_final_blau.png", width=160)
    except: st.markdown("🏛️ **Amtsschimmel-Killer**")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], label_visibility="collapsed")
    
    st.write("---")
    st.markdown("### 📦 Pakete")
    
    # Paket 1: Analyse
    st.markdown('<div class="paket-container" style="border-color: #007bff;"><div class="blue-header">🛡️ Amtsschimmel-Killer Analyse</div>', unsafe_allow_html=True)
    st.write("(1 Dokument)")
    st.markdown('<p class="price-tag">3,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung kein Abo</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    st.markdown('</div>', unsafe_allow_html=True)

    # Paket 2: Spar
    st.markdown('<div class="paket-container" style="border-color: #28a745;"><div class="green-header">⚔️ Amtsschimmel-Killer Spar-Paket</div>', unsafe_allow_html=True)
    st.write("(3 Dokumente)")
    st.markdown('<p class="price-tag">9,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung kein Abo</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    st.markdown('</div>', unsafe_allow_html=True)

    # Paket 3: Sorglos
    st.markdown('<div class="paket-container" style="border-color: #fcc419;"><div class="gold-header">🚀 Amtsschimmel-Killer Sorglos-Paket</div>', unsafe_allow_html=True)
    st.write("(10 Dokumente)")
    st.markdown('<p class="price-tag">19,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung kein Abo</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    st.subheader("📄 Dokument & Vorschau")
    uploaded_file = st.file_uploader("Upload", type=["pdf", "jpg", "png"], label_visibility="collapsed")
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            imgs = get_pdf_images(uploaded_file.getvalue())
            if imgs:
                for img in imgs: st.image(img, use_container_width=True)
            else: st.warning("Vorschau-Generator lädt... (Bitte poppler installieren)")
        else:
            st.image(uploaded_file, use_container_width=True)

with col_right:
    st.subheader("🔍 Auswertung")
    if uploaded_file:
        st.error("📅 **Frist-Check:** Die Frist endet am 30.04.2026.")
        
        # Ausführliche Inhalte
        glossar = """**Rechtsbehelfsbelehrung:** Ein zwingender Bestandteil von Bescheiden, der Ihnen erklärt, wie, wo und innerhalb welcher Frist Sie Widerspruch einlegen können.
**Ermessensunterschreitung:** Wenn die Behörde ihr Ermessen nicht nutzt, obwohl das Gesetz dies vorsieht.
**Verwaltungsakt:** Jede Verfügung oder Entscheidung einer Behörde zur Regelung eines Einzelfalls."""
        
        antwort = """Sehr geehrte Damen und Herren,\n\nbezüglich Ihres Schreibens vom [Datum] (AZ: [Aktenzeichen]) nehme ich wie folgt Stellung...\n\n[PLATZHALTER: Vorname, Nachname, Adresse, Datum]"""
        
        widerspruch = """Sehr geehrte Damen und Herren,\n\ngegen den Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit fristgerecht WIDERSPRUCH ein...\n\n[PLATZHALTER: Aktenzeichen, Name, Unterschrift]"""

        st.info(f"📚 **Glossar:**\n{glossar}")
        with st.expander("✍️ Antwortschreiben"): st.text(antwort)
        with st.expander("⚖️ Widerspruch"): st.text(widerspruch)
        
        st.write("---")
        st.subheader("💾 Downloads")
        
        # Excel
        ex_data = create_excel({"Frist": "30.04.2026", "Glossar": glossar, "Antwort": antwort, "Widerspruch": widerspruch})
        st.download_button("📊 Analyse (.xlsx)", ex_data, "Analyse.xlsx")
        
        # PDF Fallback
        st.download_button("📄 PDF-Bericht", uploaded_file.getvalue(), "Bericht.pdf")
        st.button("📅 Termin (Kalender.ico)")
    else:
        st.info("Warten auf Upload...")
