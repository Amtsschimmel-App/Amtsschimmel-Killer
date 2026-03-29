import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- 1. SEITENKONFIGURATION (Layout wie im Screenshot) ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide")

# --- 2. EXPORT-FUNKTIONEN (Sicher & Robust) ---
def create_excel(data_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data_dict])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        # Automatischer Spalten-Fit
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(column_len, 60))
    return output.getvalue()

def create_ics_manual(summary, date_str):
    # Formatiert Datum sicher für Kalender-Apps
    clean_date = "".join(filter(str.isdigit, date_str)) 
    formatted_date = f"{clean_date[4:]}{clean_date[2:4]}{clean_date[:2]}" if len(clean_date) == 8 else datetime.now().strftime("%Y%m%d")
    
    return f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART;VALUE=DATE:{formatted_date}
SUMMARY:Amtsschimmel-Frist: {summary[:30]}...
DESCRIPTION:{summary}
END:VEVENT
END:VCALENDAR"""

# --- 3. HAUPT-LAYOUT (Drei Spalten-System) ---
col_left, col_mid, col_right = st.columns([1, 1.5, 1.5])

# --- LINKE SPALTE: SPRACHEN & PAKETE ---
with col_left:
    st.subheader("🌐 Sprachen")
    sprachen = ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "AR العربية"]
    st.selectbox("Sprache wählen", sprachen, label_visibility="collapsed")
    
    st.write("") # Abstand
    # Logo Platzhalter (Blaues Icon aus deinem Screen)
    st.markdown("🎨 **Amtsschimmel-Killer**") 
    
    # Paket 1
    st.info("**Amtsschimmel Killer: Analyse**\n\n(1 Dokument)\n\n**Einmalpreis 3,99 €**\n\n❌ KEIN ABO")
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", use_container_width=True)
    
    # Paket 2
    st.info("**Amtsschimmel Killer: Spar Paket**\n\n(3 Dokumente)\n\n**Einmalpreis 9,99 €**\n\n❌ KEIN ABO")
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)
    
    # Paket 3
    st.info("**Amtsschimmel Killer: Sorglos Paket**\n\n(10 Dokumente)\n\n**Einmalpreis 19,99 €**\n\n❌ KEIN ABO")
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04", use_container_width=True)

# --- MITTLERE SPALTE: UPLOAD & VORSCHAU ---
with col_mid:
    st.subheader("📑 Upload & Vorschau")
    st.success("Guthaben: 999 Dokumente")
    
    uploaded_file = st.file_uploader("Drag and drop file here", type=["pdf", "jpg", "png", "jpeg"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Vorschau des Dokuments", use_column_width=True)

# --- RECHTE SPALTE: ANALYSE & ANTWORT ---
with col_right:
    st.subheader("🔍 Analyse & Antwort")
    
    # Platzhalter für das Ergebnis (Hier verknüpfst du später deine OpenAI-Antwort)
    ergebnis_demo = "Hier erscheint das Ergebnis nach dem Scan."
    frist_demo = "24.12.2024"
    
    st.info(ergebnis_demo)
    
    if uploaded_file:
        st.divider()
        st.write("### Export-Optionen")
        c_ex, c_cal = st.columns(2)
        
        with c_ex:
            excel_data = create_excel({"Behörde": "Erkannt", "Frist": frist_demo, "Zusammenfassung": ergebnis_demo})
            st.download_button("📊 Excel (Auto-Breite)", excel_data, "Amtsschimmel_Analyse.xlsx", use_container_width=True)
        
        with c_cal:
            ics_data = create_ics_manual(ergebnis_demo, frist_demo)
            st.download_button("📅 Kalender-Frist", ics_data, "Frist.ics", use_container_width=True)

# --- 4. UNTERER BEREICH: VORLAGEN & RECHTLICHES ---
st.write("")
st.divider()

col_v, col_r = st.columns(2)

with col_v:
    st.subheader("📝 Vorlagen")
    with st.expander("Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")
    with st.expander("Widerspruch einlegen (Fristwahrend)"):
        st.code("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]")
    with st.expander("Akteneinsicht einfordern"):
        st.code("Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

with col_r:
    st.subheader("⚖️ Rechtliches")
    tab1, tab2, tab3 = st.tabs(["Impressum", "Datenschutz", "FAQ"])
    
    with tab1:
        st.text("""Amtsschimmel-Killer
Betreiberin: Elisabeth Reinecke
Ringelsweide 9, 40223 Düsseldorf

Kontakt:
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

Haftung:
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")
        
    with tab2:
        st.markdown("""
        **1. Datenschutz auf einen Blick**
        Wir behandeln Ihre personenbezogenen Daten vertraulich (DSGVO).
        **2. Datenerfassung & Hosting**
        Diese App wird auf Streamlit Cloud gehostet. 
        **3. Dokumentenverarbeitung**
        Übertragung per TLS an OpenAI. Keine dauerhafte Speicherung.
        **4. Zahlungsabwicklung**
        Abwicklung über Stripe.
        **5. Ihre Rechte**
        Auskunft/Löschung unter amtsschimmel-killer@proton.me.
        """)
        
    with tab3:
        st.markdown("""
        **Ist das ein Abonnement?**
        Nein. Jede Zahlung ist eine Einmalzahlung.
        **Wie sicher sind meine Dokumente?**
        Verschlüsselt an OpenAI, danach sofortige Löschung.
        **Ersetzt die App eine Rechtsberatung?**
        Nein. Nur Formulierungshilfe.
        **Was passiert, wenn der Scan fehlschlägt?**
        Es wird kein Guthaben abgezogen.
        """)

