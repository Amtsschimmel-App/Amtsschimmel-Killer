import streamlit as st

# --- 1. SEITENKONFIGURATION & LOGO ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🚀")

# Google Translate für sämtliche Sprachen
st.markdown("""
    <div id="google_translate_element" style="text-align:right; padding:5px;"></div>
    <script type="text/javascript">
        function googleTranslateElementInit() {
            new google.translate.TranslateElement({pageLanguage: 'de'}, 'google_translate_element');
        }
    </script>
    <script type="text/javascript" src="//://google.com"></script>
""", unsafe_allow_html=True)

# CSS für das exakte visuelle Design aus den Bildern
st.markdown("""
    <style>
    .package-box {
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
        text-align: center;
        min-height: 250px;
    }
    .price-text { font-size: 24px; font-weight: bold; margin: 10px 0; color: #1e1e1e; }
    .buy-button {
        background-color: #1a468c;
        color: white !important;
        padding: 10px;
        text-decoration: none;
        border-radius: 4px;
        display: block;
        font-weight: bold;
        font-size: 14px;
        margin-top: 10px;
    }
    .icon-style { font-size: 30px; margin-bottom: 5px; }
    /* Fix für Expander-Abstände oben */
    .stExpander { border: 1px solid #f0f2f6 !important; margin-bottom: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Header mit Logo-Icon
    st.markdown("### 🚀 Amtsschimmel-Killer")

    # --- 2. ZUSAMMENGEKLAPPTE LEISTEN (Top Navigation) ---
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
    
    with col_nav1:
        with st.expander("⚖️ Impressum"):
            st.markdown("""
            **Amtsschimmel-Killer**  
            **Betreiberin:**  
            Elisabeth Reinecke  
            Ringelsweide 9  
            40223 Düsseldorf  
            **Kontakt:**  
            Telefon: +49 211 15821329  
            E-Mail: amtsschimmel-killer@proton.me  
            Web: amtsschimmel-killer.streamlit.app  
            **Haftung:**  
            Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
            """)

    with col_nav2:
        with st.expander("🛡️ Datenschutz"):
            st.markdown("""
            **1. Datenschutz auf einen Blick**  
            Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).  
            **2. Datenerfassung & Hosting**  
            Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.  
            **3. Dokumentenverarbeitung**  
            Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.  
            **4. Zahlungsabwicklung (Stripe)**  
            Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.  
            **5. Ihre Rechte**  
            Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
            """)

    with col_nav3:
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

    with col_nav4:
        with st.expander("📝 Vorlagen"):
            st.markdown("""
            **Fristverlängerung:**  
            Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]  
            
            **Widerspruch einlegen (Fristwahrend):**  
            Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]  
            
            **Akteneinsicht einfordern:**  
            Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
            """)

    st.divider()

    # --- 3. HAUPTLAYOUT (Drei Spalten wie im Bild) ---
    col_packs, col_upload, col_result = st.columns([1, 1.2, 1.2])

    # SPALTE LINKS: Pakete
    with col_packs:
        st.markdown(f"""
            <div class="package-box" style="background-color: #f0f7ff; border-left: 5px solid #2196F3;">
                <div class="icon-style">📄</div>
                <div style="font-weight:bold; font-size:14px;">Amtsschimmel-Killer Analyse</div>
                <div style="font-size:11px;">(1 Dokument)</div>
                <div class="price-text">3,99 €</div>
                <div style="font-size:11px;">Einmalzahlung kein Abo</div>
                <a href="https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" class="buy-button">JETZT KAUFEN</a>
            </div>
            <div class="package-box" style="background-color: #f6fff0; border-left: 5px solid #4CAF50;">
                <div class="icon-style">📦</div>
                <div style="font-weight:bold; font-size:14px;">Amtsschimmel-Killer Spar-Paket</div>
                <div style="font-size:11px;">(3 Dokumente)</div>
                <div class="price-text">9,99 €</div>
                <div style="font-size:11px;">Einmalzahlung kein Abo</div>
                <a href="https://buy.stripe.com/8x228retRbj50paalq1gs03" class="buy-button">JETZT KAUFEN</a>
            </div>
            <div class="package-box" style="background-color: #fffbf0; border-left: 5px solid #FF9800;">
                <div class="icon-style">👑</div>
                <div style="font-weight:bold; font-size:14px;">Amtsschimmel-Killer Sorglos-Paket</div>
                <div style="font-size:11px;">(10 Dokumente)</div>
                <div class="price-text">19,99 €</div>
                <div style="font-size:11px;">Einmalzahlung kein Abo</div>
                <a href="https://stripe.com" class="buy-button">JETZT KAUFEN</a>
            </div>
            """, unsafe_allow_html=True)

    # SPALTE MITTE: Dokument Upload
    with col_upload:
        st.subheader("Dokument")
        st.file_uploader("Datei hier hochladen (PDF, JPG, PNG)", type=["pdf", "jpg", "png", "jpeg"])
        st.caption("TLS-verschlüsselte Schnittstelle zu OpenAI (USA)")

    # SPALTE RECHTS: Auswertung
    with col_result:
        st.subheader("Auswertung")
        st.info("Laden Sie ein Dokument hoch, um die KI-Analyse zu starten.")
        st.divider()
        st.subheader("Downloads & Kalender")
        st.button("📄 PDF Export", use_container_width=True)
        st.button("📅 Termin speichern (iCal)", use_container_width=True)

if __name__ == "__main__":
    main()
