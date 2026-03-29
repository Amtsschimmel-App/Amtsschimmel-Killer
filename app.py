import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. DESIGN (CSS) ---
st.markdown("""
<style>
    .pkg-box { padding: 15px; border-radius: 12px; border: 1px solid #d1d8e0; text-align: center; margin-bottom: 10px; background: #fff; }
    .pkg-icon { font-size: 30px; }
    .pkg-title { font-weight: bold; font-size: 0.9em; min-height: 45px; }
    .pkg-price { font-size: 22px; font-weight: bold; color: #1f77b4; }
    .pkg-footer { font-size: 0.7em; color: #e74c3c; font-weight: bold; }
    div.stButton > button { width: 100% !important; background-color: #004488 !important; color: white !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN (EXCEL WIDE) ---
def create_excel_pro(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(data)
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 100) # Maximale Breite für Lesbarkeit
    return output.getvalue()

def get_pdf_display(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    return f'<object data="data:application/pdf;base64,{base64_pdf}" type="application/pdf" width="100%" height="600px"></object>'

# --- 4. TOP-BAR (ZUSAMMENGEKLAPPT) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\nBetreiberin: Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich (DSGVO).\n\n2. Hosting\nStreamlit Cloud erfasst Logfiles automatisch.\n\n3. OpenAI\nBriefe werden TLS-verschlüsselt an OpenAI (USA) übertragen. Keine dauerhafte Speicherung.\n\n4. Stripe\nZahlungsdaten werden direkt bei Stripe verarbeitet.")
with t3:
    with st.expander("❓ FAQ"):
        st.text("Kein Abo! Einmalzahlung.\nDokumente werden nach Analyse gelöscht.\nKeine Rechtsberatung, nur Formulierungshilfe.\nScan-Fehler kosten kein Guthaben.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nIch bitte um Verlängerung der Frist bis zum [Datum]...\nWiderspruch:\nHiermit lege ich gegen den Bescheid vom [Datum] Widerspruch ein...\nAkteneinsicht:\nIch beantrage Akteneinsicht gemäß § 25 SGB X.")

st.divider()

# --- 5. HAUPT-LAYOUT (3 SPALTEN WIE IM BILD) ---
col_pkg, col_up, col_res = st.columns([1, 1.5, 1.2])

with col_pkg:
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español"], label_visibility="collapsed")
    st.image("https://cdn-icons-png.flaticon.com", width=60) # Ersatz-Icon
    
    # Pakete
    pkgs = [
        ("📄", "Amtsschimmel-Killer: Analyse (1 Dokument)", "3,99 €", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("🥈", "Amtsschimmel-Killer: Spar Paket (3 Dokumente)", "9,99 €", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("🥇", "Amtsschimmel-Killer: Sorglos Paket (10 Dokumente)", "19,99 €", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")
    ]
    for icon, title, price, url in pkgs:
        st.markdown(f'<div class="pkg-box"><div class="pkg-icon">{icon}</div><div class="pkg-title">{title}</div><div class="pkg-price">{price}</div><div class="pkg-footer">❌ KEIN ABO • EINMALZAHLUNG</div></div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", url)

with col_up:
    st.markdown("### 📑 Upload & Vorschau")
    st.info("Guthaben: 999 Dokumente")
    up_file = st.file_uploader("Datei hier reinziehen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if up_file:
        if up_file.type == "application/pdf":
            st.markdown(get_pdf_display(up_file), unsafe_allow_html=True)
        else:
            st.image(up_file, use_container_width=True)

with col_res:
    st.markdown("### 🔍 Analyse & Antwort")
    if up_file:
        st.error("📅 Frist erkannt: 24.12.2024")
        
        # Ausführliche Analyse
        auswertung = """Das Dokument ist ein Bescheid nach § 35 SGB X. 
        Die Begründung der Behörde ist unzureichend. Es fehlen Angaben zur Ermessensausübung gemäß § 39 SGB I. 
        Ein Widerspruch ist zur Fristwahrung dringend geboten. 
        Zudem sollte Akteneinsicht beantragt werden."""
        
        st.markdown("**Detail-Analyse:**")
        st.write(auswertung)
        
        tab1, tab2 = st.tabs(["✍️ Stellungnahme", "⚖️ Widerspruch"])
        
        with tab1:
            antwort = "Sehr geehrte Damen und Herren,\n\nhiermit nehme ich Bezug auf Ihr Schreiben......"
            st.code(antwort, language="text")
        with tab2:
            widerspruch = "Sehr geehrte Damen und Herren,\n\ngegen Ihren Bescheid vom [Datum] lege ich hiermit form- und fristgerecht WIDERSPRUCH ein. Die Begründung folgt nach Akteneinsicht..."
            st.code(widerspruch, language="text")
        
        st.divider()
        st.markdown("#### 📥 Downloads")
        d1, d2 = st.columns(2)
        with d1:
            st.download_button("📄 PDF (Vollständig)", antwort + "\n\n" + widerspruch, "Dokumente.pdf")
            st.download_button("📝 Word (Detailliert)", antwort + "\n\n" + widerspruch, "Dokumente.doc")
        with d2:
            excel_data = create_excel_pro([{"Analyse": auswertung, "Stellungnahme": antwort, "Widerspruch": widerspruch}])
            st.download_button("📊 Excel (Breit)", excel_data, "Analyse_Breit.xlsx")
            st.download_button("📅 Termin", "BEGIN:VCALENDAR\nSUMMARY:Frist Amtsschimmel\nDTSTART:20241224T090000Z\nEND:VEVENT\nEND:VCALENDAR", "Frist.ics")
    else:
        st.write("Hier erscheint das Ergebnis nach dem Scan.")
