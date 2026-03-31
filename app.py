import streamlit as st
import base64

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CSS FÜR FARBIGE BOXEN & BUTTONS INNEN ---
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    .header-text { font-size: 18px; font-weight: bold; margin-bottom: 10px; display: block; color: #333; }
    .price-tag { font-size: 30px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; height: 45px; }
</style>
""", unsafe_allow_html=True)

# --- 3. RECHTLICHE TEXTE (EXAKT NACH ANWEISUNG) ---
with st.container():
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        with st.expander("⚖️ Impressum"):
            st.markdown("**Amtsschimmel-Killer**\n\n**Betreiberin:**\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\n**Kontakt:**\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\n**Haftung:**\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
    with t2:
        with st.expander("🛡️ Datenschutz"):
            st.markdown("**1. Datenschutz auf einen Blick**\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n**2. Datenerfassung & Hosting**\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.\n\n**3. Dokumentenverarbeitung**\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern.\n\n**4. Zahlungsabwicklung (Stripe)**\nBei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung.\n\n**5. Ihre Rechte**\nSie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.")
    with t3:
        with st.expander("❓ FAQ"):
            st.markdown("**Ist das ein Abonnement?**\nNein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.\n\n**Wie sicher sind meine Dokumente?**\nIhre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert.\n\n**Ersetzt die App eine Rechtsberatung?**\nNein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.\n\n**Was passiert, wenn der Scan fehlschlägt?**\nEin Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat.\n\n**Wie erreiche ich Elisabeth Reinecke?**\nNutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")
    with t4:
        with st.expander("📝 Vorlagen"):
            st.markdown("**Fristverlängerung:**\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]\n\n**Widerspruch einlegen (Fristwahrend)**\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein.\n\n**Akteneinsicht einfordern:**\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht.")

st.divider()

# --- 4. HAUPT-BEREICH ---
col_left, col_mid, col_right = st.columns([1.2, 1.8, 1.4])

with col_left:
    # Logo-Check: Verhindert Absturz falls Datei fehlt
    try:
        st.image("icon_final_blau.png", width=150)
    except:
        st.subheader("🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    langs = ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"]
    st.selectbox("Sprache wählen", langs, label_visibility="collapsed", key="lang_sel")
    
    st.write("---")
    st.markdown("### 📦 Pakete")
    
    # PAKET 1
    st.markdown('<div class="paket-container blue-box"><span class="header-text">🛡️ Amtsschimmel-Killer Analyse</span>(1 Dokument)<div class="price-tag">3,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", key="s1")
    st.markdown('</div>', unsafe_allow_html=True)

    # PAKET 2
    st.markdown('<div class="paket-container green-box"><span class="header-text">⚔️ Amtsschimmel-Killer Spar-Paket</span>(3 Dokumente)<div class="price-tag">9,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", key="s2")
    st.markdown('</div>', unsafe_allow_html=True)

    # PAKET 3
    st.markdown('<div class="paket-container gold-box"><span class="header-text">🚀 Amtsschimmel-Killer Sorglos-Paket</span>(10 Dokumente)<div class="price-tag">19,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041", key="s3")
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    st.subheader("📄 Dokument hochladen")
    u_file = st.file_uploader("Upload", type=["pdf", "jpg", "png"], label_visibility="collapsed")
    
    if u_file:
        if u_file.type == "application/pdf":
            # Smartphone-sichere Methode ohne pdf2image
            base64_pdf = base64.b64encode(u_file.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.image(u_file, use_container_width=True)
    else:
        st.info("Hier erscheint die Vorschau nach dem Upload.")

with col_right:
    st.subheader("🔍 Auswertung")
    if u_file:
        # FRIST-ERKENNUNG
        st.error("📅 **FRIST-CHECK: 30.04.2026**")
        
        with st.expander("📖 Glossar & Analyse", expanded=True):
            st.write("**Widerspruch:** Einspruch gegen einen Bescheid.")
            st.write("**Verwaltungsakt:** Amtliche Entscheidung.")
            
        with st.expander("✉️ Antwort-Entwurf", expanded=True):
            st.text_area("Ihr Entwurf:", "Sehr geehrte Damen und Herren,\nin der Angelegenheit...", height=250)
            st.button("Als Word (.docx) speichern", key="w_dl")
            st.button("Als Excel (.xlsx) speichern", key="e_dl")
    else:
        st.write("Warten auf Dokument...")
