import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS FÜR PAKETE (Button-Integration & Design) ---
st.markdown("""
<style>
    .pkg-container {
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        text-align: center;
        border: 1px solid #ddd;
    }
    .pkg-name { font-size: 0.9em; font-weight: bold; margin-bottom: 5px; height: 40px; }
    .pkg-price { font-size: 22px; font-weight: bold; color: #1f77b4; margin-bottom: 5px; }
    .pkg-footer { font-size: 0.75em; font-weight: bold; color: #d35400; margin-bottom: 10px; }
    
    /* Button Styling innerhalb der Pakete */
    div.stButton > button {
        width: 100% !important;
        background-color: #1f77b4 !important;
        color: white !important;
        border-radius: 8px !important;
        height: 35px !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN ---
def create_excel_autofit(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 5
            worksheet.set_column(i, i, min(column_len, 50))
    return output.getvalue()

# --- 4. RECHTLICHES & VORLAGEN ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\nBetreiberin: Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with c2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles automatisch vom Hoster erfasst.\n\n3. Dokumentenverarbeitung\nIhre Briefe werden per TLS an OpenAI (USA) zur Analyse übertragen. Keine dauerhafte Speicherung.\n\n4. Zahlungsabwicklung (Stripe)\nStripe erhebt die Daten zur Abrechnung. Wir erhalten nur eine Bestätigung.\n\n5. Ihre Rechte\nAuskunft, Löschung und Sperrung unter amtsschimmel-killer@proton.me.")
with c3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Nur Einmalzahlungen.\n\nWie sicher sind meine Dokumente?\nVerschlüsselte Übertragung, keine dauerhafte Speicherung.\n\nErsetzt die App eine Rechtsberatung?\nNein. Nur Formulierungshilfe.\n\nWas passiert bei Fehlern?\nKein Abzug von Guthaben bei technischem Scheitern.")
with c4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nIch bitte um Verlängerung der Frist bis zum [Datum]...\Widerspruch:\nHiermit lege ich Widerspruch gegen den Bescheid vom [Datum] ein...\nAkteneinsicht:\nIch beantrage Akteneinsicht gemäß § 25 SGB X.")

st.divider()

# --- 5. HAUPT-LAYOUT (Zwei Spalten: Pakete links, Upload rechts) ---
col_sidebar, col_main = st.columns([1, 2.5])

with col_sidebar:
    try: st.image("icon_final_blau.png", width=140)
    except: st.subheader("🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "AR العربية"], label_visibility="collapsed")
    
    st.markdown("### 💳 Scans")
    
    # Paket 1
    st.markdown('<div class="pkg-container" style="background-color: #f9f9f9;">'
                '<div class="pkg-name">📄 Analyse<br>(1 Dokument)</div>'
                '<div class="pkg-price">3,99 €</div>'
                '<div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")

    # Paket 2
    st.markdown('<div class="pkg-container" style="background-color: #ebf5fb; border-color: #3498db;">'
                '<div class="pkg-name">🥈 Spar-Paket<br>(3 Dokumente)</div>'
                '<div class="pkg-price">9,99 €</div>'
                '<div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")

    # Paket 3
    st.markdown('<div class="pkg-container" style="background-color: #fef9e7; border-color: #f1c40f;">'
                '<div class="pkg-name">🥇 Sorglos-Paket<br>(10 Dokumente)</div>'
                '<div class="pkg-price">19,99 €</div>'
                '<div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")

with col_main:
    st.markdown("### 📤 Upload & Analyse")
    st.success("👑 Admin Guthaben: 999 Scans")
    
    uploaded_file = st.file_uploader("Datei hier reinziehen oder klicken", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        st.divider()
        res_v, res_t = st.columns([1, 1.2])
        
        with res_v:
            st.markdown("#### 🖼️ Vorschau")
            if uploaded_file.type == "application/pdf":
                st.info("PDF geladen.")
            else:
                st.image(uploaded_file, use_container_width=True)
        
        with res_t:
            st.markdown("#### 🔍 Ergebnisse")
            st.error("📅 **Frist: 24.12.2024**")
            
            with st.container(border=True):
                st.markdown("**📖 Glossar:**")
                st.write("Verwaltungsakt: Maßnahme einer Behörde.")
            
            with st.container(border=True):
                st.markdown("**✍️ Antwortentwurf:**")
                antwort = "Sehr geehrte Damen und Herren,\nhiermit lege ich Widerspruch ein..."
                st.code(antwort, language="text")
        
        st.divider()
        st.markdown("#### 📥 Downloads")
        d1, d2, d3, d4 = st.columns(4)
        with d1: 
            st.download_button("📄 PDF Brief", antwort, "Antwort.pdf", use_container_width=True)
        with d2:
            ex = create_excel_autofit({"Frist": "24.12.2024", "Thema": "Widerspruch"})
            st.download_button("📊 Excel", ex, "Analyse.xlsx", use_container_width=True)
        with d3:
            st.download_button("📝 Word", antwort, "Antwort.doc", use_container_width=True)
        with d4:
            st.download_button("📅 Termin", "BEGIN:VCALENDAR...", "Frist.ics", use_container_width=True)
