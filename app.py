import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from docx import Document

# --- 1. SEITEN-SETUP ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. STABILE DOWNLOAD-FUNKTIONEN ---
def create_excel_report(data_dict):
    output = BytesIO()
    df = pd.DataFrame([data_dict])
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 80) # Maximale Breite für Lesbarkeit
    return output.getvalue()

def create_full_docx(title, text):
    doc = Document()
    doc.add_heading(title, 0)
    for line in text.split('\n'):
        doc.add_paragraph(line)
    out = BytesIO(); doc.save(out); return out.getvalue()

def create_safe_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Entfernt Sonderzeichen, die fpdf zum Absturz bringen
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_text)
    return pdf.output(dest='S').encode('latin-1')

# --- 3. CSS (PAKETE & STRIPE BUTTONS) ---
st.markdown("""
<style>
    .paket-container { border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 3px solid; background: white; text-align: center; }
    .blue-box { border-color: #007bff; }
    .green-box { border-color: #28a745; }
    .gold-box { border-color: #fcc419; }
    .header-text { font-size: 16px; font-weight: bold; margin-bottom: 10px; display: block; color: #333; }
    .price-tag { font-size: 28px; font-weight: bold; color: #1E3A8A; margin: 10px 0; }
    .no-abo { font-size: 14px; color: #d32f2f; font-weight: bold; margin-bottom: 15px; }
    .st-button-link {
        display: inline-block; padding: 12px 20px; background-color: #1E3A8A; color: white !important;
        text-decoration: none; border-radius: 8px; font-weight: bold; width: 95%; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. RECHTSTEXTE (1:1 ÜBERNAHME) ---
t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum"):
        st.text("Amtsschimmel-Killer\n\nBetreiberin:\n\nElisabeth Reinecke\n\nRingelsweide 9\n40223 Düsseldorf\n\nKontakt:\nTelefon: +49 211 15821329\nE-Mail: amtsschimmel-killer@proton.me\nWeb: amtsschimmel-killer.streamlit.app\n\nHaftung:\nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
with t2:
    with st.expander("🛡️ Datenschutz"):
        st.text("1. Datenschutz auf einen Blick\nWir behandeln Ihre personenbezogenen Daten vertraulich...\n\n2. Datenerfassung & Hosting\nDiese App wird auf Streamlit Cloud gehostet...\n\n3. Dokumentenverarbeitung\nIhre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI übertragen...\n\n4. Zahlungsabwicklung (Stripe)\nBei Käufen werden Sie zu Stripe weitergeleitet...\n\n5. Ihre Rechte\nKontaktieren Sie uns unter amtsschimmel-killer@proton.me.")
with t3:
    with st.expander("❓ FAQ"):
        st.text("Ist das ein Abonnement?\nNein. Wir hassen Abos genauso wie Amtsschimmel...\n\nWie sicher sind meine Dokumente?\nIhre Dokumente werden verschlüsselt an die KI übertragen...\n\nErsetzt die App eine Rechtsberatung?\nNein...\n\nWas passiert, wenn der Scan fehlschlägt?\nEin Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat.")
with t4:
    with st.expander("📝 Vorlagen"):
        st.text("Fristverlängerung:\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung...\n\nWiderspruch einlegen (Fristwahrend)\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum]...\n\nAkteneinsicht einfordern:\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts beantrage ich Akteneinsicht.")

st.divider()

# --- 5. LAYOUT ---
col_pakete, col_main = st.columns([1.2, 3.2])

with col_pakete:
    try: st.image("icon_final_blau.png", width=120)
    except: st.subheader("🏛️ Amtsschimmel-Killer")
    
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية", "ES Español", "FR Français", "IT Italiano", "NL Nederlands", "VN Tiếng Việt"], key="main_lang")
    st.write("---")
    
    # PAKETE
    p_config = [
        ("blue-box", "🛡️ Amtsschimmel-Killer Analyse", "(1 Dokument)", "3,99", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"),
        ("green-box", "⚔️ Amtsschimmel-Killer Spar-Paket", "(3 Dokumente)", "9,99", "https://buy.stripe.com/8x228retRbj50paalq1gs03"),
        ("gold-box", "🚀 Amtsschimmel-Killer Sorglos-Paket", "(10 Dokumente)", "19,99", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs041")
    ]
    for style, name, docs, price, link in p_config:
        st.markdown(f'<div class="paket-container {style}"><span class="header-text">{name}</span>{docs}<div class="price-tag">{price} €</div><div class="no-abo">Einmalzahlung kein Abo</div><a href="{link}" target="_blank" class="st-button-link">Jetzt kaufen</a></div>', unsafe_allow_html=True)

with col_main:
    c_preview, c_analysis = st.columns([1.8, 1.4])
    
    with c_preview:
        st.subheader("📄 Dokument")
        u_file = st.file_uploader("Datei hier ablegen", type=["pdf", "jpg", "png"])
        if u_file:
            if u_file.type == "application/pdf":
                st.success("✅ PDF erfolgreich hochgeladen.")
                st.info("Vorschau für Mobile deaktiviert, um Fehler zu vermeiden.")
                st.download_button("📥 Original PDF anzeigen", u_file, file_name="hochgeladen.pdf")
            else: st.image(u_file, use_container_width=True)
            
    with c_analysis:
        st.subheader("🔍 Auswertung")
        if u_file:
            st.error("📅 **FRIST-CHECK: 30.04.2026**")
            st.markdown("📅 **Kalender:** [Termin speichern (iCal)](#)")
            
            with st.expander("📖 Ausgiebiges Glossar", expanded=True):
                st.markdown("""**Rechtsbehelfsbelehrung:** Erklärt, wie und wo Sie gegen einen Bescheid vorgehen können.  
**Verwaltungsakt:** Eine hoheitliche Maßnahme einer Behörde zur Regelung eines Einzelfalls.  
**Ermessen:** Der gesetzlich eingeräumte Spielraum der Behörde bei Entscheidungen.  
**Anhörung:** Ihr Recht, sich zu den für die Entscheidung erheblichen Tatsachen zu äußern.  
**Widerspruchsfrist:** Zeitraum (meist 1 Monat), in dem der Widerspruch eingereicht werden muss.""")

            # TEXTE
            antwort_voll = """[VORNAME NACHNAME]
[STRASSE HAUSNUMMER]
[PLZ ORT]

An: [NAME DER BEHÖRDE]
[STRASSE NR]
[PLZ ORT]

Datum: [HEUTIGES DATUM]

Betreff: Antwort auf Ihr Schreiben vom [DATUM DES SCHREIBENS]
Aktenzeichen: [AKTENZEICHEN EINTRAGEN]

Sehr geehrte Damen und Herren,

in der oben genannten Angelegenheit nehme ich Bezug auf Ihr Schreiben. Nach Prüfung des Sachverhalts teile ich Ihnen folgendes mit:

Ich bitte um Bestätigung des Eingangs dieses Schreibens.

Mit freundlichen Grüßen,

[UNTERSCHRIFT]"""

            widerspruch_voll = """[VORNAME NACHNAME]
[STRASSE HAUSNUMMER]
[PLZ ORT]

An: [NAME DER BEHÖRDE]

WIDERSPRUCH
Gegen den Bescheid vom [DATUM], erhalten am [DATUM].

Sehr geehrte Damen und Herren,

hiermit lege ich gegen den oben genannten Bescheid fristwahrend Widerspruch ein. 

Eine ausführliche Begründung folgt in einem separaten Schreiben nach erfolgter Akteneinsicht.

Mit freundlichen Grüßen,

[UNTERSCHRIFT]"""

            with st.expander("✉️ Antwort-Entwurf", expanded=True):
                final_txt = st.text_area("Vorschau & Bearbeitung:", antwort_voll, height=200)
                st.download_button("📄 Download Word (.docx)", create_full_docx("Antwortbrief", final_txt), "Antwort.docx")
                
                ex_data = {"Dokument": u_file.name, "Frist": "30.04.2026", "Antwort": final_txt, "Glossar": "Rechtsbehelf, Verwaltungsakt, Ermessen"}
                st.download_button("📊 Download Excel (.xlsx)", create_excel_report(ex_data), "Analyse.xlsx")

            with st.expander("⚖️ Widerspruch"):
                st.download_button("📕 Widerspruch als PDF speichern", create_safe_pdf(widerspruch_voll), "Widerspruch.pdf")
        else: st.info("Warten auf Upload...")
