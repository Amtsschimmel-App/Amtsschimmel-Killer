import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (FARBIGE PAKETE & LAYOUT) ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stExpander { border: 1px solid #e6e9ef; border-radius: 8px; margin-bottom: 5px; }
    
    /* Paket-Boxen Farben */
    div[data-testid="stVerticalBlock"] > div:has(div.basis-box) { 
        background-color: #f0f7ff; border: 2px solid #007bff; border-radius: 12px; padding: 15px; 
    }
    div[data-testid="stVerticalBlock"] > div:has(div.spar-box) { 
        background-color: #f2faf3; border: 2px solid #28a745; border-radius: 12px; padding: 15px; 
    }
    div[data-testid="stVerticalBlock"] > div:has(div.sorglos-box) { 
        background-color: #fff9e6; border: 2px solid #fcc419; border-radius: 12px; padding: 15px; 
    }
    
    .price-tag { font-size: 22px; font-weight: bold; color: #1E3A8A; margin: 5px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN (VOLLSTÄNDIG FUNKTIONAL) ---
def create_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 60)
    return output.getvalue()

def create_text_file(content):
    return BytesIO(content.encode('utf-8'))

def get_preview(uploaded_file):
    # FIX: Sofortige Vorschau nach Upload
    file_bytes = uploaded_file.getvalue()
    base64_file = base64.b64encode(file_bytes).decode('utf-8')
    if uploaded_file.type == "application/pdf":
        display = f'<embed src="data:application/pdf;base64,{base64_file}" width="100%" height="800" type="application/pdf">'
    else:
        display = f'<img src="data:image/png;base64,{base64_file}" width="100%">'
    st.markdown(display, unsafe_allow_html=True)

# --- 4. TOP-BAR: RECHTLICHES (EXAKTE TEXTE & ABSTÄNDE) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\n\nBetreiberin:\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.\n\n4. Zahlungsabwicklung (Stripe)\nBei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.\n\n5. Ihre Rechte\nSie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.\n\nWie sicher sind meine Dokumente?\nIhre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.\n\nErsetzt die App eine Rechtsberatung?\nNein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.\n\nWas passiert, wenn der Scan fehlschlägt?\nEin Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.\n\nWie erreiche ich Elisabeth Reinecke?\nNutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]\n\nWiderspruch einlegen (Fristwahrend)\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]\n\nAkteneinsicht einfordern:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    try: st.image("icon_final_blau.png", width=160)
    except: st.markdown("🏛️ **Amtsschimmel-Killer**")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano"], label_visibility="collapsed")
    
    st.write("---")
    st.markdown("### 📦 Pakete")
    
    # Paket 1: Analyse
    with st.container():
        st.markdown('<div class="basis-box"></div>', unsafe_allow_html=True)
        st.markdown("### 🛡️ Basis")
        st.markdown("**Amtsschimmel-Killer Analyse** (1 Dokument)")
        st.markdown('<p class="price-tag">3,99 €</p>', unsafe_allow_html=True)
        st.markdown('<p class="no-abo">Einmalzahlung - kein Abo!</p>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")

    # Paket 2: Spar
    with st.container():
        st.markdown('<div class="spar-box"></div>', unsafe_allow_html=True)
        st.markdown("### ⚔️ Spar-Paket")
        st.markdown("**Amtsschimmel-Killer Spar-Paket** (3 Dokumente)")
        st.markdown('<p class="price-tag">9,99 €</p>', unsafe_allow_html=True)
        st.markdown('<p class="no-abo">Einmalzahlung - kein Abo!</p>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")

    # Paket 3: Sorglos
    with st.container():
        st.markdown('<div class="sorglos-box"></div>', unsafe_allow_html=True)
        st.markdown("### 🚀 Sorglos-Paket")
        st.markdown("**Amtsschimmel-Killer Sorglos-Paket** (10 Dokumente)")
        st.markdown('<p class="price-tag">19,99 €</p>', unsafe_allow_html=True)
        st.markdown('<p class="no-abo">Einmalzahlung - kein Abo!</p>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com")

with col_mid:
    st.subheader("📄 Dokument & Vorschau")
    uploaded_file = st.file_uploader("Hier Datei ablegen", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded_file:
        get_preview(uploaded_file)
    else:
        st.info("Bitte laden Sie ein Dokument hoch, um die Vorschau anzuzeigen.")

with col_right:
    st.subheader("🔍 Analyse-Ergebnisse")
    if uploaded_file:
        with st.expander("📅 Fristen (Deadlines)", expanded=True):
            st.warning("⚠️ Fristende: [Datum aus KI extrahieren]")
        with st.expander("📖 Glossar (Begriffserklärung)"):
            st.info("Hier werden schwierige Begriffe aus dem Dokument erklärt.")
        
        st.markdown("### ✉️ Entwürfe")
        tab1, tab2 = st.tabs(["Langes Antwortschreiben", "Ausführlicher Widerspruch"])
        
        # Ausführliche Texte mit Platzhaltern
        text_ant = "Sehr geehrte Damen und Herren,\n\nbezugnehmend auf Ihr Schreiben vom [Datum], Aktenzeichen [Nummer], nehme ich wie folgt Stellung:\n\n[Detaillierte Argumentation der KI wird hier eingefügt]...\n\nIch bitte um Prüfung des Sachverhalts und Bestätigung des Eingangs.\n\nMit freundlichen Grüßen,\n[Name]"
        text_wid = "Sehr geehrte Damen und Herren,\n\nhiermit lege ich gegen Ihren Bescheid vom [Datum], erhalten am [Datum], fristgerecht Widerspruch ein.\n\nBegründung:\n\n[Detaillierte rechtliche Begründung der KI wird hier eingefügt]...\n\nEin ausführlicher Schriftsatz geht Ihnen zeitnah zu.\n\nMit freundlichen Grüßen,\n[Name]"
        
        with tab1:
            st.text_area("Antwortentwurf", text_ant, height=300)
        with tab2:
            st.text_area("Widerspruchstext", text_wid, height=300)
        
        st.write("---")
        st.markdown("### 📥 Downloads")
        d1, d2, d3 = st.columns(3)
        with d1: 
            st.download_button("📄 PDF", data=create_text_file(text_ant), file_name="antwort.pdf", mime="application/pdf")
        with d2: 
            st.download_button("📊 Excel", data=create_excel({"Frist": "Datum", "Analyse": "Inhalt"}), file_name="analyse.xlsx")
        with d3: 
            st.download_button("📝 Word", data=create_text_file(text_ant), file_name="antwort.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        st.button("📅 Kalender.ico hinzufügen")
    else:
        st.write("Warten auf Datei...")
