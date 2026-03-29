import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- 1. SEITEN-LAYOUT ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide")

# --- 2. SICHERE EXPORT-FUNKTIONEN ---
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

# --- 3. RECHTLICHES GANZ OBEN (Zusammengeklappt) ---
col_re_1, col_re_2, col_re_3, col_re_4 = st.columns(4)

with col_re_1:
    with st.expander("⚖️ Impressum"):
        st.text("""Amtsschimmel-Killer
Betreiberin: Elisabeth Reinecke
Ringelsweide 9, 40223 Düsseldorf

Kontakt:
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

Haftung:
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")

with col_re_2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""
        **1. Datenschutz auf einen Blick**  
        Wir behandeln Ihre personenbezogenen Daten vertraulich (DSGVO).
        **2. Datenerfassung & Hosting**  
        Betrieb auf Streamlit Cloud. Logfiles werden automatisch erfasst.
        **3. Dokumentenverarbeitung**  
        Übertragung per TLS an OpenAI (USA). Keine Speicherung auf unseren Servern.
        **4. Zahlungsabwicklung (Stripe)**  
        Weiterleitung zu Stripe für Abrechnung.
        **5. Ihre Rechte**  
        Auskunft/Löschung: amtsschimmel-killer@proton.me
        """)

with col_re_3:
    with st.expander("❓ FAQ"):
        st.markdown("""
        **Ist das ein Abonnement?**  
        Nein. Jede Zahlung ist eine Einmalzahlung.
        **Wie sicher sind meine Dokumente?**  
        Verschlüsselt an OpenAI, danach Löschung aus dem Arbeitsspeicher.
        **Ersetzt die App eine Rechtsberatung?**  
        Nein. Wir bieten eine Formulierungshilfe.
        **Was passiert, wenn der Scan fehlschlägt?**  
        Kein Guthaben-Abzug bei technischen Fehlern.
        """)

with col_re_4:
    with st.expander("📝 Vorlagen"):
        st.markdown("**Fristverlängerung:**")
        st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")
        st.markdown("**Widerspruch (Fristwahrend):**")
        st.code("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]")
        st.markdown("**Akteneinsicht:**")
        st.code("Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

st.divider()

# --- 4. HAUPT-LAYOUT (Drei Spalten-System) ---
col_left, col_mid, col_right = st.columns([1, 1.5, 1.5])

# LINKS: Sprachen & Pakete
with col_left:
    st.markdown("### 🌐 Sprachen")
    sprachen = ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "AR العربية", "FR Français", "IT Italiano", "ES Español"]
    st.selectbox("Sprache wählen", sprachen, label_visibility="collapsed")
    
    st.write("") 
    st.image("https://cdn-icons-png.flaticon.com", width=70) # Dein Logo
    st.caption("Amtsschimmel-Killer")

    # Pakete exakt wie im Screenshot
    with st.container(border=True):
        st.markdown("📄 **Analyse** (1 Dok.)")
        st.markdown("Einmalpreis **3,99 €**\n\n❌ KEIN ABO")
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", use_container_width=True)

    with st.container(border=True):
        st.markdown("📦 **Spar Paket** (3 Dok.)")
        st.markdown("Einmalpreis **9,99 €**\n\n❌ KEIN ABO")
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)

    with st.container(border=True):
        st.markdown("🚀 **Sorglos Paket** (10 Dok.)")
        st.markdown("Einmalpreis **19,99 €**\n\n❌ KEIN ABO")
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04", use_container_width=True)

# MITTE: Upload & Vorschau
with col_mid:
    st.markdown("### 📑 Upload & Vorschau")
    st.success("Guthaben: 999 Dokumente")
    uploaded_file = st.file_uploader("Drag and drop file here", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)

# RECHTS: Analyse & Antwort
with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    antwort_text = "Hier erscheint das Ergebnis nach dem Scan."
    frist_datum = "24.12.2024" # Platzhalter
    st.info(antwort_text)
    
    if uploaded_file:
        st.divider()
        c_ex, c_cal = st.columns(2)
        with c_ex:
            excel_data = create_excel({"Analyse": antwort_text, "Frist": frist_datum})
            st.download_button("📊 Excel (Auto-Spalten)", excel_data, "Analyse.xlsx", use_container_width=True)
        with c_cal:
            ics_data = create_ics_manual(antwort_text, frist_datum)
            st.download_button("📅 Frist in Kalender", ics_data, "Frist.ics", use_container_width=True)
