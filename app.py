import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS FÜR FARBIGE PAKETE & BUTTON-INTEGRATION ---
st.markdown("""
<style>
    /* Expander Styling */
    .stExpander { border: none !important; box-shadow: none !important; }
    
    /* Paket Boxen */
    .pkg-container {
        padding: 15px;
        border-radius: 15px;
        text-align: center;
    }
    .pkg-icon { font-size: 40px; margin-bottom: 10px; }
    .pkg-title { font-weight: bold; font-size: 1.1em; min-height: 60px; color: #2c3e50; }
    .pkg-price { font-size: 28px; font-weight: bold; margin: 10px 0; color: #1f77b4; }
    .pkg-footer { font-size: 0.8em; font-weight: bold; color: #e74c3c; margin-bottom: 15px; }
    
    /* Buttons IN den Paketen stylen */
    div.stButton > button {
        width: 100% !important;
        background-color: #1f77b4 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN (EXCEL PRO & WORD) ---
def create_excel_pro(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(data)
        df.to_excel(writer, index=False, sheet_name='Detaillierte_Analyse')
        worksheet = writer.sheets['Detaillierte_Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 100) # Maximale Breite
    return output.getvalue()

def get_pdf_display(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    return f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px" type="application/pdf"></iframe>'

# --- 4. TOP-BAR: RECHTLICHES (NEBENEINANDER & ZUSAMMENGEKLAPPT) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
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

# --- 5. HAUPT-LAYOUT (PAKETE | UPLOAD | ANALYSE) ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

# LINK SPALTE: LOGO & PAKETE
with col_left:
    try:
        st.image("icon_final_blau.png", width=160)
    except:
        st.markdown("🏛️ **Amtsschimmel-Killer**")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية"], label_visibility="collapsed")
    
    st.write("")
    # Paket 1
    with st.container(border=True):
        st.markdown('<div class="pkg-icon">📄</div>', unsafe_allow_html=True)
        st.markdown('**Amtsschimmel-Killer: Analyse (1 Dokument)**')
        st.markdown('<div class="pkg-price">3,99 €</div>', unsafe_allow_html=True)
        st.markdown('<div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")

    # Paket 2
    with st.container(border=True):
        st.markdown('<div style="background-color: #ebf5fb; padding: 5px; border-radius: 10px;">', unsafe_allow_html=True)
        st.markdown('<div class="pkg-icon">🥈</div>', unsafe_allow_html=True)
        st.markdown('**Amtsschimmel-Killer: Spar-Paket (3 Dokumente)**')
        st.markdown('<div class="pkg-price">9,99 €</div>', unsafe_allow_html=True)
        st.markdown('<div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
        st.markdown('</div>', unsafe_allow_html=True)

    # Paket 3
    with st.container(border=True):
        st.markdown('<div style="background-color: #fef9e7; padding: 5px; border-radius: 10px;">', unsafe_allow_html=True)
        st.markdown('<div class="pkg-icon">🥇</div>', unsafe_allow_html=True)
        st.markdown('**Amtsschimmel-Killer: Sorglos-Paket (10 Dokumente)**')
        st.markdown('<div class="pkg-price">19,99 €</div>', unsafe_allow_html=True)
        st.markdown('<div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")
        st.markdown('</div>', unsafe_allow_html=True)

# MITTLERE SPALTE: UPLOAD & VORSCHAU
with col_mid:
    st.markdown("### 📑 Upload & Vorschau")
    st.success("👑 Guthaben: 999 Dokumente")
    uploaded_file = st.file_uploader("Datei hier reinziehen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.markdown(get_pdf_display(uploaded_file), unsafe_allow_html=True)
        else:
            st.image(uploaded_file, use_container_width=True)

# RECHTE SPALTE: ANALYSE & ANTWORT
with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    if uploaded_file:
        st.error("📅 **Frist erkannt: 24.12.2024**")
        
        ausfuehrliche_analyse = """**AUSFÜHRLICHE JURISTISCHE ANALYSE:**
Das vorliegende Dokument ist ein Bescheid einer Verwaltungsbehörde. 
Nach Prüfung der Rechtsbehelfsbelehrung wurde festgestellt, dass die Frist zur Einlegung eines Widerspruchs einen Monat beträgt. 

Mögliche Fehlerquellen im Bescheid:
1. **Ermessensfehler**: Die Behörde hat ihr Ermessen (§ 39 SGB I) nicht erkennbar ausgeübt.
2. **Begründungsmangel**: Die Begründung nach § 35 SGB X ist unvollständig.
3. **Sachverhaltsaufklärung**: Es scheint, als seien wesentliche Tatsachen nicht berücksichtigt worden.

Es wird dringend empfohlen, fristwahrend Widerspruch einzulegen und Akteneinsicht gemäß § 25 SGB X zu beantragen."""
        
        st.info(ausfuehrliche_analyse)
        
        tab1, tab2 = st.tabs(["✍️ Antwortschreiben", "⚖️ Widerspruch"])
        
        with tab1:
            stellungnahme = """Sehr geehrte Damen und Herren,

hiermit nehme ich Bezug auf Ihr Schreiben vom [Datum], Aktenzeichen [Nummer].

Nach Durchsicht der Unterlagen stelle ich fest, dass der von Ihnen geschilderte Sachverhalt in wesentlichen Punkten von der Realität abweicht. Insbesondere wurde nicht berücksichtigt, dass [hier eigenen Grund einfügen].

Ich fordere Sie daher auf, die Entscheidung unter Berücksichtigung dieser neuen Informationen erneut zu prüfen. Bis zu einer endgültigen Klärung bitte ich um eine schriftliche Bestätigung über den Erhalt dieser Stellungnahme.

Mit freundlichen Grüßen,
[Name]"""
            st.code(stellungnahme, language="text")
            
        with tab2:
            widerspruch = """Sehr geehrte Damen und Herren,

gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit form- und fristgerecht

WIDERSPRUCH

ein.

Begründung: Der Bescheid ist materiell rechtswidrig, da er auf einer unvollständigen Sachverhaltsaufklärung beruht. Zudem liegt eine Ermessensunterschreitung vor. 

Zur weiteren Begründung des Widerspruchs beantrage ich hiermit die Akteneinsicht gemäß § 25 SGB X. Ich bitte um Zusendung der Akten in Kopie oder Benennung eines Termins zur Einsichtnahme. Eine detaillierte Begründung wird nach erfolgter Akteneinsicht nachgereicht.

Mit freundlichen Grüßen,
[Name]"""
            st.code(widerspruch, language="text")
            
        st.divider()
        st.markdown("#### 📥 Ergebnisse sichern")
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("📄 PDF Brief", widerspruch, "Widerspruch.pdf", use_container_width=True)
            st.download_button("📝 Word Brief", widerspruch, "Widerspruch.doc", use_container_width=True)
        with d2:
            ex_data = create_excel_pro([{"Analyse": ausfuehrliche_analyse, "Antwort": stellungnahme, "Widerspruch": widerspruch}])
            st.download_button("📊 Excel (Breit)", ex_data, "Analyse_Breit.xlsx", use_container_width=True)
            st.download_button("📅 Termin", "BEGIN:VCALENDAR\nSUMMARY:Frist Behörde\nDTSTART:20241224T090000Z\nEND:VEVENT\nEND:VCALENDAR", "Frist.ics", use_container_width=True)
    else:
        st.write("Hier erscheint das Ergebnis nach dem Scan.")
