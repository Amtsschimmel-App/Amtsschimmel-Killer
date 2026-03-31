import streamlit as st

# --- 1. SEITENKONFIGURATION & LOGO ---
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="⚖️", layout="wide")

# Styling für die bunten Boxen
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .package-card {
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #ddd;
        text-align: center;
        margin-bottom: 10px;
    }
    .box-analyse { background-color: #E3F2FD; border-color: #2196F3; }
    .box-spar { background-color: #E8F5E9; border-color: #4CAF50; }
    .box-sorglos { background-color: #FFF3E0; border-color: #FF9800; }
    .price { font-size: 26px; font-weight: bold; color: #333; margin: 10px 0; }
    .no-abo { color: #d32f2f; font-weight: bold; font-size: 0.9em; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# Logo (Platzhalter für dein Logo)
st.image("https://placeholder.com", width=150) 
st.title("Amtsschimmel-Killer")

# --- 2. MEHRSPRACHIGKEIT ---
st.write("🌍 **Sprache wählen / Choose Language / Dil Seçin / Wybierz język / اختر اللغة**")
lang = st.radio("", ["Deutsch", "English", "Türkçe", "Polski", "عربي"], horizontal=True, label_visibility="collapsed")

# --- 3. CREDIT-ZÄHLER LOGIK ---
if 'credits' not in st.session_state:
    st.session_state.credits = 0

# Verrechnung der URL-Parameter nach Stripe-Rückkehr
params = st.query_params
if "pack" in params:
    if params["pack"] == "1": st.session_state.credits += 1
    elif params["pack"] == "3": st.session_state.credits += 3
    elif params["pack"] == "10": st.session_state.credits += 10
    st.query_params.clear()

st.info(f"Aktuelles Guthaben: {st.session_state.credits} Dokument(e)")

# --- 4. PAKETE (BUNTE BOXEN) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="package-card box-analyse">', unsafe_allow_html=True)
    st.markdown("### 📄 <br>Amtsschimmel-Killer Analyse")
    st.markdown("<p>(1 Dokument)</p>", unsafe_allow_html=True)
    st.markdown('<div class="price">3,99 €</div>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung kein Abo</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="package-card box-spar">', unsafe_allow_html=True)
    st.markdown("### 📦 <br>Amtsschimmel-Killer Spar-Paket")
    st.markdown("<p>(3 Dokumente)</p>", unsafe_allow_html=True)
    st.markdown('<div class="price">9,99 €</div>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung kein Abo</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="package-card box-sorglos">', unsafe_allow_html=True)
    st.markdown("### 🚀 <br>Amtsschimmel-Killer Sorglos-Paket")
    st.markdown("<p>(10 Dokumente)</p>", unsafe_allow_html=True)
    st.markdown('<div class="price">19,99 €</div>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung kein Abo</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://stripe.com")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. HAUPTFUNKTION ---
st.divider()
if st.session_state.credits > 0:
    uploaded_file = st.file_uploader("Laden Sie hier Ihren Behördenbrief hoch", type=["pdf", "jpg", "png", "jpeg"])
    if uploaded_file and st.button("Dokument analysieren"):
        st.success("Analyse gestartet...")
        # Hier folgt dein OpenAI-Code
else:
    st.warning("Bitte erwerben Sie ein Paket, um die Analyse zu starten.")

# --- 6. VORLAGEN ---
with st.expander("📋 Vorlagen"):
    st.markdown("""
    **Fristverlängerung:**  
    Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

    **Widerspruch einlegen (Fristwahrend):**  
    Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

    **Akteneinsicht einfordern:**  
    Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
    """)

# --- 7. FAQ ---
with st.expander("❓ FAQ"):
    st.markdown("""
    **Ist das ein Abonnement?**  
    Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

    **Wie sicher sind meine Dokumente?**  
    Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

    **Ersetzt die App eine Rechtsberatung?**  
    Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

    **Was passiert, wenn der Scan fehlschlägt?**  
    Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

    **Wie erreiche ich Elisabeth Reinecke?**  
    Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
    """)

# --- 8. IMPRESSUM & DATENSCHUTZ ---
st.divider()
c_inf1, c_inf2 = st.columns(2)
with c_inf1:
    st.markdown("""
    **Impressum:**  
    Amtsschimmel-Killer  
    Betreiberin: Elisabeth Reinecke  
    Ringelsweide 9, 40223 Düsseldorf  
    Kontakt: Telefon: +49 211 15821329 | E-Mail: amtsschimmel-killer@proton.me  
    Web: amtsschimmel-killer.streamlit.app  
    Haftung: Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
    """)

with c_inf2:
    st.markdown("""
    **Datenschutz:**  
    1. **Datenschutz auf einen Blick:** Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).  
    2. **Datenerfassung & Hosting:** Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.  
    3. **Dokumentenverarbeitung:** Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern.  
    4. **Zahlungsabwicklung (Stripe):** Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung.  
    5. **Ihre Rechte:** Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
    """)
