import streamlit as st

# --- 1. KONFIGURATION & DESIGN ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🚀")

# Google Translate für sämtliche Sprachen
st.markdown("""
    <div id="google_translate_element" style="text-align:right; padding:10px;"></div>
    <script type="text/javascript">
        function googleTranslateElementInit() {
            new google.translate.TranslateElement({pageLanguage: 'de'}, 'google_translate_element');
        }
    </script>
    <script type="text/javascript" src="//://google.com"></script>
""", unsafe_allow_html=True)

# CSS für bunte Boxen und exaktes Layout (basierend auf deinem Bild)
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: bold; }
    
    .package-box {
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .price-text { font-size: 26px; font-weight: bold; margin: 10px 0; }
    .buy-button {
        background-color: #1c4587;
        color: white !important;
        padding: 10px 20px;
        text-decoration: none;
        border-radius: 5px;
        display: block;
        font-weight: bold;
        margin-top: 10px;
    }
    .icon-style { font-size: 30px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Header / Logo Platzhalter
    st.write("### 🚀 Amtsschimmel-Killer")
    
    # Navigation über Tabs (wie im Bild oben sichtbar)
    tab_home, tab_datenschutz, tab_faq, tab_vorlagen = st.tabs([
        "🏠 Startseite", "⚖️ Datenschutz", "❓ FAQ", "📝 Vorlagen"
    ])

    with tab_home:
        # Das 3-Spalten Layout aus deinem Screenshot
        col_packs, col_upload, col_result = st.columns([1, 1.2, 1.2])

        # SPALTE 1: Pakete (Bunt & mit Icons)
        with col_packs:
            # Paket 1
            st.markdown(f"""
                <div class="package-box" style="background-color: #f0f7ff; border-top: 5px solid #2196F3;">
                    <div class="icon-style">📄</div>
                    <div style="font-weight:bold;">Amtsschimmel-Killer Analyse</div>
                    <div style="font-size:12px;">(1 Dokument)</div>
                    <div class="price-text">3,99 €</div>
                    <div style="font-size:11px;">Einmalzahlung kein Abo</div>
                    <a href="https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" class="buy-button">JETZT KAUFEN</a>
                </div>
                """, unsafe_allow_html=True)

            # Paket 2
            st.markdown(f"""
                <div class="package-box" style="background-color: #f6fff0; border-top: 5px solid #4CAF50;">
                    <div class="icon-style">📦</div>
                    <div style="font-weight:bold;">Amtsschimmel-Killer Spar-Paket</div>
                    <div style="font-size:12px;">(3 Dokumente)</div>
                    <div class="price-text">9,99 €</div>
                    <div style="font-size:11px;">Einmalzahlung kein Abo</div>
                    <a href="https://buy.stripe.com/8x228retRbj50paalq1gs03" class="buy-button">JETZT KAUFEN</a>
                </div>
                """, unsafe_allow_html=True)

            # Paket 3
            st.markdown(f"""
                <div class="package-box" style="background-color: #fffbf0; border-top: 5px solid #FF9800;">
                    <div class="icon-style">👑</div>
                    <div style="font-weight:bold;">Amtsschimmel-Killer Sorglos-Paket</div>
                    <div style="font-size:12px;">(10 Dokumente)</div>
                    <div class="price-text">19,99 €</div>
                    <div style="font-size:11px;">Einmalzahlung kein Abo</div>
                    <a href="https://stripe.com" class="buy-button">JETZT KAUFEN</a>
                </div>
                """, unsafe_allow_html=True)

        # SPALTE 2: Dokument Upload
        with col_upload:
            st.subheader("📄 Dokument")
            st.file_uploader("Brief hier hochladen...", type=["pdf", "jpg", "jpeg", "png"])
            st.info("Laden Sie Ihr Dokument hoch, um die Analyse zu starten.")

        # SPALTE 3: Auswertung
        with col_result:
            st.subheader("🔍 Auswertung")
            st.error("Noch kein Dokument zur Analyse gefunden.")
            
            st.markdown("---")
            st.subheader("📥 Downloads & Kalender")
            st.button("📄 PDF Export")
            st.button("📅 Termin speichern")

    # --- TAB: DATENSCHUTZ (Exakte Texte) ---
    with tab_datenschutz:
        st.markdown("""
        ## Datenschutz
        
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

    # --- TAB: FAQ (Exakte Texte) ---
    with tab_faq:
        st.markdown("""
        ## FAQ
        
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

    # --- TAB: VORLAGEN (Exakte Texte) ---
    with tab_vorlagen:
        st.markdown("""
        ## Vorlagen
        
        **Fristverlängerung:**
        Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

        **Widerspruch einlegen (Fristwahrend)**
        Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

        **Akteneinsicht einfordern:**
        Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
        """)

    # --- FOOTER / IMPRESSUM ---
    st.divider()
    st.markdown("""
    **Impressum:**
    Amtsschimmel-Killer | Betreiberin: Elisabeth Reinecke | Ringelsweide 9, 40223 Düsseldorf
    Kontakt: Telefon: +49 211 15821329 | E-Mail: amtsschimmel-killer@proton.me | Web: amtsschimmel-killer.streamlit.app
    Haftung: Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
    """)

if __name__ == "__main__":
    main()
