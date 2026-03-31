import streamlit as st

# --- KONFIGURATION & STYLING ---
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="⚖️", layout="wide")

# CSS für bunte Boxen und Design
st.markdown("""
    <style>
    .package-box {
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 2px solid #f0f2f6;
        text-align: center;
    }
    .box-1 { background-color: #E8F4FD; border-color: #2196F3; }
    .box-3 { background-color: #F1F8E9; border-color: #4CAF50; }
    .box-10 { background-color: #FFF3E0; border-color: #FF9800; }
    .price-tag { font-size: 24px; font-weight: bold; margin: 10px 0; }
    .no-abo { color: #d32f2f; font-weight: bold; font-size: 0.9em; }
    .stripe-button {
        background-color: #6772E5;
        color: white !important;
        padding: 10px 20px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE (CREDITS) ---
if 'credits' not in st.session_state:
    st.session_state.credits = 0

# URL Parameter auslesen (für erfolgreiche Zahlung)
query_params = st.query_params
if "pack" in query_params:
    pack = query_params["pack"]
    if pack == "1": st.session_state.credits += 1
    elif pack == "3": st.session_state.credits += 3
    elif pack == "10": st.session_state.credits += 10
    st.query_params.clear() # Parameter löschen, damit Refresh nicht neu zählt

# --- LOGO & HEADER ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=150) # Stelle sicher, dass logo.png im Ordner liegt
with col2:
    st.title("Amtsschimmel-Killer ⚖️")
    st.subheader("Bürokratendeutsch einfach verstehen und kontern.")

# --- MEHRSPRACHIGKEIT ---
lang = st.radio("Sprache / Language / Langue:", ["Deutsch", "English", "Türkçe", "Polski", "عربي"], horizontal=True)

# --- HAUPTBEREICH: PAKETE ---
st.write("---")
st.header("Wähle dein Paket")
st.write(f"**Dein aktuelles Guthaben: {st.session_state.credits} Dokument(e)**")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="package-box box-1">
        <h3>📄 <br>Amtsschimmel-Killer Analyse</h3>
        <p>1 Dokument</p>
        <div class="price-tag">3,99 €</div>
        <p class="no-abo">Einmalzahlung kein Abo</p>
        <a href="https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" class="stripe-button">Jetzt kaufen</a>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="package-box box-3">
        <h3>📦 <br>Amtsschimmel-Killer Spar-Paket</h3>
        <p>3 Dokumente</p>
        <div class="price-tag">9,99 €</div>
        <p class="no-abo">Einmalzahlung kein Abo</p>
        <a href="https://buy.stripe.com/8x228retRbj50paalq1gs03" class="stripe-button">Jetzt kaufen</a>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="package-box box-10">
        <h3>🚀 <br>Amtsschimmel-Killer Sorglos-Paket</h3>
        <p>10 Dokumente</p>
        <div class="price-tag">19,99 €</div>
        <p class="no-abo">Einmalzahlung kein Abo</p>
        <a href="https://stripe.com" class="stripe-button">Jetzt kaufen</a>
    </div>
    """, unsafe_allow_html=True)

# --- ANALYSE BEREICH ---
st.write("---")
if st.session_state.credits > 0:
    uploaded_file = st.file_uploader("Brief hier hochladen (PDF oder Bild)", type=["pdf", "jpg", "png"])
    if uploaded_file:
        if st.button("Dokument jetzt killen"):
            st.info("KI-Analyse läuft... (Hier OpenAI API Integration einfügen)")
            # st.session_state.credits -= 1
else:
    st.warning("Bitte wähle ein Paket oben aus, um Dokumente zu analysieren.")

# --- VORLAGEN ---
with st.expander("📄 Sofort-Vorlagen (Kostenlos)"):
    st.markdown("""
    **Fristverlängerung:**  
    Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

    **Widerspruch einlegen (Fristwahrend):**  
    Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

    **Akteneinsicht einfordern:**  
    Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
    """)

# --- FAQ ---
with st.expander("❓ FAQ - Häufige Fragen"):
    st.write("**Ist das ein Abonnement?**")
    st.write("Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.")
    st.write("**Wie sicher sind meine Dokumente?**")
    st.write("Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.")
    st.write("**Ersetzt die App eine Rechtsberatung?**")
    st.write("Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.")
    st.write("**Was passiert, wenn der Scan fehlschlägt?**")
    st.write("Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.")
    st.write("**Wie erreiche ich Elisabeth Reinecke?**")
    st.write("Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")

# --- IMPRESSUM & DATENSCHUTZ ---
st.write("---")
col_footer1, col_footer2 = st.columns(2)

with col_footer1:
    st.markdown("""
    **Impressum:**  
    Amtsschimmel-Killer  
    Betreiberin: Elisabeth Reinecke  
    Ringelsweide 9, 40223 Düsseldorf  
    Kontakt: Telefon: +49 211 15821329  
    E-Mail: amtsschimmel-killer@proton.me  
    Web: amtsschimmel-killer.streamlit.app  
    Haftung: Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
    """)

with col_footer2:
    st.markdown("""
    **Datenschutz:**  
    1. **Datenschutz auf einen Blick:** Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).  
    2. **Datenerfassung & Hosting:** Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst.  
    3. **Dokumentenverarbeitung:** Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) übertragen. Wir speichern keine Briefe.  
    4. **Zahlungsabwicklung (Stripe):** Bei Käufen werden Sie zu Stripe weitergeleitet. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.  
    5. **Ihre Rechte:** Sie haben das Recht auf Auskunft, Löschung und Sperrung. Kontakt: amtsschimmel-killer@proton.me.
    """)
