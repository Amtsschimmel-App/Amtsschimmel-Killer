import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide")

# --- 2. EXPORT-FUNKTIONEN (Auto-Fit Excel & Kalender) ---
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

# --- 3. RECHTLICHES & VORLAGEN (Oben fixiert) ---
c_top1, c_top2, c_top3, c_top4 = st.columns(4)

with c_top1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""
Impressum:

Amtsschimmel-Killer
Betreiberin: Elisabeth Reinecke
Ringelsweide 9
40223 Düsseldorf

Kontakt:
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

Haftung:
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        """)

with c_top2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""
Datenschutz:

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

with c_top3:
    with st.expander("❓ FAQ"):
        st.markdown("""
FAQ

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

with c_top4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""
Vorlagen:

Fristverlängerung:
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

Widerspruch einlegen (Fristwahrend)
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

Akteneinsicht einfordern:
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
        """)

st.divider()

# --- 4. HAUPT-LAYOUT (Drei Spalten) ---
col_left, col_mid, col_right = st.columns([1, 1.5, 1.5])

# LINKS: Logo & Pakete
with col_left:
    try:
        st.image("icon_final_blau.png", width=120)
    except:
        st.markdown("🏛️ **Amtsschimmel-Killer**")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "AR العربية"], label_visibility="collapsed")
    
    st.write("") 
    # Paket 1
    st.markdown("""<div style="background-color: #fdebd0; padding: 10px; border-radius: 10px; border: 1px solid #f8c471;">
        <h5 style="margin:0;">📄 Analyse (1 Dok.)</h5><b>3,99 €</b><br><b>Einmalzahlung</b><br><small>❌ KEIN ABO</small></div>""", unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", use_container_width=True)
    
    # Paket 2
    st.markdown("""<div style="background-color: #ebf5fb; padding: 10px; border-radius: 10px; border: 1px solid #a9cce3; margin-top:10px;">
        <h5 style="margin:0;">🥈 Spar-Paket (3 Dok.)</h5><b>9,99 €</b><br><b>Einmalzahlung</b><br><small>❌ KEIN ABO</small></div>""", unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)
    
    # Paket 3
    st.markdown("""<div style="background-color: #fef9e7; padding: 10px; border-radius: 10px; border: 1px solid #f7dc6f; margin-top:10px;">
        <h5 style="margin:0;">🥇 Sorglos-Paket (10 Dok.)</h5><b>19,99 €</b><br><b>Einmalzahlung</b><br><small>❌ KEIN ABO</small></div>""", unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04", use_container_width=True)

# MITTE: Upload & Vorschau
with col_mid:
    st.markdown("### 📑 Upload & Vorschau")
    st.success("👑 Admin Guthaben: 999 Scans")
    uploaded_file = st.file_uploader("Dokument hochladen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.info("📄 PDF erfolgreich geladen.")
        else:
            st.image(uploaded_file, use_column_width=True, caption="Vorschau")

# RECHTE SPALTE: Analyse-Boxen
with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    if uploaded_file:
        st.warning("📅 **Frist erkannt: 24.12.2024**")
        
        with st.container(border=True):
            st.markdown("**Inhalts-Analyse:**")
            st.write("Die Behörde bittet um Stellungnahme zu Ihrem Antrag.")
            
        with st.container(border=True):
            st.markdown("**Antwortentwurf:**")
            st.info("Sehr geehrte Damen und Herren, anbei sende ich Ihnen...")

# --- 5. DOWNLOAD BEREICH (Ganz unten) ---
if uploaded_file:
    st.divider()
    st.markdown("### 📥 Ergebnisse sichern")
    d1, d2, d3, d4 = st.columns(4)
    with d1: st.button("📄 PDF Export", use_container_width=True)
    with d2: st.button("📝 Word (.docx)", use_container_width=True)
    with d3:
        ex = create_excel({"Frist": "24.12.2024", "Analyse": "Stellungnahme"})
        st.download_button("📊 Excel (Auto-Fit)", ex, "Analyse.xlsx", use_container_width=True)
    with d4:
        ics = create_ics_manual("Frist Behörde", "24.12.2024")
        st.download_button("📅 Kalender (.ics)", ics, "Termin.ics", use_container_width=True)
