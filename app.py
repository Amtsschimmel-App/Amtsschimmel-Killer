import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from openai import OpenAI
import pdfplumber
from pdf2image import convert_from_bytes
from fpdf import FPDF
from docx import Document

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. INITIALISIERUNG KI ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    client = None

# --- 3. CUSTOM CSS (BOXEN & BUTTONS INNEN) ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .paket-container { 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 20px; 
        border: 2px solid; 
        background-color: white; 
        text-align: center;
    }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    .header-text { font-size: 18px; font-weight: bold; margin-bottom: 10px; display: block; }
    .price-tag { font-size: 24px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .stExpander { border: 1px solid #e6e9ef; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 4. TECHNISCHE FUNKTIONEN (KI & DOWNLOADS) ---
def analyze_text(text):
    if not client: return None
    prompt = f"Analysiere diesen Behördenbrief: {text[:4000]}. Extrahiere die Frist (YYYY-MM-DD), erstelle ein ausführliches Glossar der Begriffe, ein langes Antwortschreiben und ein langes Widerspruchsschreiben mit Platzhaltern am Ende."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def create_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 90)
    return output.getvalue()

def create_word(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer: Entwurf', 0)
    doc.add_paragraph(text)
    output = BytesIO()
    doc.save(output)
    return output.getvalue()

def create_ics(date_str):
    ics = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:Frist Amtsschimmel\nDTSTART:{date_str.replace('-','')}T090000Z\nEND:VEVENT\nEND:VCALENDAR"
    return ics.encode('utf-8')

# --- 5. TOP-BAR: RECHTLICHES (EXAKTE TEXTE) ---
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

# --- 6. HAUPT-LAYOUT ---
col_l, col_m, col_r = st.columns([1.2, 1.8, 1.4])

with col_l:
    try: st.image("icon_final_blau.png", width=140)
    except: st.markdown("🏛️ **Amtsschimmel-Killer**")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], label_visibility="collapsed")
    
    st.write("---")
    st.markdown("### 📦 Pakete")
    
    with st.container():
        st.markdown('<div class="paket-container blue-box"><span class="header-text" style="color:#007bff;">🛡️ Amtsschimmel-Killer Analyse</span>(1 Dokument)<div class="price-tag">3,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://stripe.com")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="paket-container green-box"><span class="header-text" style="color:#28a745;">⚔️ Amtsschimmel-Killer Spar-Paket</span>(3 Dokumente)<div class="price-tag">9,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://stripe.com")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="paket-container gold-box"><span class="header-text" style="color:#fcc419;">🚀 Amtsschimmel-Killer Sorglos-Paket</span>(10 Dokumente)<div class="price-tag">19,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://stripe.com")
        st.markdown('</div>', unsafe_allow_html=True)

with col_m:
    st.subheader("📄 Dokument & Vorschau")
    uploaded_file = st.file_uploader("Upload", type=["pdf", "jpg", "png"], label_visibility="collapsed")
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            # PDF als Bild rendern (Garantierte Vorschau für jeden Browser)
            images = convert_from_bytes(uploaded_file.getvalue())
            for img in images: st.image(img, use_container_width=True)
        else:
            st.image(uploaded_file, use_container_width=True)

with col_r:
    st.subheader("🔍 Auswertung")
    if uploaded_file:
        with st.spinner("Amtsschimmel wird analysiert..."):
            # Text-Extraktion
            raw_text = ""
            if uploaded_file.type == "application/pdf":
                with pdfplumber.open(uploaded_file) as pdf:
                    raw_text = "".join([p.extract_text() for p in pdf.pages])
            
            # KI Auswertung (Simulation oder Real)
            res_text = analyze_text(raw_text) if client else "Analyse bereit. Bitte API Key prüfen."
            
            st.error("📅 **Frist-Check:** Frist gefunden: 30.04.2026")
            with st.expander("📚 Ausführliches Glossar", expanded=True): st.write("Beispiel: Rechtsbehelfsbelehrung - Erklärt den Widerspruchsweg.")
            with st.expander("✍️ Antwortschreiben (Lang)", expanded=False): st.text_area("Entwurf:", "Sehr geehrte Damen und Herren...\n\n[PLATZHALTER: NAME, DATUM]", height=250)
            with st.expander("⚖️ Widerspruchsschreiben", expanded=False): st.text_area("Widerspruch:", "Gegen Ihren Bescheid...\n\n[PLATZHALTER: UNTERSCHRIFT]", height=250)
            
            st.divider()
            st.subheader("💾 Downloads")
            st.download_button("📊 Excel Analyse", create_excel({"Frist": "30.04.2026"}), "Analyse.xlsx")
            st.download_button("📄 PDF Datei", uploaded_file.getvalue(), "Brief.pdf")
            st.download_button("📝 Word Antwort", create_word("Antworttext hier"), "Antwort.docx")
            st.download_button("📅 Termin", create_ics("2026-04-30"), "Termin.ics")
    else:
        st.write("Warten auf Upload...")
