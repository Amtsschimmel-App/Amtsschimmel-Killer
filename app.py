import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from fpdf import FPDF
from docx import Document
import openai

# --- 1. SETUP & DESIGN ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

st.markdown("""
<style>
    .paket-box { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; background-color: #f0f7ff; }
    .green-box { border-color: #28a745; background-color: #f3fff5; }
    .gold-box { border-color: #fcc419; background-color: #fffdf0; }
    .price-tag { font-size: 28px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .stripe-button {
        display: inline-block; padding: 12px 20px; background-color: #1E3A8A !important; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 100%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DOWNLOAD-FUNKTIONEN ---
def create_excel(frist, glossar, antwort, widerspruch):
    out = BytesIO()
    df = pd.DataFrame([{"Frist": frist, "Glossar": glossar, "Antwort": antwort, "Widerspruch": widerspruch}])
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
        writer.sheets['Sheet1'].set_column(0, 3, 70)
    return out.getvalue()

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))
    return bytes(pdf.output(dest='S'))

# --- 3. RECHTSTEXTE (EXAKT MIT ABSTÄNDEN) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("Amtsschimmel-Killer\n\nBetreiberin:\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.\n\n4. Zahlungsabwicklung (Stripe)\nBei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.\n\n5. Ihre Rechte\nSie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.markdown("Ist das ein Abonnement?\nNein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.\n\nWie sicher sind meine Dokumente?\nIhre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.\n\nErsetzt die App eine Rechtsberatung?\nNein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.\n\nWas passiert, wenn der Scan fehlschlägt?\nEin Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.\n\nWie erreiche ich Elisabeth Reinecke?\nNutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]\n\nWiderspruch einlegen (Fristwahrend)\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]\n\nAkteneinsicht einfordern:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

st.divider()

# --- 4. HAUPTBEREICH (3 SPALTEN) ---
col_side, col_doc, col_res = st.columns([1, 1.5, 1.5])

with col_side:
    st.image("icon_final_blau.png", width=120)
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], key="lang")
    
    # Pakete
    st.markdown('<div class="paket-box blue-box">🛡️ <b>Amtsschimmel-Killer Analyse</b><br>(1 Dokument)<div class="price-tag">3,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" class="stripe-button">Jetzt kaufen</a></div>', unsafe_allow_html=True)
    st.markdown('<div class="paket-box green-box">⚔️ <b>Amtsschimmel-Killer Spar-Paket</b><br>(3 Dokumente)<div class="price-tag">9,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="https://buy.stripe.com/8x228retRbj50paalq1gs03" class="stripe-button">Jetzt kaufen</a></div>', unsafe_allow_html=True)
    st.markdown('<div class="paket-box gold-box">🚀 <b>Amtsschimmel-Killer Sorglos-Paket</b><br>(10 Dokumente)<div class="price-tag">19,99 €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="https://buy.stripe.com/28EcN50D1bj52xi8di1gs041" class="stripe-button">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_doc:
    st.subheader("📄 Dokument")
    u_file = st.file_uploader("Datei hochladen", type=["png", "jpg", "jpeg"], key="up")
    if u_file: st.image(u_file, use_container_width=True)

with col_res:
    st.subheader("🔍 Auswertung")
    if u_file:
        with st.spinner("Analysiere Dokument..."):
            try:
                client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                b64_img = base64.b64encode(u_file.getvalue()).decode('utf-8')
                
                # Der KI-Aufruf mit korrigierter Syntax
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=
                    }]
                )
                raw = response.choices[0].message.content
                parts = raw.split("###")
                
                # Anzeige der Ergebnisse
                st.error(f"📅 **FRIST: {parts[1] if len(parts)>1 else 'Unbekannt'}**")
                with st.expander("📖 Glossar", expanded=True): st.write(parts[2] if len(parts)>2 else "Kein Glossar")
                with st.expander("📋 Antwort"): st.text_area("Entwurf", parts[3] if len(parts)>3 else "Kein Entwurf", height=150, key="a")
                with st.expander("⚖️ Widerspruch"): st.text_area("Text", parts[4] if len(parts)>4 else "Kein Text", height=150, key="w")
                
                # Download-Raster
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button("📊 Excel", create_excel("30.04.2026", "Glossar", "Antwort", "Widerspruch"), "analyse.xlsx", key="d1")
                    st.download_button("📝 Word", b"docx", "brief.docx", key="d2")
                with c2:
                    st.download_button("📕 PDF", create_pdf("Widerspruch"), "widerspruch.pdf", key="d3")
                    st.download_button("📅 iCal", b"ics", "frist.ics", key="d4")
            except Exception as e:
                st.error(f"KI-Fehler: {str(e)}")
