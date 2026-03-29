import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide", page_icon="🏛️")

# Custom CSS für die Paket-Optik
st.markdown("""
<style>
    .package-box {
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .price { font-size: 24px; font-weight: bold; color: #1f77b4; }
    .no-abo-badge { 
        background-color: #ff4b4b; 
        color: white; 
        padding: 2px 10px; 
        border-radius: 5px; 
        font-size: 12px; 
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. OBERE NAVIGATION (RECHTLICHES & VORLAGEN) ---
c_top1, c_top2, c_top3, c_top4 = st.columns(4)

with c_top1:
    with st.expander("⚖️ Impressum"):
        st.text("""Amtsschimmel-Killer
Betreiberin: Elisabeth Reinecke
Ringelsweide 9
40223 Düsseldorf

Kontakt:
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

Haftung:
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")

with c_top2:
    with st.expander("🛡️ Datenschutz"):
        st.text("""1. Datenschutz auf einen Blick
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

2. Datenerfassung & Hosting
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

3. Dokumentenverarbeitung
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

4. Zahlungsabwicklung (Stripe)
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

5. Ihre Rechte
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.""")

with c_top3:
    with st.expander("❓ FAQ"):
        st.text("""Ist das ein Abonnement?
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

Wie sicher sind meine Dokumente?
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

Ersetzt die App eine Rechtsberatung?
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

Was passiert, wenn der Scan fehlschlägt?
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

Wie erreiche ich Elisabeth Reinecke?
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.""")

with c_top4:
    with st.expander("📝 Vorlagen"):
        st.text("""Fristverlängerung:
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

Widerspruch einlegen (Fristwahrend):
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

Akteneinsicht einfordern:
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]""")

st.divider()

# --- 3. HAUPTBEREICH (Logo & Sprachen über den Spalten) ---
t1, t2 = st.columns([1, 3])
with t1:
    try:
        st.image("icon_final_blau.png", width=150)
    except:
        st.header("🏛️ Amtsschimmel-Killer")
with t2:
    st.selectbox("Sprache / Language / Dil / Język / Мова / لغة", 
                 ["DE - Deutsch", "EN - English", "TR - Türkçe", "PL - Polski", "UA - Українська", "RU - Русский", "AR - العربية", "FR - Français", "ES - Español", "IT - Italiano"])

# --- 4. LAYOUT: PAKETE LINKS | UPLOAD RECHTS ---
col_left, col_right = st.columns([1, 1.8])

with col_left:
    st.subheader("💳 Guthaben laden")
    
    # Paket 1
    st.markdown('<div class="package-box" style="background-color: #f8f9fa;">'
                '<h4>📄 Analyse (1 Dok.)</h4>'
                '<p class="price">3,99 €</p>'
                '<span class="no-abo-badge">❌ KEIN ABO</span><br><small>Einmalzahlung</small>'
                '</div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", use_container_width=True)
    
    # Paket 2
    st.markdown('<div class="package-box" style="background-color: #e3f2fd; border: 1px solid #2196f3;">'
                '<h4>🥈 Spar-Paket (3 Dok.)</h4>'
                '<p class="price">9,99 €</p>'
                '<span class="no-abo-badge">❌ KEIN ABO</span><br><small>Einmalzahlung</small>'
                '</div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)
    
    # Paket 3
    st.markdown('<div class="package-box" style="background-color: #fffde7; border: 1px solid #fbc02d;">'
                '<h4>🥇 Sorglos-Paket (10 Dok.)</h4>'
                '<p class="price">19,99 €</p>'
                '<span class="no-abo-badge">❌ KEIN ABO</span><br><small>Einmalzahlung</small>'
                '</div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04", use_container_width=True)

with col_right:
    st.subheader("📑 Dokumenten-Analyse")
    st.success("👑 Admin Guthaben: 999 Scans")
    
    uploaded_file = st.file_uploader("Datei hier reinziehen oder klicken", type=["pdf", "jpg", "png", "jpeg"])
    
    if uploaded_file:
        st.info(f"Datei geladen: {uploaded_file.name}")
        
        # Analyse-Ergebnisse (Platzhalter für KI)
        with st.container(border=True):
            st.warning("📅 **Frist erkannt: 24.12.2024**")
            st.markdown("**Inhalts-Zusammenfassung:**")
            st.write("Die Behörde fordert Unterlagen zu Ihrem Antrag an.")
            st.markdown("**Antwortentwurf:**")
            st.code("Sehr geehrte Damen und Herren, anbei erhalten Sie...", language="text")

# --- 5. EXPORT BEREICH ---
if uploaded_file:
    st.divider()
    st.subheader("📥 Export")
    ex1, ex2, ex3 = st.columns(3)
    with ex1: st.button("📄 Als PDF", use_container_width=True)
    with ex2: st.button("📊 Als Excel", use_container_width=True)
    with ex3: st.button("📅 Kalender-Termin", use_container_width=True)
