import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document
import openai
import base64
import json

# --- 1. SETUP & KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# OpenAI API Key aus Secretsimport streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document
import openai
import base64
import json

# --- 1. SETUP & KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# API Key sicher aus Secrets laden
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- 2. CREDIT-LOGIK (URL PARAMETER) ---
if 'credits' not in st.session_state:
    st.session_state['credits'] = 0

# Auslesen der Stripe-Rückkehr-Parameter
query_params = st.query_params
if "pack" in query_params and "session_id" in query_params:
    s_id = query_params["session_id"]
    # Verhindert Mehrfach-Credits beim Neuladen der Seite
    if "processed_session" not in st.session_state or st.session_state["processed_session"] != s_id:
        st.session_state['credits'] += int(query_params["pack"])
        st.session_state["processed_session"] = s_id
        st.success(f"✅ Zahlung erfolgreich! {query_params['pack']} Dokument(e) freigeschaltet.")

# --- 3. KI-FUNKTION (SYNTAX DEFINITIV FIX) ---
def analyze_document_with_ai(uploaded_file):
    try:
        file_bytes = uploaded_file.getvalue()
        base64_image = base64.b64encode(file_bytes).decode('utf-8')
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # FIX: Die Liste [ ] wird hier korrekt für messages verwendet
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=
                }
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices.message.content)
    except Exception as e:
        st.error(f"KI-Fehler: {e}")
        return None

# --- 4. DOWNLOAD-HELPER (STABIL) ---
def create_excel_report(antwort, widerspruch, glossar, frist):
    output = BytesIO()
    df = pd.DataFrame([{"Frist": frist, "Glossar": glossar, "Antwort": antwort, "Widerspruch": widerspruch}])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
    return output.getvalue()

def create_docx(text):
    doc = Document(); doc.add_heading('Amtsschimmel-Killer Entwurf', 0)
    for line in text.split('\n'): doc.add_paragraph(line)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return bytes(pdf.output(dest='S'))

def create_ical(date_str):
    ics = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:Fristende Amtsschimmel-Killer\nDTSTART:20260430T080000Z\nEND:VEVENT\nEND:VCALENDAR"
    return ics.encode('utf-8')

# --- 5. CSS (BOXEN & DESIGN) ---
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; } .green-box { border-color: #28a745; } .gold-box { border-color: #fcc419; }
    .price-tag { font-size: 28px; font-weight: bold; color: #1E3A8A; margin: 15px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link { display: inline-block; padding: 12px 20px; background-color: #1E3A8A !important; color: white !important; text-decoration: none; border-radius: 8px; font-weight: bold; width: 95%; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 6. RECHTSTEXTE (TOP BAR - EXAKTE ÜBERNAHME) ---
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

# --- 7. SIDEBAR & PAKETE ---
col_pak, col_main = st.columns([1.2, 3.2])

with col_pak:
    try: st.image("icon_final_blau.png", width=120)
    except: st.subheader("🏛️ Amtsschimmel-Killer")
    
    st.write(f"### 🎫 Guthaben: {st.session_state['credits']} Scans")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], key="lang_sel")
    st.write("---")
    
    pakete = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "(1 Dokument)", "3,99", "https://stripe.com"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "(3 Dokumente)", "9,99", "https://stripe.com"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://stripe.com")
    ]
    for style, name, docs, price, link in pakete:
        st.markdown(f'<div class="paket-container {style}"><span style="font-weight:bold">{name}</span><br>{docs}<div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

# --- 8. HAUPTBEREICH ---
with col_main:
    u_file = st.file_uploader("Datei hier ablegen", type=["pdf", "jpg", "png"], label_visibility="collapsed")
    
    if u_file:
        if st.session_state['credits'] > 0:
            if st.button("🚀 Jetzt Dokument analysieren"):
                with st.spinner("Amtsschimmel wird vertrieben..."):
                    res = analyze_document_with_ai(u_file)
                    if res:
                        st.session_state['ki_data'] = res
                        st.session_state['credits'] -= 1
                        st.rerun()
        else:
            st.warning("⚠️ Bitte kaufe ein Paket, um Scans freizuschalten.")

        if 'ki_data' in st.session_state:
            res = st.session_state['ki_data']
            st.error(f"📅 **FRIST-CHECK: {res.get('frist')}**")
            
            with st.expander("📖 Glossar", expanded=True): st.text(res.get('glossar'))
            with st.expander("📋 Antwort-Entwurf", expanded=True): st.text_area("Vorschau:", res.get('antwort'), height=200, key="ta_ant")
            
            st.write("---")
            st.subheader("📥 Downloads & Kalender")
            d1, d2 = st.columns(2)
            with d1:
                st.download_button("📊 Excel (Komplett)", create_excel_report(res.get('antwort'), res.get('widerspruch'), res.get('glossar'), res.get('frist')), "Analyse.xlsx", key="dl_ex")
                st.download_button("📝 Word (Alle Briefe)", create_docx(res.get('antwort')), "Entwurf.docx", key="dl_doc")
            with d2:
                st.download_button("📕 PDF (Widerspruch)", create_pdf(res.get('widerspruch')), "Widerspruch.pdf", key="dl_pdf")
                st.download_button("📅 Termin speichern", create_ical(res.get('frist')), "frist.ics", key="dl_cal")

if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- 2. CREDIT-LOGIK (STRIPE REDIRECT) ---
if 'credits' not in st.session_state:
    st.session_state['credits'] = 0

# Auslesen der URL-Parameter für erfolgreiche Zahlungen
query_params = st.query_params
if "session_id" in query_params and "pack" in query_params:
    session_id = query_params["session_id"]
    if "last_session" not in st.session_state or st.session_state["last_session"] != session_id:
        st.session_state['credits'] += int(query_params["pack"])
        st.session_state["last_session"] = session_id
        st.success(f"✅ Zahlung erfolgreich! {query_params['pack']} Dokument(e) freigeschaltet.")

# --- 3. KI-FUNKTION (KORRIGIERTE SYNTAX) ---
def analyze_document_with_ai(uploaded_file):
    try:
        file_bytes = uploaded_file.getvalue()
        base64_image = base64.b64encode(file_bytes).decode('utf-8')
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices.message.content)
    except Exception as e:
        st.error(f"KI-Fehler: {e}")
        return None

# --- 4. DOWNLOAD-HELPER (STABIL) ---
def create_excel_report(antwort, widerspruch, glossar, frist):
    output = BytesIO()
    df = pd.DataFrame([{"Frist": frist, "Glossar": glossar, "Antwort": antwort, "Widerspruch": widerspruch}])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
    return output.getvalue()

def create_docx(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Entwurf', 0)
    for line in text.split('\n'): doc.add_paragraph(line)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return bytes(pdf.output(dest='S'))

def create_ical(date_str):
    ics = f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:Fristende Amtsschimmel-Killer\nDTSTART:20260430T080000Z\nEND:VEVENT\nEND:VCALENDAR"
    return ics.encode('utf-8')

# --- 5. CSS (BOXEN & DESIGN) ---
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; } .green-box { border-color: #28a745; } .gold-box { border-color: #fcc419; }
    .price-tag { font-size: 28px; font-weight: bold; color: #1E3A8A; margin: 15px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link { display: inline-block; padding: 12px 20px; background-color: #1E3A8A !important; color: white !important; text-decoration: none; border-radius: 8px; font-weight: bold; width: 95%; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 6. TOP-BAR: RECHTSTEXTE (EXAKTE ÜBERNAHME) ---
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

# --- 7. HAUPT-LAYOUT ---
col_pak, col_main = st.columns([1.2, 3.2])

with col_pak:
    try: st.image("icon_final_blau.png", width=120)
    except: st.subheader("🏛️ Amtsschimmel-Killer")
    
    st.write(f"### 🎫 Guthaben: {st.session_state['credits']} Scans")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], key="lang_sel")
    st.write("---")
    
    pakete = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "(1 Dokument)", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "(3 Dokumente)", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")
    ]
    for style, name, docs, price, link in pakete:
        st.markdown(f'<div class="paket-container {style}"><span style="font-weight:bold">{name}</span><br>{docs}<div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_main:
    u_file = st.file_uploader("Dokument hier ablegen", type=["pdf", "jpg", "png"], label_visibility="collapsed")
    
    if u_file:
        if st.session_state['credits'] > 0:
            if st.button("🚀 Jetzt Dokument analysieren"):
                with st.spinner("Amtsschimmel wird vertrieben..."):
                    ki_res = analyze_document_with_ai(u_file)
                    if ki_res:
                        st.session_state['ki_data'] = ki_res
                        st.session_state['credits'] -= 1
                        st.rerun()
        else:
            st.warning("⚠️ Bitte kaufe ein Paket, um Scans freizuschalten.")

        if 'ki_data' in st.session_state:
            res = st.session_state['ki_data']
            st.error(f"📅 **FRIST-CHECK: {res.get('frist')}**")
            
            with st.expander("📖 Glossar", expanded=True): st.text(res.get('glossar'))
            with st.expander("📋 Antwort-Entwurf", expanded=True): st.text_area("Vorschau:", res.get('antwort'), height=150, key="ta_ant")
            
            st.write("---")
            st.subheader("📥 Downloads & Kalender")
            d1, d2 = st.columns(2)
            with d1:
                st.download_button("📊 Excel (Komplett)", create_excel_report(res.get('antwort'), res.get('widerspruch'), res.get('glossar'), res.get('frist')), "Analyse.xlsx", key="dl_ex")
                st.download_button("📝 Word (Alle Briefe)", create_docx(res.get('antwort')), "Entwurf.docx", key="dl_doc")
            with d2:
                st.download_button("📕 PDF (Widerspruch)", create_pdf(res.get('widerspruch')), "Widerspruch.pdf", key="dl_pdf")
                st.download_button("📅 Termin speichern", create_ical(res.get('frist')), "frist.ics", key="dl_cal")
