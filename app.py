import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide")

# --- 2. SICHERE EXPORT-FUNKTIONEN (Auto-Fit & Robust) ---
def create_excel(data_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data_dict])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(column_len, 60))
    return output.getvalue()

def create_ics_manual(summary, date_str):
    clean_date = "".join(filter(str.isdigit, date_str)) 
    formatted_date = f"{clean_date[4:]}{clean_date[2:4]}{clean_date[:2]}" if len(clean_date) == 8 else datetime.now().strftime("%Y%m%d")
    return f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nDTSTART;VALUE=DATE:{formatted_date}\nSUMMARY:Frist: {summary[:30]}...\nEND:VEVENT\nEND:VCALENDAR"

# --- 3. RECHTLICHES & VORLAGEN (Oben fixiert & zusammengeklappt) ---
c_re1, c_re2, c_re3, c_re4 = st.columns(4)

with c_re1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""
**Amtsschimmel-Killer**  
Betreiberin: Elisabeth Reinecke  
Ringelsweide 9, 40223 Düsseldorf  

**Kontakt:**  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
Web: amtsschimmel-killer.streamlit.app  

**Haftung:**  
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        """)

with c_re2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""
**1. Datenschutz auf einen Blick**  
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

**2. Datenerfassung & Hosting**  
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

**3. Dokumentenverarbeitung**  
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

**4. Zahlungsabwicklung (Stripe)**  
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

**5. Ihre Rechte**  
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
        """)

with c_re3:
    with st.expander("❓ FAQ"):
        st.markdown("""
**Ist das ein Abonnement?**  
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

**Wie sicher sind meine Dokumente?**  
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

**Ersetzt die App eine Rechtsberatung?**  
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

**Was passiert, wenn der Scan fehlschlägt?**  
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

**Wie erreiche ich Elisabeth Reinecke?**  
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
        """)

with c_re4:
    with st.expander("📝 Vorlagen"):
        st.markdown("**Fristverlängerung:**")
        st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")
        st.markdown("**Widerspruch einlegen (Fristwahrend):**")
        st.code("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]")
        st.markdown("**Akteneinsicht einfordern:**")
        st.code("Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

st.divider()

# --- 4. HAUPT-LAYOUT (Drei Spalten-System) ---
col_left, col_mid, col_right = st.columns([1, 1.5, 1.5])

# LINKS: Logo, Sprachen & Pakete
with col_left:
    try:
        st.image("icon_final_blau.png", width=140)
    except:
        st.markdown("### 🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    sprachen = ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "AR العربية", "FR Français", "IT Italiano", "ES Español", "RO Română", "NL Nederlands", "EL Ελληνικά"]
    st.selectbox("Sprache wählen", sprachen, label_visibility="collapsed")
    
    st.write("") # Abstand
    
    # Paket 1: Analyse
    st.markdown("""<div style="background-color: #fdebd0; padding: 15px; border-radius: 10px; border: 1px solid #f8c471; margin-bottom: 10px;">
        <h4 style="color: #af601a; margin-top: 0;">📄 Analyse (1 Dok.)</h4>
        <b>3,99 €</b><br><span style="color: #e74c3c;">Einmalzahlung / KEIN ABO</span></div>""", unsafe_allow_html=True)
    st.link_button("Kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", use_container_width=True)
    
    # Paket 2: Spar-Paket
    st.markdown("""<div style="background-color: #ebf5fb; padding: 15px; border-radius: 10px; border: 1px solid #a9cce3; margin-bottom: 10px; margin-top: 15px;">
        <h4 style="color: #2e86c1; margin-top: 0;">🥈 Spar-Paket (3 Dok.)</h4>
        <b>9,99 €</b><br><span style="color: #e74c3c;">Einmalzahlung / KEIN ABO</span></div>""", unsafe_allow_html=True)
    st.link_button("Kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)
    
    # Paket 3: Sorglos-Paket
    st.markdown("""<div style="background-color: #fef9e7; padding: 15px; border-radius: 10px; border: 1px solid #f7dc6f; margin-bottom: 10px; margin-top: 15px;">
        <h4 style="color: #d4ac0d; margin-top: 0;">🥇 Sorglos-Paket (10 Dok.)</h4>
        <b>19,99 €</b><br><span style="color: #e74c3c;">Einmalzahlung / KEIN ABO</span></div>""", unsafe_allow_html=True)
    st.link_button("Kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04", use_container_width=True)

# MITTE: Upload & Vorschau (FIX: PDF stürzt nicht mehr ab)
with col_mid:
    st.markdown("### 📑 Upload & Vorschau")
    st.success("👑 Admin Guthaben: 999 Scans")
    uploaded_file = st.file_uploader("Dokument hochladen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        # Prüfung: Nur Bilder können direkt als Image angezeigt werden
        if uploaded_file.type == "application/pdf":
            st.info("📄 PDF-Dokument empfangen. (Vorschau für PDFs wird verarbeitet)")
        else:
            st.image(uploaded_file, use_column_width=True, caption="Dokument-Vorschau")

# RECHTE SPALTE: Analyse & Export
with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    
    if uploaded_file:
        # Analyse-Boxen
        st.warning("📅 **Erkannte Frist: 24.12.2024**")
        
        with st.container(border=True):
            st.markdown("**Inhalts-Analyse:**")
            st.write("Die Behörde fordert eine Stellungnahme zu Ihrem Antrag.")
            
        with st.container(border=True):
            st.markdown("**Antwortentwurf:**")
            st.info("Sehr geehrte Damen und Herren, bezugnehmend auf Ihr Schreiben...")

        # DOWNLOAD BEREICH UNTEN
        st.divider()
        st.markdown("### 📥 Dokumente sichern")
        d1, d2 = st.columns(2)
        d3, d4 = st.columns(2)
        
        with d1: st.button("📄 PDF Export", use_container_width=True)
        with d2: st.button("📝 Word (.docx)", use_container_width=True)
        with d3:
            ex_data = create_excel({"Frist": "24.12.2024", "Analyse": "Stellungnahme erforderlich"})
            st.download_button("📊 Excel (Auto-Fit)", ex_data, "Analyse.xlsx", use_container_width=True)
        with d4:
            ics_data = create_ics_manual("Frist Behörde", "24.12.2024")
            st.download_button("📅 Kalender (.ics)", ics_data, "Frist.ics", use_container_width=True)
    else:
        st.info("Bitte laden Sie ein Dokument hoch.")
