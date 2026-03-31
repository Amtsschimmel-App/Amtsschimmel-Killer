import streamlit as st
import base64
from PIL import Image
import io

# --- 1. SEITENKONFIGURATION & LOGO ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🤖")

# Custom CSS für die farbigen Pakete und das Layout
st.markdown("""
    <style>
    .package-box {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 2px solid;
        text-align: center;
    }
    .blue-box { border-color: #007bff; background-color: #f0f7ff; }
    .green-box { border-color: #28a745; background-color: #f3fff5; }
    .gold-box { border-color: #ffc107; background-color: #fffdf0; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    .price-tag { font-size: 24px; font-weight: bold; display: block; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR: PAKETE & SPRACHEN ---
with st.sidebar:
    st.image("https://githubusercontent.com", width=100) # Falls Pfad lokal, anpassen
    st.title("Amtsschimmel-Killer")
    
    # Sprachen-Auswahl (12 Sprachen)
    languages = ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", 
                 "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", 
                 "NL Nederlands", "VN Tiếng Việt"]
    selected_lang = st.selectbox("Sprache / Language", languages)

    st.markdown("---")

    # Paket 1: Analyse (Blau)
    st.markdown("""<div class="package-box blue-box">
        <h4>🔹 Amtsschimmel-Killer Analyse</h4>
        <p>(1 Dokument)</p>
        <span class="price-tag">3,99 €</span>
        <p><small>Einmalzahlung kein Abo</small></p>
        </div>""", unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", type="primary", help="Stripe Endung ...gs02")

    # Paket 2: Spar-Paket (Grün)
    st.markdown("""<div class="package-box green-box">
        <h4>🟢 Amtsschimmel-Killer Spar-Paket</h4>
        <p>(3 Dokumente)</p>
        <span class="price-tag">9,99 €</span>
        <p><small>Einmalzahlung kein Abo</small></p>
        </div>""", unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", type="primary", help="Stripe Endung ...gs03")

    # Paket 3: Sorglos-Paket (Gold)
    st.markdown("""<div class="package-box gold-box">
        <h4>👑 Amtsschimmel-Killer Sorglos-Paket</h4>
        <p>(10 Dokumente)</p>
        <span class="price-tag">19,99 €</span>
        <p><small>Einmalzahlung kein Abo</small></p>
        </div>""", unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041", type="primary", help="Stripe Endung ...gs041")

# --- 3. HAUPTBEREICH: RECHTLICHES & TOOLS ---
col_main, col_eval = st.columns([1, 1.2])

with col_main:
    st.header("📄 Dokument hochladen")
    
    with st.expander("⚖️ Rechtliche Informationen (Impressum, Datenschutz)"):
        tab1, tab2, tab3, tab4 = st.tabs(["Impressum", "Datenschutz", "FAQ", "Vorlagen"])
        
        with tab1:
            st.markdown("""**Betreiberin:** Elisabeth Reinecke<br>Ringelsweide 9, 40223 Düsseldorf<br>
            **Kontakt:** +49 211 15821329 | amtsschimmel-killer@proton.me<br>
            **Haftung:** Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""", unsafe_allow_html=True)
            
        with tab2:
            st.markdown("""1. **Datenschutz:** Vertraulich gemäß DSGVO.<br>
            2. **Hosting:** Streamlit Cloud.<br>
            3. **Dokumente:** Übertragung an OpenAI via TLS. Keine dauerhafte Speicherung.<br>
            4. **Zahlung:** Abwicklung über Stripe.<br>
            5. **Rechte:** Auskunft/Löschung via E-Mail.""", unsafe_allow_html=True)
            
        with tab3:
            st.write("**Ist das ein Abo?** Nein. Einmalzahlung.")
            st.write("**Sicherheit?** Verschlüsselte Übertragung, sofortige Löschung.")
            st.write("**Rechtsberatung?** Nein, nur Formulierungshilfe.")
            
        with tab4:
            st.info("**Fristverlängerung:** ...bitte um Verlängerung der gesetzten Frist bis zum [Datum]...")
            st.info("**Widerspruch:** ...gegen Ihren Bescheid vom [Datum] lege ich hiermit Widerspruch ein...")
            st.info("**Akteneinsicht:** ...beantrage ich gemäß § 25 SGB X Akteneinsicht...")

    uploaded_file = st.file_uploader("Brief/Bescheid hier reinziehen (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])

# --- 4. AUSWERTUNG & LOGIK ---
with col_eval:
    st.header("🔍 Auswertung")
    
    if uploaded_file is not None:
        # Check Dateityp zur Vermeidung von Error 400
        file_ext = uploaded_file.name.split('.')[-1].lower()
        
        if file_ext == "pdf":
            st.success(f"PDF '{uploaded_file.name}' erfolgreich geladen.")
            # Hier käme die PDF-Verarbeitung (z.B. pdf2image)
        elif file_ext in ["png", "jpg", "jpeg"]:
            image = Image.open(uploaded_file)
            st.image(image, caption="Vorschau", use_container_width=True)
        else:
            st.error("Fehler: Ungültiges Format. Bitte nur PDF, PNG oder JPG nutzen.")

        # --- DOWNLOAD ZENTRUM (2x2 Grid) ---
        st.markdown("### 📥 Download-Zentrum")
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📊 Excel (Komplett)", data=b"Dummy Data", file_name="analyse.xlsx", key="btn_xl")
            st.download_button("📝 Word (Briefe)", data=b"Dummy Data", file_name="briefe.docx", key="btn_doc")
        with c2:
            st.download_button("📕 PDF (Widerspruch)", data=b"Dummy Data", file_name="widerspruch.pdf", key="btn_pdf")
            st.download_button("📅 Termin (iCal)", data=b"Dummy Data", file_name="frist.ics", key="btn_ical")

    else:
        st.info("Bitte laden Sie ein Dokument hoch, um die Analyse zu starten.")

# --- 5. FOOTER ---
st.markdown("---")
st.caption("© 2024 Amtsschimmel-Killer | Elisabeth Reinecke | Düsseldorf")
