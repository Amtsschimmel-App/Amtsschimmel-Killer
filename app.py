import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. ELEGANTES DESIGN (CSS) ---
st.markdown("""
<style>
    /* Paket-Karten Styling */
    .pkg-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #d1d8e0;
        margin-bottom: 10px;
        text-align: center;
        transition: transform 0.2s;
    }
    .pkg-icon { font-size: 35px; margin-bottom: 10px; }
    .pkg-title { font-weight: bold; font-size: 0.95em; color: #2c3e50; min-height: 50px; }
    .pkg-price { font-size: 24px; font-weight: bold; color: #1f77b4; margin: 5px 0; }
    .pkg-tag { font-size: 0.75em; font-weight: bold; color: #e74c3c; text-transform: uppercase; }
    
    /* Buttons */
    div.stButton > button {
        width: 100% !important;
        background-color: #1f77b4 !important;
        color: white !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN (BREITE SPALTEN & DATEN) ---
def create_excel_wide(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data])
        df.to_excel(writer, index=False, sheet_name='Analyse_Detail')
        worksheet = writer.sheets['Analyse_Detail']
        # Setzt alle Spalten auf eine Breite von 100 (extrem breit für viel Text)
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 100)
    return output.getvalue()

def show_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 4. TOP-BAR: RECHTLICHES & VORLAGEN (NEBENEINANDER & ZUSAMMENGEKLAPPT) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\nBetreiberin: Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles automatisch erfasst.\n\n3. Dokumentenverarbeitung\nIhre Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen.\n\n4. Zahlungsabwicklung (Stripe)\nStripe erhebt die Daten zur Abrechnung.\n\n5. Ihre Rechte\nRecht auf Auskunft, Löschung und Sperrung unter amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Wir hassen Abos. Jede Zahlung ist eine Einmalzahlung. Keine automatische Verlängerung.\n\nWie sicher sind meine Dokumente?\nVerschlüsselte Übertragung, keine dauerhafte Speicherung.\n\nErsetzt die App eine Rechtsberatung?\nNein. Wir bieten Formulierungshilfe.\n\nWas passiert bei Fehlern?\nKein Guthabenabzug bei technischem Scheitern.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nIch bitte um Verlängerung der Frist bis zum [Datum]...\n\nWiderspruch:\nHiermit lege ich Widerspruch gegen den Bescheid vom [Datum] ein...\n\nAkteneinsicht:\nIch beantrage Akteneinsicht gemäß § 25 SGB X.")

st.divider()

# --- 5. HAUPTBEREICH: 3-SPALTEN-LAYOUT (PAKETE | UPLOAD | ANALYSE) ---
col_pakete, col_upload, col_analyse = st.columns([1, 1.5, 1.2])

# SPALTE 1: SPRACHEN & PAKETE (LINKS)
with col_pakete:
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "ES Español", "IT Italiano"], label_visibility="collapsed")
    
    st.image("https://cdn-icons-png.flaticon.com", width=60) # Beispiel Icon für Amtsschimmel-Killer
    
    # Paket 1
    st.markdown('<div class="pkg-card" style="background-color: #f9f9f9;"><div class="pkg-icon">📄</div><div class="pkg-title">Amtsschimmel-Killer: Analyse (1 Dokument)</div><div class="pkg-price">3,99 €</div><div class="pkg-tag">❌ KEIN ABO • EINMALZAHLUNG</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")

    # Paket 2
    st.markdown('<div class="pkg-card" style="background-color: #ebf5fb; border-color: #3498db;"><div class="pkg-icon">🥈</div><div class="pkg-title">Amtsschimmel-Killer: Spar Paket (3 Dokumente)</div><div class="pkg-price">9,99 €</div><div class="pkg-tag">❌ KEIN ABO • EINMALZAHLUNG</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")

    # Paket 3
    st.markdown('<div class="pkg-card" style="background-color: #fef9e7; border-color: #f1c40f;"><div class="pkg-icon">🥇</div><div class="pkg-title">Amtsschimmel-Killer: Sorglos Paket (10 Dokumente)</div><div class="pkg-price">19,99 €</div><div class="pkg-tag">❌ KEIN ABO • EINMALZAHLUNG</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")

# SPALTE 2: UPLOAD & VORSCHAU (MITTE)
with col_upload:
    st.markdown("### 📑 Upload & Vorschau")
    st.info("👑 Guthaben: 999 Dokumente")
    
    up_file = st.file_uploader("Drag and drop file here", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if up_file:
        st.success(f"Datei '{up_file.name}' geladen.")
        if up_file.type == "application/pdf":
            show_pdf(up_file)
        else:
            st.image(up_file, use_container_width=True)

# SPALTE 3: ANALYSE & ANTWORT (RECHTS)
with col_analyse:
    st.markdown("### 🔍 Analyse & Antwort")
    if not up_file:
        st.write("Hier erscheint das Ergebnis nach dem Scan.")
    else:
        st.error("📅 Frist erkannt: 24.12.2024")
        
        ausfuehrlich = """**AUSFÜHRLICHE ANALYSE:**
        Bei dem vorliegenden Dokument handelt es sich um einen Bescheid der Behörde. 
        Auffällig ist die Rechtsbehelfsbelehrung, die unpräzise Formulierungen zur Fristwahrung enthält. 
        Es wird empfohlen, innerhalb der nächsten 14 Tage eine ausführliche Stellungnahme abzugeben. 
        Zudem sollte Akteneinsicht nach § 25 SGB X beantragt werden, um die Sachlage vollumfänglich zu prüfen."""
        
        with st.container(border=True):
            st.markdown("**Ergebnis:**")
            st.write(ausfuehrlich)
        
        st.markdown("**Detaillierter Antwortentwurf:**")
        antwort_pro = """Sehr geehrte Damen und Herren,
        
hiermit nehme ich Bezug auf Ihr Schreiben vom [Datum]. Gegen den Bescheid lege ich hiermit form- und fristgerecht WIDERSPRUCH ein. 

Die Begründung erfolgt nach erfolgter Akteneinsicht, welche ich hiermit gemäß § 25 SGB X beantrage. Bitte bestätigen Sie den Eingang dieses Schreibens umgehend."""
        st.code(antwort_pro, language="text")
        
        # DOWNLOAD BEREICH
        st.divider()
        d_c1, d_c2 = st.columns(2)
        with d_c1:
            st.download_button("📄 PDF Brief", antwort_pro, "Analyse.pdf", use_container_width=True)
            st.download_button("📝 Word", antwort_pro, "Analyse.doc", use_container_width=True)
        with d_c2:
            excel_data = create_excel_wide({"Kategorie": "Detaillierte Analyse", "Inhalt": ausfuehrlich, "Vorschlag": antwort_pro})
            st.download_button("📊 Excel Breit", excel_data, "Analyse_Breit.xlsx", use_container_width=True)
            st.download_button("📅 Termin", "BEGIN:VCALENDAR\nSUMMARY:Frist Amtsschimmel\nDTSTART:20241224T090000\nEND:VEVENT\nEND:VCALENDAR", "Frist.ics", use_container_width=True)
