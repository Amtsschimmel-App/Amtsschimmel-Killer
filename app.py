import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# Custom CSS für die Boxen und Buttons
st.markdown("""
<style>
    .p-box { padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; text-align: center; margin-bottom: 10px; height: 280px; }
    .price { font-size: 26px; font-weight: bold; margin: 10px 0; color: #1f77b4; }
    .no-abo { background-color: #ff4b4b; color: white; padding: 3px 10px; border-radius: 5px; font-size: 14px; font-weight: bold; }
    div.stButton > button { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. HILFSFUNKTIONEN FÜR EXPORT ---

def create_excel_autofit(data_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data_dict])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 5
            worksheet.set_column(i, i, min(column_len, 50))
    return output.getvalue()

def create_ics(summary, date_str):
    # Einfaches ICS Format
    ics_content = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nDTSTART:20241224T090000Z\nSUMMARY:{summary}\nDESCRIPTION:Erstellt von Amtsschimmel-Killer\nEND:VEVENT\nEND:VCALENDAR"
    return ics_content

def create_simple_word(text):
    # Da docx eine externe Library ist, hier als Text-Datei Simulation oder Platzhalter
    return text.encode('utf-8')

# --- 3. RECHTLICHES & VORLAGEN (Header) ---
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

Widerspruch einlegen (Fristwahrend)
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

Akteneinsicht einfordern:
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]""")

st.divider()

# --- 4. LOGO & SPRACHE ---
l1, l2 = st.columns([2, 1])
with l1:
    try: st.image("icon_final_blau.png", width=220)
    except: st.title("🏛️ Amtsschimmel-Killer")
with l2:
    st.selectbox("🌐 Sprache wählen / Select Language", 
                 ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "AR العربية", "FR Français", "ES Español", "IT Italiano"])

# --- 5. HAUPT-LOGIK ---
uploaded_file = st.file_uploader("Dokument hochladen (PDF, JPG, PNG)", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")

if not uploaded_file:
    st.info("Bitte wählen Sie ein Paket aus, um Scans freizuschalten. Nach dem Kauf können Sie Ihr Dokument hier hochladen.")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown('<div class="p-box" style="background-color: #f8f9fa;"><h4>Amtsschimmel-Killer:<br>Analyse (1 Dok.)</h4><div class="price">3,99 €</div><span class="no-abo">❌ KEIN ABO</span><br><br></div>', unsafe_allow_html=True)
        st.link_button("🛒 Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    with p2:
        st.markdown('<div class="p-box" style="background-color: #ebf5fb; border: 1px solid #3498db;"><h4>Amtsschimmel-Killer:<br>Spar-Paket (3 Dok.)</h4><div class="price">9,99 €</div><span class="no-abo">❌ KEIN ABO</span><br><br></div>', unsafe_allow_html=True)
        st.link_button("🛒 Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    with p3:
        st.markdown('<div class="p-box" style="background-color: #fef9e7; border: 1px solid #f1c40f;"><h4>Amtsschimmel-Killer:<br>Sorglos-Paket (10 Dok.)</h4><div class="price">19,99 €</div><span class="no-abo">❌ KEIN ABO</span><br><br></div>', unsafe_allow_html=True)
        st.link_button("🛒 Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")
else:
    # ANALYSE MODUS
    st.success("👑 Admin Guthaben: 999 Scans verfügbar")
    col_preview, col_results = st.columns([1, 1.2])
    
    with col_preview:
        st.subheader("🖼️ Dokumenten-Vorschau")
        if uploaded_file.type == "application/pdf":
            st.warning("Vorschau für PDF-Dateien im Browser eingeschränkt. Datei bereit zur Analyse.")
        else:
            st.image(uploaded_file, use_container_width=True, caption="Hochgeladener Brief")
            
    with col_results:
        st.subheader("🔍 KI-Auswertung")
        st.error("📅 **Wichtige Frist: 24.12.2024**")
        
        with st.container(border=True):
            st.markdown("**📖 Glossar (Einfach erklärt)**")
            st.write("- **Rechtsbehelfsbelehrung:** Der Abschnitt, der sagt, wie man sich wehren kann.\n- **Säumigkeitszuschlag:** Eine Strafe für zu spätes Zahlen.")
            
        with st.container(border=True):
            st.markdown("**✍️ Antwortschreiben (Vorschlag)**")
            antwort_text = "Sehr geehrte Damen und Herren,\n\nbezugnehmend auf Ihr Schreiben vom [Datum] lege ich hiermit Widerspruch ein.\n\nMit freundlichen Grüßen,\n[Dein Name]"
            st.code(antwort_text, language="text")
        
        st.divider()
        st.markdown("### 📥 Ergebnisse sichern")
        d1, d2, d3, d4 = st.columns(4)
        
        with d1:
            st.download_button("📄 PDF", "PDF Inhalt", "Analyse.pdf", use_container_width=True)
        with d2:
            excel_data = create_excel_autofit({"Frist": "24.12.2024", "Betreff": "Widerspruch", "Empfänger": "Behörde"})
            st.download_button("📊 Excel", excel_data, "Analyse.xlsx", use_container_width=True)
        with d3:
            word_data = create_simple_word(antwort_text)
            st.download_button("📝 Word", word_data, "Antwort.doc", use_container_width=True)
        with d4:
            ics_data = create_ics("Frist: Amtsschimmel-Killer", "20241224")
            st.download_button("📅 Termin", ics_data, "Frist.ics", use_container_width=True)
