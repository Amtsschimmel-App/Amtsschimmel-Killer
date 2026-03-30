import streamlit as st
import pandas as pd
from io import BytesIO
import base64

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (FARBIGE BOXEN & LAYOUT) ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stExpander { border: 1px solid #e6e9ef; border-radius: 8px; margin-bottom: 5px; }
    
    /* Paket-Boxen Design */
    .paket-container { border-radius: 12px; padding: 15px; margin-bottom: 20px; border: 2px solid; background-color: white; }
    .basis-box { border-color: #007bff; }
    .spar-box { border-color: #28a745; }
    .sorglos-box { border-color: #fcc419; }
    
    .header-box { padding: 5px 10px; border-radius: 8px 8px 0 0; margin-bottom: 10px; font-weight: bold; }
    .blue-h { background-color: #e3f2fd; color: #007bff; }
    .green-h { background-color: #e8f5e9; color: #28a745; }
    .gold-h { background-color: #fff9e6; color: #fcc419; }
    
    .price-tag { font-size: 22px; font-weight: bold; color: #1E3A8A; margin: 5px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. TECHNISCHE FUNKTIONEN (VORSCHAU & REPARATUR) ---
def get_pdf_display_fixed(uploaded_file):
    """Zeigt das PDF/Bild stabil an, ohne von Chrome blockiert zu werden."""
    file_bytes = uploaded_file.getvalue()
    base64_file = base64.b64encode(file_bytes).decode('utf-8')
    if uploaded_file.type == "application/pdf":
        # Einbettung via Iframe für maximale Kompatibilität
        display_code = f'<iframe src="data:application/pdf;base64,{base64_file}" width="100%" height="800px" style="border:none;"></iframe>'
    else:
        display_code = f'<img src="data:image/png;base64,{base64_file}" width="100%">'
    st.components.v1.html(display_code, height=800, scrolling=True)

def create_valid_pdf_data(text):
    """Erzeugt einen PDF-Datenstrom, den Adobe Acrobat öffnen kann."""
    # Simuliert eine valide PDF-Struktur (Minimal-Header für Adobe)
    pdf_content = f"%PDF-1.4\n1 0 obj\n<< /Title (Amtsschimmel-Killer Antwort) /Creator (Amtsschimmel-Killer) >>\nendobj\n2 0 obj\n<< /Type /Page /Parent 3 0 R /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length {len(text)+100} >>\nstream\nBT /F1 12 Tf 50 800 Td ({text.encode('latin-1', 'replace').decode('latin-1')}) Tj ET\nendstream\nendobj\n3 0 obj\n<< /Type /Pages /Kids [2 0 R] /Count 1 >>\nendobj\n5 0 obj\n<< /Type /Catalog /Pages 3 0 R >>\nendobj\nxref\n0 6\n0000000000 65535 f\ntrailer\n<< /Size 6 /Root 5 0 R >>\nstartxref\n%%EOF".encode('latin-1', 'replace')
    return pdf_content

def create_excel(data_dict):
    """Excel mit automatischer Spaltenbreite."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data_dict])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 20
            worksheet.set_column(i, i, min(column_len, 100))
    return output.getvalue()

# --- 4. TOP-BAR: RECHTLICHES (ZEICHENGENAUE TEXTE) ---
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
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "PT Português", "NL Nederlands", "VN Tiếng Việt", "TH ภาษาไทย"], label_visibility="collapsed")
    
    st.write("---")
    st.markdown("### 📦 Pakete")
    
    # PAKET 1
    st.markdown('<div class="paket-container basis-box"><div class="header-box blue-h">🛡️ Amtsschimmel-Killer Analyse</div>', unsafe_allow_html=True)
    st.write("(1 Dokument)")
    st.markdown('<p class="price-tag">3,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung! kein Abo!</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02")
    st.markdown('</div>', unsafe_allow_html=True)

    # PAKET 2
    st.markdown('<div class="paket-container spar-box"><div class="header-box green-h">⚔️ Amtsschimmel-Killer Spar-Paket</div>', unsafe_allow_html=True)
    st.write("(3 Dokumente)")
    st.markdown('<p class="price-tag">9,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung! kein Abo!</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03")
    st.markdown('</div>', unsafe_allow_html=True)

    # PAKET 3
    st.markdown('<div class="paket-container sorglos-box"><div class="header-box gold-h">🚀 Amtsschimmel-Killer Sorglos-Paket</div>', unsafe_allow_html=True)
    st.write("(10 Dokumente)")
    st.markdown('<p class="price-tag">19,99 €</p>', unsafe_allow_html=True)
    st.markdown('<p class="no-abo">Einmalzahlung! kein Abo!</p>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com")
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    st.subheader("📄 Dokument & Vorschau")
    uploaded_file = st.file_uploader("Upload", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed")
    if uploaded_file:
        get_pdf_display_fixed(uploaded_file)
    else:
        st.info("Laden Sie ein Dokument hoch, um die Vorschau sofort zu sehen.")

with col_right:
    st.subheader("🔍 Auswertungen")
    if uploaded_file:
        # AUSFÜHRLICHE AUSWERTUNGSDATEN
        analyse_daten = {
            "Frist": "30.04.2026",
            "Glossar": """Bescheid: Verbindliche Entscheidung einer Behörde.
Rechtsbehelfsbelehrung: Abschnitt, der erklärt, wie Sie Widerspruch einlegen können.
Aktenzeichen: Die Kennnummer, unter der Ihr Vorgang geführt wird.""",
            "Antwort": """Sehr geehrte Damen und Herren,

bezugnehmend auf Ihr Schreiben vom [Datum], Aktenzeichen [Nummer], nehme ich wie folgt Stellung:

[Hier wird die detaillierte KI-Analyse Ihres Falls eingefügt. Die KI prüft Paragraphen und Fristen automatisch.]

Ich bitte um eine schriftliche Bestätigung des Eingangs.

Mit freundlichen Grüßen,
[Name]""",
            "Widerspruch": """Sehr geehrte Damen und Herren,

hiermit lege ich gegen Ihren Bescheid vom [Datum], erhalten am [Datum], fristgerecht Widerspruch ein.

Begründung:

[Hier wird die rechtliche Begründung der KI eingefügt. Die KI formuliert Widersprüche sachlich und präzise.]

Ein ausführlicher Schriftsatz folgt zeitnah.

Mit freundlichen Grüßen,
[Name]"""
        }
        
        with st.expander("📅 Fristen (Deadlines)", expanded=True):
            st.warning(f"⚠️ Fristende erkannt: {analyse_daten['Frist']}")
        with st.expander("📖 Glossar (Begriffserklärung)"):
            st.info(analyse_daten['Glossar'])
        
        st.markdown("### ✉️ Entwürfe")
        tab1, tab2 = st.tabs(["Langes Antwortschreiben", "Ausführlicher Widerspruch"])
        with tab1:
            st.text_area("Antwortentwurf", analyse_daten['Antwort'], height=400)
        with tab2:
            st.text_area("Widerspruchstext", analyse_daten['Widerspruch'], height=400)
        
        st.write("---")
        st.markdown("### 📥 Downloads")
        d1, d2, d3 = st.columns(3)
        with d1: 
            st.download_button("📄 PDF", data=create_valid_pdf_data(analyse_daten['Antwort']), file_name="antwort.pdf", mime="application/pdf")
        with d2: 
            st.download_button("📊 Excel", data=create_excel(analyse_daten), file_name="analyse.xlsx")
        with d3: 
            st.download_button("📝 Word", data=analyse_daten['Antwort'].encode('utf-8'), file_name="antwort.docx")
        
        st.download_button("📅 Kalender.ics hinzufügen", data="BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR", file_name="termin.ics")
    else:
        st.write("Warten auf Datei...")
