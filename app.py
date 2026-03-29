import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- SEITENKONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="centered")

# --- HILFSFUNKTIONEN (Sicherer Export ohne Absturz-Gefahr) ---
def create_excel(data_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data_dict])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        # Automatische Spaltenbreite berechnen
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(column_len, 60))
    return output.getvalue()

def create_ics_manual(summary, date_str):
    # Formatiert das Datum für den Kalender (YYYYMMDD)
    clean_date = "".join(filter(str.isdigit, date_str)) 
    if len(clean_date) == 8:
        formatted_date = f"{clean_date[4:]}{clean_date[2:4]}{clean_date[:2]}"
    else:
        formatted_date = datetime.now().strftime("%Y%m%d")
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART;VALUE=DATE:{formatted_date}
SUMMARY:Amtsschimmel-Frist: {summary[:30]}...
DESCRIPTION:{summary}
END:VEVENT
END:VCALENDAR"""
    return ics_content

# --- HEADER & STRIPE PAKETE ---
st.title("🏛️ Amtsschimmel-Killer")
st.markdown("### Wähle dein Paket:")

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    st.link_button("🥉 3 Scans - 3,99€", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
with col_p2:
    st.link_button("🥈 10 Scans - 9,99€", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
with col_p3:
    st.link_button("🥇 25 Scans - 19,99€", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")

st.divider()

# --- ANALYSE-BEREICH (Beispielwerte) ---
# Hier greift normalerweise dein KI-Ergebnis
analyse_ergebnis = {
    "Behörde": "Finanzamt Düsseldorf",
    "Frist": "24.12.2024",
    "Handlung": "Widerspruch einlegen"
}

st.subheader("Analyse-Export")
c1, c2 = st.columns(2)
with c1:
    excel_data = create_excel(analyse_ergebnis)
    st.download_button("📊 Excel (Auto-Spalten)", excel_data, "Analyse.xlsx")
with c2:
    ics_data = create_ics_manual(analyse_ergebnis["Handlung"], analyse_ergebnis["Frist"])
    st.download_button("📅 Kalender-Termin", ics_data, "Frist.ics")

st.divider()

# --- VORLAGEN ---
st.subheader("📝 Vorlagen")
with st.expander("Fristverlängerung"):
    st.write("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")

with st.expander("Widerspruch einlegen (Fristwahrend)"):
    st.write("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]")

with st.expander("Akteneinsicht einfordern"):
    st.write("Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

# --- IMPRESSUM, DATENSCHUTZ, FAQ (Deine Texte 1:1 übernommen) ---
st.divider()

st.markdown("### Impressum:")
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

st.divider()

st.markdown("### Datenschutz:")
with st.expander("Details anzeigen"):
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

st.divider()

st.markdown("### FAQ")
with st.expander("Häufige Fragen"):
    st.markdown("""
    **Ist das ein Abonnement?**
    Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.
    
    **Wie sicher sind meine Dokumente?**
    Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert.
    
    **Ersetzt die App eine Rechtsberatung?**
    Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.
    
    **Was passiert, wenn der Scan fehlschlägt?**
    Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat.
    
    **Wie erreiche ich Elisabeth Reinecke?**
    Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
    """)
