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

# --- 3. EXPORT FUNKTIONEN (EXCEL PRO, PDF & WORD DUMMIES) ---
def create_excel_pro(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(data)
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        # Automatisches Anpassen der Spaltenbreite
        for i, col in enumerate(df.columns):
            column_len = df[col].astype(str).str.len().max()
            column_len = max(column_len, len(col)) + 2
            worksheet.set_column(i, i, min(column_len, 100))
    return output.getvalue()

def get_pdf_display_fixed(uploaded_file):
    # Fix: Sofortige Anzeige nach Upload
    file_bytes = uploaded_file.getvalue()
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    
    if uploaded_file.type == "application/pdf":
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    else:
        pdf_display = f'<img src="data:image/png;base64,{base64_pdf}" width="100%">'
    
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 4. TOP-BAR: RECHTLICHES (EXAKTE TEXTE & ABSTÄNDE) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("""Amtsschimmel-Killer\n\nBetreiberin:\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("""1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.\n\n4. Zahlungsabwicklung (Stripe)\nBei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.\n\n5. Ihre Rechte\nSie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.""")
with t3:
    with st.expander("❓ FAQ"):
        st.text("""Ist das ein Abonnement?\nNein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.\nWie sicher sind meine Dokumente?\nIhre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.\nErsetzt die App eine Rechtsberatung?\nNein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.\nWas passiert, wenn der Scan fehlschlägt?\nEin Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.\nWie erreiche ich Elisabeth Reinecke?\nNutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.""")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("""Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]\n\nWiderspruch einlegen (Fristwahrend)\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]\n\nAkteneinsicht einfordern:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]""")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    # 3. Logo
    try: st.image("icon_final_blau.png", width=160)
    except: st.markdown("🏛️ **Amtsschimmel-Killer**")
    
    # 2. Sprachen
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano"], label_visibility="collapsed")
    
    st.write("---")
    st.markdown("### 📦 Pakete")
    # 1. & 4. Pakete mit Stripe Codes
    with st.container(border=True):
        st.markdown("### 🛡️ Amtsschimmel-Killer")
        st.write("1. Paket: 3,99 € (1 Scan)")
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    with st.container(border=True):
        st.markdown("### ⚔️ Amtsschimmel-Killer")
        st.write("2. Paket: 9,99 € (3 Scans)")
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    with st.container(border=True):
        st.markdown("### 🚀 Amtsschimmel-Killer")
        st.write("3. Paket: 19,99 € (10 Scans)")
        st.link_button("Jetzt kaufen", "https://buy.stripe.com")

with col_mid:
    st.subheader("📄 Dokument & Vorschau")
    uploaded_file = st.file_uploader("Upload", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded_file:
        get_pdf_display_fixed(uploaded_file)

with col_right:
    st.subheader("🔍 Analyse-Ergebnisse")
    if uploaded_file:
        # 2. Fristen & 3. Glossar
        with st.expander("📅 Fristen (Deadlines)", expanded=True):
            st.warning("⚠️ Fristende: [Datum aus KI extrahieren]")
        with st.expander("📖 Glossar (Begriffserklärung)"):
            st.info("Rechtsbehelfsbelehrung: Erklärt, wie man gegen den Bescheid vorgeht.")
        
        # 4. & 5. Antwort & Widerspruch
        st.markdown("### ✉️ Entwürfe")
        tab1, tab2 = st.tabs(["Langes Antwortschreiben", "Ausführlicher Widerspruch"])
        with tab1:
            st.text_area("Antwortentwurf", "Sehr geehrte Damen und Herren,\n\n[Ausführlicher KI-Text mit Platzhaltern]...\n\nMit freundlichen Grüßen,\n[Name]", height=200)
        with tab2:
            st.text_area("Widerspruchsentwurf", "Sehr geehrte Damen und Herren,\n\nhiermit lege ich gegen den Bescheid vom [Datum] Widerspruch ein...\n\nMit freundlichen Grüßen,\n[Name]", height=200)
        
        # Exporte
        st.write("---")
        st.markdown("### 📥 Downloads")
        c1, c2, c3 = st.columns(3)
        with c1: st.button("📄 PDF")
        with c2: st.button("📊 Excel")
        with c3: st.button("📝 Word")
        st.write("📅 Kalender.ico hinzufügen")
    else:
        st.info("Bitte Dokument hochladen.")
