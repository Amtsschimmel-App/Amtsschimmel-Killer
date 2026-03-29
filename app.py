import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (Buttons IN Paketen, Layout-Fix) ---
st.markdown("""
<style>
    .pkg-box {
        padding: 20px; border-radius: 15px; border: 1px solid #ddd;
        text-align: center; margin-bottom: 0px; min-height: 220px;
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .pkg-name { font-size: 0.95em; font-weight: bold; color: #2c3e50; }
    .pkg-price { font-size: 24px; font-weight: bold; color: #1f77b4; margin: 10px 0; }
    .pkg-footer { font-size: 0.75em; font-weight: bold; color: #d35400; margin-bottom: 15px; }
    
    /* Button direkt in die Box optisch integrieren */
    div.stButton > button {
        width: 100% !important; border-radius: 8px !important;
        background-color: #1f77b4 !important; color: white !important;
    }
    .stDownloadButton > button { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN ---
def create_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 10
            worksheet.set_column(i, i, min(column_len, 60))
    return output.getvalue()

def display_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 4. RECHTLICHES & VORLAGEN ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\nBetreiberin: Elisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with c2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern.\n\n4. Zahlungsabwicklung (Stripe)\nStripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung.\n\n5. Ihre Rechte\nSie haben das Recht auf Auskunft, Löschung und Sperrung unter amtsschimmel-killer@proton.me.")
with c3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Keine automatische Verlängerung.\n\nWie sicher sind meine Dokumente?\nÜbertragung TLS-verschlüsselt, Verarbeitung im RAM, keine dauerhafte Speicherung.\n\nErsetzt die App eine Rechtsberatung?\nNein. Nur Formulierungshilfe.\n\nWas passiert, wenn der Scan fehlschlägt?\nKein Guthabenabzug bei technischem Scheitern.")
with c4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]\n\nWiderspruch einlegen:\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben.\n\nAkteneinsicht:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht.")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_side, col_main = st.columns([1, 2.5])

with col_side:
    try: st.image("icon_final_blau.png", width=160)
    except: st.title("🏛️ Amtsschimmel-Killer")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache wählen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "FR Français", "ES Español", "IT Italiano"], label_visibility="collapsed")
    
    st.markdown("### 💳 Scans")
    
    # Paket 1
    st.markdown('<div class="pkg-box" style="background-color: #f9f9f9;"><div class="pkg-name">Amtsschimmel-Paket:<br>Basis (1 Dokument)</div><div class="pkg-price">3,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    st.markdown('</div>', unsafe_allow_html=True)

    # Paket 2
    st.markdown('<div class="pkg-box" style="background-color: #ebf5fb; border: 1px solid #3498db;"><div class="pkg-name">Amtsschimmel-Paket:<br>Spar (3 Dokumente)</div><div class="pkg-price">9,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    st.markdown('</div>', unsafe_allow_html=True)

    # Paket 3
    st.markdown('<div class="pkg-box" style="background-color: #fef9e7; border: 1px solid #f1c40f;"><div class="pkg-name">Amtsschimmel-Paket:<br>Sorglos (10 Dokumente)</div><div class="pkg-price">19,99 €</div><div class="pkg-footer">EINMALZAHLUNG • KEIN ABO</div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04")
    st.markdown('</div>', unsafe_allow_html=True)

with col_main:
    st.markdown("### 📥 Dokument hochladen")
    st.success("👑 Admin Guthaben: 999 Scans")
    
    up_file = st.file_uploader("Hier klicken oder Datei reinziehen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if up_file:
        st.divider()
        c_left, c_right = st.columns([1.2, 1.3])
        
        with c_left:
            st.markdown("#### 🖼️ Dokumenten-Vorschau")
            if up_file.type == "application/pdf":
                display_pdf(up_file)
            else:
                st.image(up_file, use_container_width=True)
        
        with c_right:
            st.markdown("#### 🔍 Ausführliche Analyse")
            st.error("📅 **Frist erkannt: 24.12.2024**")
            
            with st.container(border=True):
                st.markdown("**📖 Ausführliches Glossar:**")
                st.write("""
                - **Ermessensspielraum:** Die Behörde darf innerhalb eines gewissen Rahmens selbst entscheiden.
                - **Rechtsbehelfsbelehrung:** Erklärt, wie und wo Sie Widerspruch einlegen können.
                - **Mitwirkungspflicht:** Sie sind verpflichtet, angeforderte Unterlagen einzureichen, sonst darf die Behörde Leistungen versagen.
                """)
            
            with st.container(border=True):
                st.markdown("**✍️ Ausführliches Antwortschreiben:**")
                ausfuehrliche_antwort = """Sehr geehrte Damen und Herren,

Bezugnehmend auf Ihr Schreiben vom [Datum], Aktenzeichen [Nummer], nehme ich wie folgt Stellung:

Gegen den oben genannten Bescheid lege ich hiermit form- und fristgerecht WIDERSPRUCH ein.

Begründung:
Nach meiner ersten Prüfung beruht Ihre Entscheidung auf einer unvollständigen Sachverhaltsaufklärung. Die von Ihnen angeforderten Unterlagen liegen mir teilweise noch nicht vor, wurden aber bereits angefordert. 

Zudem beantrage ich hiermit vorsorglich Akteneinsicht gemäß § 25 SGB X, um die Entscheidungsgrundlage im Detail nachvollziehen zu können. Ich bitte um Bestätigung des Eingangs sowie um Aussetzung der Vollziehung, bis über den Widerspruch abschließend entschieden wurde.

Mit freundlichen Grüßen,
[Ihr Name]"""
                st.code(ausfuehrliche_antwort, language="text")
            
            st.divider()
            st.markdown("#### 📥 Download Bereich")
            d1, d2, d3, d4 = st.columns(4)
            with d1: st.download_button("📄 PDF Brief", ausfuehrliche_antwort, "Antwort.pdf")
            with d2:
                ex = create_excel({"Frist": "24.12.2024", "Betreff": "Widerspruch", "Status": "Dringend"})
                st.download_button("📊 Excel (Auto)", ex, "Analyse.xlsx")
            with d3: st.download_button("📝 Word (.doc)", ausfuehrliche_antwort, "Antwort.doc")
            with d4: st.download_button("📅 Termin", "BEGIN:VCALENDAR\nSUMMARY:Amtsschimmel Frist\nDTSTART:20241224T090000\nEND:VEVENT\nEND:VCALENDAR", "Frist.ics")
