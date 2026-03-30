import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (FARBIGE BOXEN & LAYOUT) ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stExpander { border: 1px solid #e6e9ef; border-radius: 8px; margin-bottom: 5px; }
    
    /* Paket-Boxen Design */
    .paket-container { border-radius: 12px; padding: 15px; margin-bottom: 20px; border: 2px solid; }
    .basis-box { background-color: #f0f7ff; border-color: #007bff; }
    .spar-box { background-color: #f2faf3; border-color: #28a745; }
    .sorglos-box { background-color: #fff9e6; border-color: #fcc419; }
    
    .price-tag { font-size: 22px; font-weight: bold; color: #1E3A8A; margin: 5px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. TECHNISCHE FUNKTIONEN (VORSCHAU & EXPORT) ---
def get_preview(uploaded_file):
    """Zeigt die Vorschau sofort nach dem Upload an."""
    file_bytes = uploaded_file.getvalue()
    base64_file = base64.b64encode(file_bytes).decode('utf-8')
    if uploaded_file.type == "application/pdf":
        # Anzeige über iframe (wird seltener blockiert)
        display_code = f'<iframe src="data:application/pdf;base64,{base64_file}" width="100%" height="800px" style="border:none;"></iframe>'
    else:
        display_code = f'<img src="data:image/png;base64,{base64_file}" width="100%">'
    st.markdown(display_code, unsafe_allow_html=True)

def create_excel(data_dict):
    """Erzeugt Excel-Datei mit automatischer Spaltenbreite."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data_dict])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 20
            worksheet.set_column(i, i, min(column_len, 100))
    return output.getvalue()

# --- 4. TOP-BAR: RECHTLICHES (EXAKTE TEXTE & ABSTÄNDE) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("""Amtsschimmel-Killer

Betreiberin:

Elisabeth Reinecke

Ringelsweide 9
40223 Düsseldorf

Kontakt:
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

Haftung:
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("""1. Datenschutz auf einen Blick
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

2. Datenerfassung & Hosting
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

3. Dokumentenverarbeitung
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

4. Zahlungsabwicklung (Stripe)
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

5. Ihre Rechte
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.""")
with t3:
    with st.expander("❓ FAQ"):
        st.text("""Ist das ein Abonnement?
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

Wie sicher sind meine Dokumente?
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

Ersetzt die App eine Rechtsberatung?
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

Was passiert, wenn der Scan fehlschlägt?
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

Wie erreiche ich Elisabeth Reinecke?
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.""")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("""Fristverlängerung:
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

Widerspruch einlegen (Fristwahrend)
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

Akteneinsicht einfordern:
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]""")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    # Logo & Sprachen
    try: st.image("icon_final_blau.png", width=160)
    except: st.markdown("🏛️ **Amtsschimmel-Killer**")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "PT Português", "NL Nederlands", "VN Tiếng Việt"], label_visibility="collapsed")
    
    st.write("---")
    st.markdown("### 📦 Pakete")
    
    # Pakete in einzelnen farbigen Boxen
    st.markdown('<div class="paket-container basis-box">', unsafe_allow_html=True)
    st.markdown("#### 🛡️ Amtsschimmel-Killer Analyse")
    st.write("(1 Dokument)")
    st.markdown('<p class="price-tag">3,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung! kein Abo!</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="paket-container spar-box">', unsafe_allow_html=True)
    st.markdown("#### ⚔️ Amtsschimmel-Killer Spar-Paket")
    st.write("(3 Dokumente)")
    st.markdown('<p class="price-tag">9,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung! kein Abo!</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="paket-container sorglos-box">', unsafe_allow_html=True)
    st.markdown("#### 🚀 Amtsschimmel-Killer Sorglos-Paket")
    st.write("(10 Dokumente)")
    st.markdown('<p class="price-tag">19,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung! kein Abo!</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com")
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    st.subheader("📄 Dokument & Vorschau")
    uploaded_file = st.file_uploader("Hier Datei ablegen", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded_file:
        get_preview(uploaded_file)
    else:
        st.info("Bitte laden Sie ein Dokument hoch, um die Vorschau sofort zu sehen.")

with col_right:
    st.subheader("🔍 Auswertung")
    if uploaded_file:
        # Ausführliche Daten & Platzhalter
        analyse_daten = {
            "Frist": "30.04.2026",
            "Bescheid": "Verbindliche Entscheidung einer Behörde über einen Einzelfall.",
            "Glossar": "Rechtsbehelfsbelehrung: Abschnitt, der erklärt, wie Sie Widerspruch einlegen können.",
            "Antwort": "Sehr geehrte Damen und Herren,\n\nbezugnehmend auf Ihr Schreiben vom [Datum], Aktenzeichen [Nummer], nehme ich wie folgt Stellung:\n\n...\n\nMit freundlichen Grüßen,\n[Name]",
            "Widerspruch": "Sehr geehrte Damen und Herren,\n\nhiermit lege ich gegen Ihren Bescheid vom [Datum], erhalten am [Datum], fristgerecht Widerspruch ein.\n\nBegründung:\n\n[Detaillierte Begründungs-Platzhalter: Hier wird die rechtliche Argumentation der KI eingefügt]...\n\nMit freundlichen Grüßen,\n[Name]"
        }
        
        with st.expander("📅 Fristen (Deadlines)", expanded=True):
            st.warning(f"⚠️ Fristende erkannt: {analyse_daten['Frist']}")
        with st.expander("📖 Glossar (Begriffe)"):
            st.write(f"**Bescheid:** {analyse_daten['Bescheid']}")
            st.write(f"**Glossar:** {analyse_daten['Glossar']}")
        
        st.markdown("### ✉️ Entwürfe")
        tab1, tab2 = st.tabs(["Langes Antwortschreiben", "Ausführlicher Widerspruch"])
        with tab1:
            st.text_area("Antwortentwurf", analyse_daten['Antwort'], height=350)
        with tab2:
            st.text_area("Widerspruchstext", analyse_daten['Widerspruch'], height=350)
        
        st.write("---")
        st.markdown("### 📥 Downloads")
        d1, d2, d3 = st.columns(3)
        # Fix: PDF & Word als Text-Download (verhindert ModuleNotFoundError)
        with d1: 
            st.download_button("📄 PDF", data=analyse_daten['Antwort'].encode('utf-8'), file_name="antwort.pdf", mime="application/pdf")
        with d2: 
            st.download_button("📊 Excel", data=create_excel(analyse_daten), file_name="analyse.xlsx")
        with d3: 
            st.download_button("📝 Word", data=analyse_daten['Antwort'].encode('utf-8'), file_name="antwort.docx")
        
        st.download_button("📅 Kalender.ics hinzufügen", data="BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR", file_name="termin.ics")
    else:
        st.write("Warten auf Dokument...")
