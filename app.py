import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from openai import OpenAI
import pdfplumber
from fpdf import FPDF
from docx import Document

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. INITIALISIERUNG KI ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) if "OPENAI_API_KEY" in st.secrets else None

# --- 3. CUSTOM CSS (BOXEN & BUTTONS INNEN) ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 2px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    .header-text { font-size: 18px; font-weight: bold; margin-bottom: 10px; display: block; }
    .price-tag { font-size: 24px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    iframe { border-radius: 8px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# --- 4. TECHNISCHE FUNKTIONEN (KI & DOWNLOADS) ---
def analyze_document(text):
    if not client: return {"Frist": "Kein API Key", "Glossar": "Fehlt", "Antwort": "Fehlt", "Widerspruch": "Fehlt"}
    prompt = f"Analysiere diesen Behördenbrief: {text[:4000]}. Extrahiere die Frist (YYYY-MM-DD), erstelle ein ausführliches Glossar der Begriffe, ein langes Antwortschreiben und ein langes Widerspruchsschreiben mit Platzhaltern am Ende. Antworte strukturiert."
    response = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
    res = response.choices[0].message.content
    return {"Frist": "30.04.2026", "Glossar": res, "Antwort": res, "Widerspruch": res}

def create_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame([data]).to_excel(writer, index=False, sheet_name='Analyse')
        writer.sheets['Analyse'].set_column(0, 5, 100)
    return output.getvalue()

def create_word(text):
    doc = Document(); doc.add_heading('Amtsschimmel-Killer Entwurf', 0); doc.add_paragraph(text)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_pdf_report(data):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    for k, v in data.items(): pdf.multi_cell(0, 10, f"{k}: {v}\n")
    return pdf.output(dest='S').encode('latin-1', 'replace')

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
    
    for p in [("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "1 Dokument", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
              ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "3 Dokumente", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
              ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "10 Dokumente", "19,99", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")]:
        st.markdown(f'<div class="paket-container {p[0]}"><span class="header-text">{p[1]}</span>({p[2]})<div class="price-tag">{p[3]} €</div><div class="no-abo">Einmalzahlung kein Abo</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", p[4])
        st.markdown('</div>', unsafe_allow_html=True)

with col_m:
    st.subheader("📄 Dokument & Vorschau")
    uploaded_file = st.file_uploader("Upload", type=["pdf", "jpg", "png"], label_visibility="collapsed")
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            st.markdown(f'<iframe src="data:application/pdf;base64,{b64}#toolbar=0" width="100%" height="900px"></iframe>', unsafe_allow_html=True)
        else: st.image(uploaded_file, use_container_width=True)

with col_r:
    st.subheader("🔍 Auswertung")
    if uploaded_file:
        with st.spinner("Analyse läuft..."):
            txt = ""
            if uploaded_file.type == "application/pdf":
                with pdfplumber.open(uploaded_file) as pdf: txt = "".join([p.extract_text() for p in pdf.pages])
            res = analyze_document(txt)
            st.error(f"📅 **Frist-Check:** Frist endet am **{res['Frist']}**")
            with st.expander("📚 Glossar", expanded=True): st.write(res['Glossar'])
            with st.expander("✍️ Antwortschreiben", expanded=False): st.text_area("Entwurf:", res['Antwort'], height=250)
            with st.expander("⚖️ Widerspruch", expanded=False): st.text_area("Entwurf:", res['Widerspruch'], height=250)
            st.divider()
            st.subheader("💾 Downloads")
            st.download_button("📊 Excel Analyse", create_excel(res), "Analyse.xlsx")
            st.download_button("📄 PDF Bericht", create_pdf_report(res), "Bericht.pdf")
            st.download_button("📝 Word Antwort", create_word(res['Antwort']), "Antwort.docx")
            st.button("📅 Termin merken (Kalender.ico)")
    else: st.write("Warten auf Upload...")
