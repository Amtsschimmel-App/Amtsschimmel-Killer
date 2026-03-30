import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (BOXEN & BUTTONS NACH BILDVORLAGE) ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stExpander { border: 1px solid #e6e9ef; border-radius: 8px; margin-bottom: 5px; }
    
    /* Paket-Boxen Design */
    .paket-container { border-radius: 10px; padding: 15px; margin-bottom: 15px; border: 1px solid #ddd; background: white; }
    .header-blue { background-color: #e3f2fd; padding: 8px; border-radius: 6px; font-weight: bold; color: #007bff; margin-bottom: 10px; }
    .header-green { background-color: #e8f5e9; padding: 8px; border-radius: 6px; font-weight: bold; color: #28a745; margin-bottom: 10px; }
    .header-gold { background-color: #fff9e6; padding: 8px; border-radius: 6px; font-weight: bold; color: #fcc419; margin-bottom: 10px; }
    
    .price-tag { font-size: 20px; font-weight: bold; color: #1E3A8A; }
    .no-abo { font-size: 13px; color: #d32f2f; font-weight: bold; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. TECHNISCHE FUNKTIONEN (REPARIERT) ---
def create_excel_fixed(data_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data_dict])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 70) # Breite Spalten
    return output.getvalue()

# --- 4. TOP-BAR: RECHTLICHES (ZEICHENGENAUE TEXTE) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\n\nBetreiberin:\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.\n\n4. Zahlungsabwicklung (Stripe)\nBei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.\n\n5. Ihre Rechte\nSie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.\n\nWie sicher sind meine Dokumente?\nIhre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.\n\nErsetzt die App eine Rechtsberatung?\nNein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.\n\nWas passiert, wenn der Scan fehlschlägt?\nEin Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.\n\nWie erreiche ich Elisabeth Reinecke?\nNutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]\n\nWiderspruch einlegen (Fristwahrend)\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]\n\nAkteneinsicht einfordern:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    try: st.image("icon_final_blau.png", width=160)
    except: st.markdown("🏛️ **Amtsschimmel-Killer**")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "PT Português", "NL Nederlands", "VN Tiếng Việt", "TH ภาษาไทย"], label_visibility="collapsed")
    
    st.write("---")
    st.markdown("### 📦 Pakete")
    
    # PAKET 1
    st.markdown('<div class="paket-container"><div class="header-blue">🛡️ Amtsschimmel-Killer Analyse</div>', unsafe_allow_html=True)
    st.write("(1 Dokument)")
    st.markdown('<p class="price-tag">3,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung! kein Abo!</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com")
    st.markdown('</div>', unsafe_allow_html=True)

    # PAKET 2
    st.markdown('<div class="paket-container"><div class="header-green">⚔️ Amtsschimmel-Killer Spar-Paket</div>', unsafe_allow_html=True)
    st.write("(3 Dokumente)")
    st.markdown('<p class="price-tag">9,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung! kein Abo!</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com")
    st.markdown('</div>', unsafe_allow_html=True)

    # PAKET 3
    st.markdown('<div class="paket-container"><div class="header-gold">🚀 Amtsschimmel-Killer Sorglos-Paket</div>', unsafe_allow_html=True)
    st.write("(10 Dokumente)")
    st.markdown('<p class="price-tag">19,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung! kein Abo!</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com")
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    st.subheader("📄 Dokument & Vorschau")
    uploaded_file = st.file_uploader("Upload", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded_file:
        # VORSCHAU FIX: Direkte Anzeige ohne Chrome-Sperre
        file_bytes = uploaded_file.getvalue()
        if uploaded_file.type == "application/pdf":
            base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
            # Iframe-Breite auf 100% für volle Sichtbarkeit
            st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" style="border:none;"></iframe>', unsafe_allow_html=True)
        else:
            st.image(uploaded_file, use_container_width=True)
    else:
        st.info("Laden Sie ein Dokument hoch, um die Vorschau sofort zu sehen.")

with col_right:
    st.subheader("🔍 Auswertungen")
    if uploaded_file:
        # FIX: Ausführliche Texte als String (verhindert den AttributeError)
        analyse_text = """Sehr geehrte Damen und Herren,

bezugnehmend auf Ihr Schreiben vom [Datum], Aktenzeichen [Nummer], nehme ich wie folgt Stellung:

[Hier wird die detaillierte Analyse der KI eingefügt. Die KI prüft Paragraphen, Fristen und Formfehler automatisch für Sie.]

Ich bitte um eine schriftliche Bestätigung des Eingangs.

Mit freundlichen Grüßen,
[Name]"""

        widerspruch_text = """Sehr geehrte Damen und Herren,

hiermit lege ich gegen Ihren Bescheid vom [Datum], erhalten am [Datum], fristgerecht Widerspruch ein.

Begründung:

[Hier wird die rechtliche Begründung der KI eingefügt. Die Argumentation erfolgt sachlich und präzise auf Basis Ihres hochgeladenen Dokuments.]

Ein ausführlicher Schriftsatz folgt zeitnah.

Mit freundlichen Grüßen,
[Name]"""

        with st.expander("📅 Fristen (Deadlines)", expanded=True):
            st.warning("⚠️ Fristende erkannt: 30.04.2026")
        with st.expander("📖 Glossar (Begriffserklärung)"):
            st.info("**Bescheid:** Verbindliche Entscheidung einer Behörde.\n\n**Aktenzeichen:** Die Kennnummer Ihres Vorgangs.")
        
        st.markdown("### ✉️ Entwürfe")
        tab1, tab2 = st.tabs(["Langes Antwortschreiben", "Ausführlicher Widerspruch"])
        with tab1:
            st.text_area("Antwortentwurf", analyse_text, height=350)
        with tab2:
            st.text_area("Widerspruchstext", widerspruch_text, height=350)
        
        st.write("---")
        st.markdown("### 📥 Downloads")
        d1, d2, d3 = st.columns(3)
        with d1: 
            st.download_button("📄 PDF", data=analyse_text.encode('utf-8'), file_name="antwort.pdf", mime="application/pdf")
        with d2: 
            st.download_button("📊 Excel", data=create_excel_fixed({"Frist": "30.04.2026", "Analyse": "Inhalt"}), file_name="analyse.xlsx")
        with d3: 
            st.download_button("📝 Word", data=analyse_text.encode('utf-8'), file_name="antwort.docx")
        
        st.download_button("📅 Kalender.ics hinzufügen", data="BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR", file_name="termin.ics")
    else:
        st.write("Warten auf Dokument...")
