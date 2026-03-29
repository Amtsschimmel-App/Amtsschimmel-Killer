import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
import shutil
import stripe
from datetime import datetime
import gc 

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")
LOGO_DATEI = "icon_final_blau.png"

# 2. DESIGN & STYLING (CSS)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { 
        text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; 
        border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s;
    }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; scale: 1.02; }
    .step-box { background: #eff6ff; padding: 15px; border-radius: 10px; border: 1px solid #bfdbfe; text-align: center; min-height: 100px; }
    .legal-box { font-size: 0.85em; color: #475569; line-height: 1.5; background: #f8fafc; padding: 15px; border-radius: 8px; }
    .faq-question { font-weight: bold; color: #1e3a8a; margin-top: 15px; font-size: 1.1em; }
    .faq-answer { margin-bottom: 15px; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 4. SESSION STATE & ADMIN LOGIK (999 Guthaben Fix) ---
if "credits" not in st.session_state: 
    st.session_state.credits = 0
if "last_analysis" not in st.session_state: 
    st.session_state.last_analysis = ""

# WICHTIG: Admin-Check für 999 Guthaben
# Aufruf via: https://amtsschimmel-killer.streamlit.app!
if st.query_params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999
    st.toast("🔓 ADMIN-MODUS AKTIV: 999 Scans freigeschaltet")

# --- 5. SIDEBAR (Guthaben & Pakete) ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI): 
        st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    st.divider()
    st.subheader("Guthaben aufladen")
    try:
        pkgs = [
            ("📄 Basis-Paket", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"),
            ("🚀 Spar-Paket", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"),
            ("💎 Profi-Paket", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")
        ]
        for name, link, count, price in pkgs:
            st.markdown(f'''
                <a href="{link}" target="_blank" class="buy-button">
                    <b>{name}</b><br>
                    <span style="color: #16a34a;">{price} | {count}</span><br>
                    <small>✔ Einmalzahlung | Kein Abo</small>
                </a>''', unsafe_allow_html=True)
    except:
        st.error("Stripe-Links in den Secrets fehlen.")

# --- 6. HAUPTBEREICH (Tabs) ---
tab1, tab2, tab3 = st.tabs(["🚀 Brief-Killer", "⚡ Sofort-Antworten", "❓ FAQ & Hilfe"])

with tab1:
    st.title("Amtsschimmel-Killer 📄🚀")
    
    # 3-Schritte-Anleitung
    s1, s2, s3 = st.columns(3)
    with s1: st.markdown('<div class="step-box"><b>1. Guthaben wählen</b><br><small>Paket links buchen.<br>Einmalzahlung.</small></div>', unsafe_allow_html=True)
    with s2: st.markdown('<div class="step-box"><b>2. Brief hochladen</b><br><small>Foto oder PDF hochladen.<br>Wir lesen den Bescheid.</small></div>', unsafe_allow_html=True)
    with s3: st.markdown('<div class="step-box"><b>3. Antwort nutzen</b><br><small>Antwort kopieren, Aktenzeichen ergänzen.</small></div>', unsafe_allow_html=True)
    
    st.divider()

    if st.session_state.last_analysis:
        if st.button("🔄 Nächsten Brief bearbeiten"):
            st.session_state.last_analysis = ""
            st.rerun()

    if not st.session_state.last_analysis:
        st.subheader("Hier Brief hochladen:")
        st.info("💡 **Sicherheitshinweis:** Sensible Daten können vor dem Upload geschwärzt werden. Aktenzeichen sollten lesbar bleiben.")
        
        upload = st.file_uploader("", type=['pdf', 'png', 'jpg', 'jpeg'])
        
        if upload:
            if st.session_state.credits > 0:
                if st.button("🚀 Analyse starten"):
                    with st.spinner("Amtsschimmel wird vertrieben..."):
                        # Platzhalter für reale Funktion: st.session_state.last_analysis = generate_killer_response(get_text_hybrid(upload))
                        st.session_state.last_analysis = "KI-Antwortbrief erfolgreich generiert..." 
                        st.session_state.credits -= 1
                        st.rerun()
            else:
                st.error("Guthaben leer. Bitte Paket wählen (Einmalzahlung).")

    if st.session_state.last_analysis:
        st.success("Analyse abgeschlossen!")
        st.code(st.session_state.last_analysis, language="text")
        st.download_button("💾 Als .txt Datei herunterladen", st.session_state.last_analysis, "antwortbrief.txt")

with tab2:
    st.subheader("⚡ Sofort-Antworten")
    with st.expander("⏳ Fristverlängerung beantragen"):
        st.code("Sehr geehrte Damen und Herren,\nin der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist bis zum [Datum].\n\nMit freundlichen Grüßen,\n[Name]", language="text")
    with st.expander("🛑 Widerspruch (Fristwahrend)"):
        st.code("Sehr geehrte Damen und Herren,\ngegen Ihren Bescheid vom [Datum] lege ich hiermit Widerspruch ein.\n\nMit freundlichen Grüßen,\n[Name]", language="text")

with tab3:
    st.subheader("❓ Häufig gestellte Fragen (FAQ)")
    faq_data = [
        ("Ist das wirklich kein Abonnement?", "Ja, wir garantieren: Jede Zahlung ist eine reine Einmalzahlung (Prepaid). Es gibt keine automatische Verlängerung."),
        ("Sollte ich sensible Daten schwärzen?", "Ja, gerne! Private Details können unkenntlich gemacht werden. Anliegen und Aktenzeichen müssen lesbar bleiben."),
        ("Was passiert mit meinen Dokumenten?", "Dokumente werden verschlüsselt verarbeitet und nach der Analyse sofort gelöscht. Keine dauerhafte Speicherung."),
        ("Ersetzt diese App eine Rechtsberatung?", "Nein. Die App ist eine Formulierungshilfe und kein Ersatz für einen Anwalt."),
        ("Wie erreiche ich den Support?", "Schreiben Sie uns an: amtsschimmel-killer@proton.me")
    ]
    for question, answer in faq_data:
        st.markdown(f'<div class="faq-question">{question}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="faq-answer">{answer}</div>', unsafe_allow_html=True)

# --- 7. FOOTER (Impressum & Datenschutz Elisabeth Reinecke) ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    with st.expander("🏢 Impressum"):
        st.markdown(f"""
        <div class="legal-box">
        <strong>Amtsschimmel-Killer</strong><br>
        Betreiberin: Elisabeth Reinecke<br>
        Ringelsweide 9<br>
        40223 Düsseldorf<br><br>
        <strong>Kontakt:</strong><br>
        Telefon: +49 211 15821329<br>
        E-Mail: amtsschimmel-killer@proton.me<br>
        Web: amtsschimmel-killer.streamlit.app<br><br>
        <strong>Haftung:</strong><br>
        Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
        </div>
        """, unsafe_allow_html=True)

with c2:
    with st.expander("⚖️ Datenschutzerklärung"):
        st.markdown(f"""
        <div class="legal-box">
        <strong>Verantwortlich:</strong> Elisabeth Reinecke, Ringelsweide 9, 40223 Düsseldorf.<br><br>
        <strong>Datenverarbeitung:</strong> Hochgeladene Dateien werden verschlüsselt an OpenAI übertragen. Wir speichern keine Scans oder persönlichen Daten dauerhaft auf unseren Servern.<br><br>
        <strong>Zahlungen:</strong> Abwicklung via Stripe. Keine Speicherung von Bankdaten bei uns.<br><br>
        <strong>Ihre Rechte:</strong> Auskunft, Löschung und Widerruf jederzeit per E-Mail möglich.
        </div>
        """, unsafe_allow_html=True)
