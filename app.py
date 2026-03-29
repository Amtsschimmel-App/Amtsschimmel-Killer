import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. EXAKTES DESIGN (CSS) ---
st.markdown("""
<style>
    /* Paketboxen Styling */
    .pkg-container {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #d1d8e0;
        text-align: center;
        margin-bottom: 0px;
        min-height: 220px;
    }
    .pkg-title { font-weight: bold; font-size: 1.1em; color: #2c3e50; min-height: 50px; }
    .pkg-price { font-size: 26px; font-weight: bold; color: #1f77b4; margin: 10px 0; }
    .pkg-footer { font-size: 0.8em; font-weight: bold; color: #e74c3c; text-transform: uppercase; }
    
    /* Button Integration */
    div.stButton > button {
        width: 100% !important;
        background-color: #004488 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN (BREITE SPALTEN & AUSFÜHRLICHER TEXT) ---
def create_excel_pro(data_list):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(data_list)
        df.to_excel(writer, index=False, sheet_name='Detaillierte_Analyse')
        worksheet = writer.sheets['Detaillierte_Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 100) # Maximale Breite für ausführliche Texte
    return output.getvalue()

def get_pdf_display(uploaded_file):
    base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
    return f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'

# --- 4. TOP-BAR: RECHTLICHES (Nebeneinander & Zusammengeklappt) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\nBetreiberin: Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Logfiles werden automatisch erfasst.\n\n3. Dokumentenverarbeitung\nBriefe werden TLS-verschlüsselt an OpenAI (USA) übertragen. Keine dauerhafte Speicherung.\n\n4. Zahlungsabwicklung\nStripe erhebt die Daten zur Abrechnung.")
with t3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Nur Einmalzahlungen.\n\nWie sicher sind meine Dokumente?\nVerschlüsselte Übertragung, keine dauerhafte Speicherung.\n\nErsetzt die App eine Rechtsberatung?\nNein. Nur Formulierungshilfe.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nIch bitte um Verlängerung der Frist bis zum [Datum]...\nWiderspruch:\nHiermit lege ich Widerspruch gegen den Bescheid vom [Datum] ein...\nAkteneinsicht:\nIch beantrage Akteneinsicht gemäß § 25 SGB X.")

st.divider()

# --- 5. HAUPTBEREICH: 3-SPALTEN-LAYOUT ---
col_left, col_mid, col_right = st.columns([1.1, 1.5, 1.3])

# SPALTE 1: SPRACHEN & PAKETE (LINKS)
with col_left:
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية"], label_visibility="collapsed")
    st.image("https://cdn-icons-png.flaticon.com", width=70) # Dein Logo
    
    st.markdown("### 💳 Scans")
    # Paket 1
    st.markdown('<div class="pkg-container" style="background-color: #f9f9f9;"><div class="pkg-title">Amtsschimmel-Killer: Analyse (1 Dokument)</div><div class="pkg-price">3,99 €</div><div class="pkg-footer">❌ KEIN ABO • EINMALZAHLUNG</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")

    # Paket 2
    st.markdown('<div class="pkg-container" style="background-color: #ebf5fb; border-color: #3498db;"><div class="pkg-title">Amtsschimmel-Killer: Spar Paket (3 Dokumente)</div><div class="pkg-price">9,99 €</div><div class="pkg-footer">❌ KEIN ABO • EINMALZAHLUNG</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")

    # Paket 3
    st.markdown('<div class="pkg-container" style="background-color: #fef9e7; border-color: #f1c40f;"><div class="pkg-title">Amtsschimmel-Killer: Sorglos Paket (10 Dokumente)</div><div class="pkg-price">19,99 €</div><div class="pkg-footer">❌ KEIN ABO • EINMALZAHLUNG</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")

# SPALTE 2: UPLOAD & VORSCHAU (MITTE)
with col_mid:
    st.markdown("### 📑 Upload & Vorschau")
    st.success("👑 Guthaben: 999 Dokumente")
    uploaded_file = st.file_uploader("Datei hier reinziehen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.markdown(get_pdf_display(uploaded_file), unsafe_allow_html=True)
        else:
            st.image(uploaded_file, use_container_width=True)

# SPALTE 3: ANALYSE & ANTWORT (RECHTS)
with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    if uploaded_file:
        st.error("📅 **Frist erkannt: 24.12.2024**")
        
        ausfuehrliche_analyse = """**DETAILLIERTE JURISTISCHE ANALYSE:**
        Der vorliegende Bescheid weist formelle Mängel in der Rechtsbehelfsbelehrung auf. 
        Die Behörde hat die notwendige Ermessensprüfung gemäß § 39 SGB I nicht erkennbar durchgeführt. 
        Dies führt zur Rechtswidrigkeit des Verwaltungsaktes. 
        Es wird empfohlen, innerhalb der Monatsfrist zu widersprechen und gleichzeitig Akteneinsicht zu beantragen, 
        um die interne Sachverhaltsermittlung der Behörde auf Fehler zu prüfen."""
        
        st.info(ausfuehrliche_analyse)
        
        tab1, tab2 = st.tabs(["📝 Antwortschreiben", "⚖️ Widerspruch"])
        
        with tab1:
            st.markdown("**Ausführliche Stellungnahme:**")
            antwort_pro = """Sehr geehrte Damen und Herren,
            
hiermit nehme ich Bezug auf Ihr Schreiben vom [Datum]. Nach eingehender Prüfung der Sach- und Rechtslage stelle ich fest, dass die von Ihnen angeführten Begründungen nicht der tatsächlichen Situation entsprechen. 

Insbesondere wurden die vorliegenden Nachweise zur [Thematik] nicht hinreichend gewürdigt. Ich fordere Sie daher auf, den Sachverhalt erneut unter Berücksichtigung der beigefügten Argumente zu prüfen. Bis zu einer abschließenden Klärung bitte ich um Aussetzung der Vollziehung."""
            st.code(antwort_pro, language="text")
            
        with tab2:
            st.markdown("**Ausführlicher Widerspruch:**")
            widerspruch_pro = """Sehr geehrte Damen und Herren,

gegen Ihren Bescheid vom [Datum], Aktenzeichen [Nummer], lege ich hiermit form- und fristgerecht WIDERSPRUCH ein.

Begründung: Der Bescheid ist materiell rechtswidrig. Die Behörde ist von einem unrichtigen Sachverhalt ausgegangen. Zudem liegt ein Ermessensfehler vor. Eine detaillierte Begründung wird nach erfolgter Akteneinsicht gemäß § 25 SGB X nachgereicht. Ich beantrage hiermit, mir die Akten in Kopie zuzusenden oder mir einen Termin zur Einsichtnahme zu nennen."""
            st.code(widerspruch_pro, language="text")
            
        st.divider()
        st.markdown("#### 📥 Ergebnisse sichern")
        d_c1, d_c2 = st.columns(2)
        with d_c1:
            st.download_button("📄 PDF (Vollständig)", ausfuehrliche_analyse + "\n\n" + widerspruch_pro, "Analyse.pdf", use_container_width=True)
            st.download_button("📝 Word (Detailliert)", widerspruch_pro, "Widerspruch.doc", use_container_width=True)
        with d_c2:
            excel_pro = create_excel_pro([{"Analyse": ausfuehrliche_analyse, "Entwurf": widerspruch_pro}])
            st.download_button("📊 Excel Pro (Breit)", excel_pro, "Analyse_Breit.xlsx", use_container_width=True)
            st.download_button("📅 Termin", "BEGIN:VCALENDAR\nSUMMARY:Frist Amtsschimmel\nDTSTART:20241224T090000Z\nEND:VEVENT\nEND:VCALENDAR", "Frist.ics", use_container_width=True)
    else:
        st.write("Hier erscheint das Ergebnis nach dem Scan.")
