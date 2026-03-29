import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide")

# CSS für exakte Optik wie im Bild
st.markdown("""
<style>
    .pkg-card { padding: 15px; border: 1px solid #2e5a88; border-radius: 8px; text-align: center; margin-bottom: 5px; background: white; }
    .pkg-title { font-weight: bold; font-size: 0.9em; }
    .pkg-price { font-size: 1.2em; font-weight: bold; color: #1f77b4; }
    .pkg-footer { color: red; font-weight: bold; font-size: 0.7em; }
    div.stButton > button { width: 100% !important; background-color: #004488 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. EXPORT-LOGIK (Ausführlich & Breit) ---
def create_excel_wide(data_list):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(data_list)
        df.to_excel(writer, index=False, sheet_name='Detaillierte Analyse')
        worksheet = writer.sheets['Detaillierte Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 100) # Extrem breit für ausführliche Texte
    return output.getvalue()

# --- 3. RECHTLICHES (Exakte Abstände) ---
with st.sidebar: # Um das 3-Spalten-Bild im Hauptbereich nicht zu stören
    st.markdown("### 🏛️ Informationen")
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\nBetreiberin: Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.\n\n4. Zahlungsabwicklung (Stripe)\nBei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.\n\n5. Ihre Rechte\nSie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.")
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]\n\nWiderspruch einlegen (Fristwahrend)\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]\n\nAkteneinsicht einfordern:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

# --- 4. HAUPT-LAYOUT (Drei Spalten wie im Bild) ---
col_left, col_mid, col_right = st.columns([1, 1.5, 1.2])

# LINKS: Sprachen & Pakete
with col_left:
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español"], label_visibility="collapsed")
    st.image("https://via.placeholder.com", width=80) # Platzhalter für dein Icon
    
    # Paket 1
    st.markdown('<div class="pkg-card"><div class="pkg-title">Amtsschimmel-Killer: Analyse (1 Dokument)</div><div class="pkg-price">3,99 €</div><div class="pkg-footer">❌ KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    
    # Paket 2
    st.markdown('<div class="pkg-card"><div class="pkg-title">Amtsschimmel-Killer: Spar Paket (3 Dokumente)</div><div class="pkg-price">9,99 €</div><div class="pkg-footer">❌ KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    
    # Paket 3
    st.markdown('<div class="pkg-card"><div class="pkg-title">Amtsschimmel-Killer: Sorglos Paket (10 Dokumente)</div><div class="pkg-price">19,99 €</div><div class="pkg-footer">❌ KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")

# MITTE: Upload & Vorschau
with col_mid:
    st.markdown("### 📄 Upload & Vorschau")
    st.info("Guthaben: 999 Dokumente")
    uploaded_file = st.file_uploader("Drag and drop file here", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        st.success(f"Dokument '{uploaded_file.name}' geladen.")
        if uploaded_file.type == "application/pdf":
            base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.image(uploaded_file, use_container_width=True)

# RECHTS: Analyse & Antwort
with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    if not uploaded_file:
        st.write("Hier erscheint das Ergebnis nach dem Scan.")
    else:
        st.error("📅 Frist erkannt: 24.12.2024")
        
        ausfuehrlicher_text = """SEHR AUSFÜHRLICHE ANALYSE:
        Das vorliegende Dokument ist ein Bescheid der Behörde X. 
        Die Rechtsbehelfsbelehrung ist fehlerhaft, da die Fristangabe unklar ist. 
        Es wird dringend empfohlen, Akteneinsicht nach § 25 SGB X zu beantragen. 
        Zudem fehlt eine hinreichende Begründung für die Kürzung der Leistungen nach § 35 SGB X. 
        Die Behörde hat ihr Ermessen nicht pflichtgemäß ausgeübt."""
        
        st.markdown("**Detaillierte Auswertung:**")
        st.write(ausfuehrlicher_text)
        
        st.markdown("**Ausführlicher Antwortentwurf:**")
        antwort_pro = "Sehr geehrte Damen und Herren,\n\nhiermit nehme ich ausführlich Stellung zu Ihrem Schreiben...\n\n(Hier folgen 3-4 Absätze juristisch fundierter Text zur Fristwahrung und Akteneinsicht)..."
        st.code(antwort_pro, language="text")
        
        # DOWNLOADS GANZ UNTEN RECHTS
        st.divider()
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button("📄 PDF", antwort_pro, "Analyse.pdf")
            st.download_button("📝 Word", antwort_pro, "Analyse.doc")
        with d_col2:
            excel_pro = create_excel_wide([{"Kategorie": "Analyse", "Inhalt": ausfuehrlicher_text}, {"Kategorie": "Antwort", "Inhalt": antwort_pro}])
            st.download_button("📊 Excel (Breit)", excel_pro, "Analyse.xlsx")
            st.download_button("📅 Termin", "BEGIN:VCALENDAR\nSUMMARY:Frist Amtsschimmel\nDTSTART:20241224T090000\nEND:VEVENT\nEND:VCALENDAR", "Termin.ics")
