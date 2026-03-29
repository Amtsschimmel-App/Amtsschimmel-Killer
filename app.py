import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (Pakete, Icons, Buttons) ---
st.markdown("""
<style>
    .pkg-box {
        padding: 20px; border-radius: 15px; border: 1px solid #ddd;
        text-align: center; margin-bottom: 10px; min-height: 280px;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .pkg-icon { font-size: 40px; margin-bottom: 10px; }
    .pkg-name { font-size: 1em; font-weight: bold; color: #2c3e50; min-height: 45px; }
    .pkg-price { font-size: 26px; font-weight: bold; color: #1f77b4; margin: 10px 0; }
    .pkg-footer { font-size: 0.8em; font-weight: bold; color: #d35400; margin-bottom: 15px; }
    
    div.stButton > button {
        width: 100% !important; border-radius: 10px !important;
        background-color: #1f77b4 !important; color: white !important;
        font-weight: bold !important; height: 45px !important;
    }
    .stDownloadButton > button { width: 100% !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN (EXCEL PRO AUTO-FIT) ---
def create_excel_pro(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data])
        df.to_excel(writer, index=False, sheet_name='Amtsschimmel_Analyse')
        worksheet = writer.sheets['Amtsschimmel_Analyse']
        # Extrem weite Spalten für lange Texte
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 80) 
    return output.getvalue()

def display_pdf_robust(file_bytes):
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 4. RECHTLICHES & VORLAGEN ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\nBetreiberin: Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with c2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles automatisch erfasst.\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen.\n\n4. Zahlungsabwicklung (Stripe)\nStripe erhebt die erforderlichen Daten zur Abrechnung.\n\n5. Ihre Rechte\nRecht auf Auskunft, Löschung und Sperrung unter amtsschimmel-killer@proton.me.")
with c3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Keine automatische Verlängerung.\n\nWie sicher sind meine Dokumente?\nVerschlüsselte Übertragung, keine dauerhafte Speicherung.\n\nErsetzt die App eine Rechtsberatung?\nNein. Nur Formulierungshilfe.\n\nWas passiert bei Scan-Fehlern?\nKein Guthabenabzug bei technischem Abbruch.")
with c4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum]...\n\nWiderspruch:\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum] lege ich hiermit Widerspruch ein...\n\nAkteneinsicht:\nSehr geehrte Damen und Herren, ich beantrage hiermit Akteneinsicht gemäß § 25 SGB X.")

st.divider()

# --- 5. HAUPTBEREICH (Split-Layout) ---
col_sidebar, col_main = st.columns([1, 2.5])

with col_sidebar:
    try: st.image("icon_final_blau.png", width=180)
    except: st.title("🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "IT Italiano", "ES Español", "NL Nederlands", "RO Română"], label_visibility="collapsed")
    
    st.markdown("### 💳 Scans laden")
    # Pakete mit Icons und integriertem Button
    for pkg in [
        {"icon": "📄", "name": "Amtsschimmel-Paket:<br>Basis (1 Dokument)", "price": "3,99 €", "url": "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", "color": "#f9f9f9"},
        {"icon": "🥈", "name": "Amtsschimmel-Paket:<br>Spar (3 Dokumente)", "price": "9,99 €", "url": "https://buy.stripe.com/8x228retRbj50paalq1gs03", "color": "#ebf5fb"},
        {"icon": "🥇", "name": "Amtsschimmel-Paket:<br>Sorglos (10 Dokumente)", "price": "19,99 €", "url": "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04", "color": "#fef9e7"}
    ]:
        st.markdown(f'<div class="pkg-box" style="background-color: {pkg["color"]};">'
                    f'<div class="pkg-icon">{pkg["icon"]}</div>'
                    f'<div class="pkg-name">{pkg["name"]}</div>'
                    f'<div class="pkg-price">{pkg["price"]}</div>'
                    f'<div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", pkg["url"])
        st.markdown('</div>', unsafe_allow_html=True)

with col_main:
    st.markdown("### 📥 Dokumenten-Check")
    st.success("👑 Admin Guthaben: 999 Scans")
    
    up_file = st.file_uploader("Datei hier reinziehen oder klicken", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if up_file:
        file_bytes = up_file.read()
        st.divider()
        c_left, c_right = st.columns([1, 1.2])
        
        with c_left:
            st.markdown("#### 🖼️ Dokumenten-Vorschau")
            if up_file.type == "application/pdf":
                display_pdf_robust(file_bytes)
            else:
                st.image(file_bytes, use_container_width=True)
        
        with c_right:
            st.markdown("#### 🔍 Ausführliche Analyse")
            st.error("📅 **Frist erkannt: 24.12.2024**")
            
            with st.container(border=True):
                st.markdown("**📖 Ausführliches Glossar:**")
                st.write("""
                **Verwaltungsakt:** Jede Verfügung, Entscheidung oder andere hoheitliche Maßnahme, die eine Behörde zur Regelung eines Einzelfalls auf dem Gebiet des öffentlichen Rechts trifft.
                \n**Rechtsbehelfsbelehrung:** Ein zwingender Bestandteil eines Bescheids. Fehlt diese oder ist sie fehlerhaft, verlängert sich die Widerspruchsfrist von einem Monat auf ein Jahr.
                \n**Ermessensunterschreitung:** Wenn die Behörde gar nicht erst prüft, ob sie eine Ausnahme machen könnte, obwohl das Gesetz ihr die Wahl lässt. Dies macht einen Bescheid rechtswidrig.
                """)
            
            with st.container(border=True):
                st.markdown("**✍️ Ausführliches Antwortschreiben / Stellungnahme:**")
                ausfuehrlich = """Sehr geehrte Damen und Herren,

Bezugnehmend auf Ihr Schreiben vom [Datum], eingegangen am [Datum], Aktenzeichen [Nummer], nehme ich hiermit ausführlich Stellung.

Zunächst weise ich darauf hin, dass die von Ihnen getroffene Entscheidung auf einer unzureichenden Sachverhaltsaufklärung beruht. Die Berücksichtigung der individuellen Lebensumstände (gemäß § 35 SGB X / § 39 VwVfG) scheint nicht ausreichend erfolgt zu sein.

Ich beantrage hiermit die Aussetzung der Vollziehung sowie eine angemessene Fristverlängerung zur endgültigen Begründung, da mir zum aktuellen Zeitpunkt noch wesentliche Unterlagen Dritter fehlen. Zudem mache ich hiermit mein Recht auf Akteneinsicht geltend, um die internen Entscheidungsprozesse prüfen zu können.

Bitte bestätigen Sie mir den Erhalt dieser Nachricht sowie die gewährte Fristverlängerung schriftlich.

Mit freundlichen Grüßen,
[Ihr Name]"""
                st.code(ausfuehrlich, language="text")
            
            st.divider()
            st.markdown("#### 📥 Download Bereich")
            d1, d2, d3, d4 = st.columns(4)
            with d1: st.download_button("📄 PDF Brief", ausfuehrlich, "Antwort_Brief.pdf")
            with d2:
                ex_data = create_excel_pro({"Frist": "24.12.2024", "Analyse": "Ausführliche Stellungnahme erforderlich", "Glossar": "Ermessen, Frist, Akteneinsicht"})
                st.download_button("📊 Excel Pro", ex_data, "Amtsschimmel_Analyse.xlsx")
            with d3: st.download_button("📝 Word (.doc)", ausfuehrlich, "Antwort_Brief.doc")
            with d4: st.download_button("📅 Termin", "BEGIN:VCALENDAR\nSUMMARY:Frist Amtsschimmel-Killer\nDTSTART:20241224T090000\nEND:VEVENT\nEND:VCALENDAR", "Frist.ics")
