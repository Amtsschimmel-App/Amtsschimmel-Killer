
import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from datetime import datetime, timedelta

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# --- 2. CUSTOM CSS (LOGO & PAKET-STYLING) ---
st.markdown("""
    <style>
    .pkg-box { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    .pkg-title { font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; }
    .pkg-price { font-size: 1.5rem; font-weight: bold; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXPORT FUNKTIONEN ---
def create_excel_pro(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(data)
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 100)
    return output.getvalue()

# --- 4. TOP-BAR: RECHTLICHES (MIT EXAKTEN TEXTEN & ABSTÄNDEN) ---
t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum"):
        st.markdown("""
**Amtsschimmel-Killer**

**Betreiberin:**

Elisabeth Reinecke

Ringelsweide 9
40223 Düsseldorf

<br>

**Kontakt:**
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

<br>

**Haftung:**
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        """, unsafe_allow_html=True)

with t2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("""
**1. Datenschutz auf einen Blick**
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

<br>

**2. Datenerfassung & Hosting**
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

<br>

**3. Dokumentenverarbeitung**
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

<br>

**4. Zahlungsabwicklung (Stripe)**
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

<br>

**5. Ihre Rechte**
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
        """, unsafe_allow_html=True)

with t3:
    with st.expander("❓ FAQ"):
        st.markdown("""
**Ist das ein Abonnement?**
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

<br>

**Wie sicher sind meine Dokumente?**
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

<br>

**Ersetzt die App eine Rechtsberatung?**
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

<br>

**Was passiert, wenn der Scan fehlschlägt?**
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

<br>

**Wie erreiche ich Elisabeth Reinecke?**
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
        """, unsafe_allow_html=True)

with t4:
    with st.expander("📝 Vorlagen"):
        st.markdown("""
**Fristverlängerung:**
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

<br><br>

**Widerspruch einlegen (Fristwahrend):**
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

<br><br>

**Akteneinsicht einfordern:**
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]
        """, unsafe_allow_html=True)

st.divider()

# --- 5. HAUPT-LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.6, 1.3])

with col_left:
    try:
        st.image("icon_final_blau.png", width=160)
    except:
        st.markdown("🏛️ **Amtsschimmel-Killer**")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "RU Русский", "AR العربية"], label_visibility="collapsed")

    st.write("")
    
    # PAKETE MIT BRANDING & STRIPE CODES
    with st.container():
        st.markdown('<div class="pkg-box">📄 <span class="pkg-title">Amtsschimmel-Killer: Basis</span><br><span class="pkg-price">3,99 €</span><br>1 Analyse</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", use_container_width=True)

    with st.container():
        st.markdown('<div class="pkg-box" style="background-color: #ebf5fb;">🥈 <span class="pkg-title">Amtsschimmel-Killer: Spar-Paket</span><br><span class="pkg-price">9,99 €</span><br>3 Analysen</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)

    with st.container():
        st.markdown('<div class="pkg-box" style="background-color: #fef9e7;">🥇 <span class="pkg-title">Amtsschimmel-Killer: Sorglos</span><br><span class="pkg-price">19,99 €</span><br>10 Analysen</div>', unsafe_allow_html=True)
        st.link_button("Jetzt kaufen", "https://buy.stripe.com", use_container_width=True)

with col_mid:
    st.subheader("1. Dokument hochladen")
    uploaded_file = st.file_uploader("Datei wählen (PDF oder Bild)", type=['pdf', 'png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    # --- NEU: AUTOMATISCHE VORSCHAU ---
    if uploaded_file is not None:
        st.write("---")
        st.markdown("### 🖼️ Dokumentenvorschau")
        if uploaded_file.type == "application/pdf":
            base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.image(uploaded_file, use_container_width=True)
        
        if st.button("Analyse starten ✨", use_container_width=True):
            st.info("KI-Analyse wird gestartet...")

with col_right:
    st.subheader("2. Analyse-Ergebnis")
    st.info("Bitte laden Sie links ein Dokument hoch und wählen Sie ein Paket.")
