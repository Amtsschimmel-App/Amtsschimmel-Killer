import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stExpander { border: 1px solid #e6e9ef; border-radius: 8px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN ---
def create_excel_pro(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(data)
        df.to_excel(writer, index=False, sheet_name='Detaillierte_Analyse')
        worksheet = writer.sheets['Detaillierte_Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 100)
    return output.getvalue()

def get_pdf_display_fixed(uploaded_file):
    base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    pdf_display = f'''
    <div style="text-align:center;">
        <object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="600px">
            <embed src="data:application/pdf;base64,{base64_pdf}" type="application/pdf" />
        </object>
        <br><a href="data:application/pdf;base64,{base64_pdf}" download="dokument.pdf">PDF-Vorschau wird blockiert? Hier klicken zum Herunterladen</a>
    </div>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 4. TOP-BAR: RECHTLICHES (EXAKTE TEXTE & ABSTÄNDE) ---
t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum"):
        st.text("""
Amtsschimmel-Killer

Betreiberin:

Elisabeth Reinecke

Ringelsweide 9
40223 Düsseldorf

Kontakt:
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

Haftung:
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        """)

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("""
1. Datenschutz auf einen Blick
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

2. Datenerfassung & Hosting
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

3. Dokumentenverarbeitung
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

4. Zahlungsabwicklung (Stripe)
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

5. Ihre Rechte
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
        """)

with t3:
    with st.expander("❓ FAQ"):
        st.text("""
Ist das ein Abonnement?
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

Wie sicher sind meine Dokumente?
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

Ersetzt die App eine Rechtsberatung?
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

Was passiert, wenn der Scan fehlschlägt?
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

Wie erreiche ich Elisabeth Reinecke?
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
        """)

with t4:
    with st.expander("📝 Vorlagen"):
        st.text("""
Fristverlängerung:
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

Widerspruch einlegen (Fristwahrend)
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

Akteneinsicht einfordern:
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
        """)

st.divider()

# --- 5. HAUPT-LAYOUT (LOGO | PAKETE | UPLOAD | ANALYSE) ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    # 3. Logo beibehalten
    try:
        st.image("icon_final_blau.png", width=180)
    except:
        st.title("🏛️ Amtsschimmel-Killer")
    
    # 2. Sprachen beibehalten
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية"], label_visibility="collapsed")
    
    st.write("---")
    st.markdown("### 📦 Pakete")

    # 1. Pakete beibehalten & 4. Stripe-Codes
    
    # Paket 1: 3,99
    with st.container(border=True):
        st.markdown("#### 🛡️ Amtsschimmel-Killer")
        st.markdown("**Basis-Check (1 Scan)**")
        st.markdown("### 3,99 €")
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")

    # Paket 2: 9,99
    with st.container(border=True):
        st.markdown("#### ⚔️ Amtsschimmel-Killer")
        st.markdown("**Standard-Paket (3 Scans)**")
        st.markdown("### 9,99 €")
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")

    # Paket 3: 19,99
    with st.container(border=True):
        st.markdown("#### 🚀 Amtsschimmel-Killer")
        st.markdown("**Pro-Flat (10 Scans)**")
        st.markdown("### 19,99 €")
        st.link_button("Jetzt kaufen", "https://buy.stripe.com")

with col_mid:
    st.subheader("📄 Dokumenten-Upload")
    uploaded_file = st.file_uploader("Datei hier hochladen", type=["pdf", "jpg", "jpeg", "png"])
    if uploaded_file:
        get_pdf_display_fixed(uploaded_file)

with col_right:
    st.subheader("🔍 Analyse")
    st.info("Bitte laden Sie ein Dokument hoch.")
