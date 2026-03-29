import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# Custom CSS für die Paketboxen und Buttons
st.markdown("""
<style>
    .pkg-box {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        text-align: center;
        margin-bottom: 15px;
        min-height: 250px;
    }
    .pkg-name { font-weight: bold; font-size: 1.1em; color: #2c3e50; min-height: 50px; }
    .pkg-price { font-size: 26px; font-weight: bold; color: #1f77b4; margin: 10px 0; }
    .pkg-info { font-size: 0.85em; font-weight: bold; color: #d35400; text-transform: uppercase; margin-bottom: 15px; }
    div.stButton > button { width: 100% !important; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. EXPORT-FUNKTION (EXCEL AUTO-FIT) ---
def create_excel_autofit(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 5
            worksheet.set_column(i, i, min(column_len, 50))
    return output.getvalue()

# --- 3. RECHTLICHES & VORLAGEN (EXPANDER) ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    with st.expander("⚖️ Impressum"):
        st.text("""Amtsschimmel-Killer
Betreiberin: Elisabeth Reinecke
Ringelsweide 9
40223 Düsseldorf

Kontakt:
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

Haftung:
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")
with c2:
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
with c3:
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
with c4:
    with st.expander("📝 Vorlagen"):
        st.text("""Fristverlängerung:
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

Widerspruch einlegen (Fristwahrend):
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

Akteneinsicht einfordern:
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]""")

st.divider()

# --- 4. HAUPT-LAYOUT ---
col_left, col_right = st.columns([1.1, 1.8])

# LINKE SEITE: LOGO, SPRACHEN & PAKETE
with col_left:
    try: st.image("icon_final_blau.png", width=180)
    except: st.title("🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Wähle deine Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "ES Español", "IT Italiano"], label_visibility="collapsed")
    
    st.markdown("### 💳 Scans laden")
    
    # PAKET 1: Analyse
    with st.container():
        st.markdown('<div class="pkg-box" style="background-color: #f8f9fa;">'
                    '<div class="pkg-name">Amtsschimmel-Killer:<br>Analyse (1 Dokument)</div>'
                    '<div class="pkg-price">3,99 €</div>'
                    '<div class="pkg-info">❌ KEIN ABO • EINMALZAHLUNG</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")

    # PAKET 2: Spar-Paket
    with st.container():
        st.markdown('<div class="pkg-box" style="background-color: #ebf5fb; border: 1px solid #3498db;">'
                    '<div class="pkg-name">Amtsschimmel-Killer:<br>Spar-Paket (3 Dokumente)</div>'
                    '<div class="pkg-price">9,99 €</div>'
                    '<div class="pkg-info">❌ KEIN ABO • EINMALZAHLUNG</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")

    # PAKET 3: Sorglos-Paket
    with st.container():
        st.markdown('<div class="pkg-box" style="background-color: #fef9e7; border: 1px solid #fbc02d;">'
                    '<div class="pkg-name">Amtsschimmel-Killer:<br>Sorglos-Paket (10 Dokumente)</div>'
                    '<div class="pkg-price">19,99 €</div>'
                    '<div class="pkg-info">❌ KEIN ABO • EINMALZAHLUNG</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")

# RECHTE SEITE: UPLOAD & ERGEBNISSE
with col_right:
    st.markdown("### 📥 Dokument hochladen")
    st.success("👑 Admin Guthaben: 999 Scans verfügbar")
    
    uploaded_file = st.file_uploader("Hier klicken oder Datei reinziehen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        st.divider()
        res_left, res_right = st.columns([1, 1.2])
        
        with res_left:
            st.markdown("#### 🖼️ Vorschau")
            if uploaded_file.type == "application/pdf":
                st.info("PDF erkannt. Bereit zur Analyse.")
            else:
                st.image(uploaded_file, use_container_width=True)
        
        with res_right:
            st.markdown("#### 🔍 Ergebnisse")
            st.error("📅 **Frist erkannt: 24.12.2024**")
            
            with st.container(border=True):
                st.markdown("**📖 Glossar (Erklärung):**")
                st.write("- **Rechtsbehelfsbelehrung:** Information darüber, wie man Widerspruch einlegen kann.")
            
            with st.container(border=True):
                st.markdown("**✍️ Antwortschreiben:**")
                st.code("Sehr geehrte Damen und Herren,\nhiermit lege ich Widerspruch ein...", language="text")
        
        st.divider()
        st.markdown("#### 📥 Downloads")
        d1, d2, d3, d4 = st.columns(4)
        with d1: st.button("📄 PDF Brief")
        with d2:
            ex_data = create_excel_autofit({"Frist": "24.12.2024", "Typ": "Widerspruch"})
            st.download_button("📊 Excel (Auto)", ex_data, "Analyse.xlsx")
        with d3: st.button("📝 Word (.doc)")
        with d4: st.download_button("📅 Termin (.ics)", "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:Frist Behörde\nDTSTART:20241224T090000Z\nEND:VEVENT\nEND:VCALENDAR", "Termin.ics")
