import streamlit as st
import pandas as pd
from io import BytesIO
from ics import Calendar, Event
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="centered")

# --- HILFSFUNKTIONEN (EXCEL & KALENDER) ---
def create_excel(data_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data_dict])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        # Automatisches Anpassen der Spaltenbreite
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(column_len, 60))
    return output.getvalue()

def create_ics(summary, date_str):
    c = Calendar()
    e = Event()
    e.name = "Amtsschimmel-Frist"
    try:
        e.begin = datetime.strptime(date_str, "%d.%m.%Y")
    except:
        e.begin = datetime.now()
    e.description = summary
    e.make_all_day()
    c.events.add(e)
    return str(c)

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

# --- HAUPTFUNKTION (BEISPIEL-LOGIK) ---
# Hier steht normalerweise dein Datei-Upload und die OpenAI-Abfrage
# Zur Demonstration nehmen wir an, die KI hat folgendes gefunden:
analyse_beispiel = {
    "Behörde": "Beispielbehörde",
    "Frist": "24.12.2024",
    "Wichtigste Info": "Widerspruch einlegen innerhalb eines Monats."
}

st.subheader("Analyse & Export")
c1, c2 = st.columns(2)

with c1:
    excel_file = create_excel(analyse_beispiel)
    st.download_button("📊 Excel mit Auto-Spalten", excel_file, "Analyse.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with c2:
    ics_file = create_ics(analyse_beispiel["Wichtigste Info"], analyse_beispiel["Frist"])
    st.download_button("📅 Termin in Kalender", ics_file, "Frist.ics", "text/calendar")

st.divider()

# --- VORLAGEN ---
st.subheader("📝 Vorlagen")
with st.expander("Fristverlängerung"):
    st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")

with st.expander("Widerspruch einlegen (Fristwahrend)"):
    st.code("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]")

with st.expander("Akteneinsicht einfordern"):
    st.code("Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

# --- RECHTLICHES & FAQ ---
st.divider()
tab_imp, tab_dat, tab_faq = st.tabs(["Impressum", "Datenschutz", "FAQ"])

with tab_imp:
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

with tab_dat:
    st.markdown("""
    1. **Datenschutz auf einen Blick**  
    Wir behandeln Ihre personenbezogenen Daten vertraulich... (etc.)
    
    2. **Datenerfassung & Hosting**  
    Diese App wird auf Streamlit Cloud gehostet...
    
    3. **Dokumentenverarbeitung**  
    Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) übertragen...
    
    4. **Zahlungsabwicklung (Stripe)**  
    Bei Käufen werden Sie zu Stripe weitergeleitet...
    
    5. **Ihre Rechte**  
    Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten.
    """)

with tab_faq:
    st.markdown("""
    **Ist das ein Abonnement?**  
    Nein. Wir hassen Abos genauso wie Amtsschimmel...
    
    **Wie sicher sind meine Dokumente?**  
    Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen...
    
    **Ersetzt die App eine Rechtsberatung?**  
    Nein. Wir bieten eine Formulierungshilfe...
    
    **Was passiert, wenn der Scan fehlschlägt?**  
    Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat...
    
    **Wie erreiche ich Elisabeth Reinecke?**  
    Nutzen Sie einfach die E-Mail oder Telefonnummer im Impressum.
    """)
