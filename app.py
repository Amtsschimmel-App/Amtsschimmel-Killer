import streamlit as st

# --- 1. GRUNDKONFIGURATION & LOGO ---
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="🚀", layout="wide")

# Google Translate Integration für "sämtliche Sprachen"
st.markdown("""
    <div id="google_translate_element" style="text-align:right; padding:10px;"></div>
    <script type="text/javascript">
        function googleTranslateElementInit() {
            new google.translate.TranslateElement({pageLanguage: 'de'}, 'google_translate_element');
        }
    </script>
    <script type="text/javascript" src="//://google.com"></script>
""", unsafe_allow_html=True)

# Styling für bunte Boxen
st.markdown("""
    <style>
    .package-box {
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        color: #1E1E1E;
        min-height: 280px;
    }
    .price { font-size: 28px; font-weight: bold; margin: 10px 0; }
    .stripe-btn {
        background-color: #000000;
        color: white !important;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 8px;
        display: inline-block;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Admin-Check via URL
    is_admin = st.query_params.get("admin") == "GeheimAmt2024!"

    # Header
    st.title("🚀 REBOOT: AMTSSCHIMMEL-KILLER")
    st.markdown("### Protokoll: Elisabeth Reinecke")
    st.divider()

    # --- 2. PAKETE (Bunte Boxen) ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="package-box" style="background-color: #FFEBEE; border: 3px solid #EF5350;">
                <h3>🔍 Amtsschimmel-Killer Analyse</h3>
                <p>(1 Dokument)</p>
                <div class="price">3,99 €</div>
                <p><b>Einmalzahlung kein Abo</b></p>
                <a href="https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" class="stripe-btn">JETZT KAUFEN</a>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="package-box" style="background-color: #E8F5E9; border: 3px solid #66BB6A;">
                <h3>📦 Amtsschimmel-Killer Spar-Paket</h3>
                <p>(3 Dokumente)</p>
                <div class="price">9,99 €</div>
                <p><b>Einmalzahlung kein Abo</b></p>
                <a href="https://buy.stripe.com/8x228retRbj50paalq1gs03" class="stripe-btn">JETZT KAUFEN</a>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="package-box" style="background-color: #E3F2FD; border: 3px solid #42A5F5;">
                <h3>👑 Amtsschimmel-Killer Sorglos-Paket</h3>
                <p>(10 Dokumente)</p>
                <div class="price">19,99 €</div>
                <p><b>Einmalzahlung kein Abo</b></p>
                <a href="https://stripe.com" class="stripe-btn">JETZT KAUFEN</a>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- 3. VORLAGEN (Exakte Texte) ---
    st.subheader("Vorlagen:")
    st.markdown("""
    **Fristverlängerung:**  
    Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

    **Widerspruch einlegen (Fristwahrend):**  
    Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

    **Akteneinsicht einfordern:**  
    Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
    """)

    # --- 4. FAQ (Exakte Texte) ---
    st.divider()
    st.subheader("FAQ")
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

    # --- 5. RECHTLICHES (Exakte Texte & Abstände) ---
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **Impressum:**  
        Amtsschimmel-Killer  
        Betreiberin: Elisabeth Reinecke  
        Ringelsweide 9  
        40223 Düsseldorf  
        
        **Kontakt:**  
        Telefon: +49 211 15821329  
        E-Mail: amtsschimmel-killer@proton.me  
        Web: amtsschimmel-killer.streamlit.app  
        
        **Haftung:**  
        Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        """)
    
    with col_b:
        st.markdown("""
        **Datenschutz:**  
        1. Datenschutz auf einen Blick  
        Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).  
        
        2. Datenerfassung & Hosting  
        Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.  
        
        3. Dokumentenverarbeitung  
        Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern.  
        
        4. Zahlungsabwicklung (Stripe)  
        Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung.  
        
        5. Ihre Rechte  
        Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
        """)

    if is_admin:
        st.sidebar.success("🔑 Admin-Status: Elisabeth erkannt")

if __name__ == "__main__":
    main()
