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
    .result-box { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 10px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); }
    .faq-question { font-weight: bold; color: #1e3a8a; margin-top: 15px; font-size: 1.1em; }
    .faq-answer { margin-bottom: 15px; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
# Sicherstellen, dass Secrets existieren, bevor sie geladen werden
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
if "STRIPE_API_KEY" in st.secrets:
    stripe.api_key = st.secrets["STRIPE_API_KEY"]

# --- 4. SESSION STATE ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""

# --- 5. SIDEBAR (Guthaben & Pakete) ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI): 
        st.image(LOGO_DATEI)
    else:
        st.title("📄 Amtsschimmel-Killer")
        
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    st.divider()
    st.subheader("Guthaben aufladen")
    
    # Pakete aus den Secrets laden
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
    with s1: st.markdown('<div class="step-box"><b>1. Guthaben wählen</b><br><small>Paket links buchen.<br>Garantierte Einmalzahlung.</small></div>', unsafe_allow_html=True)
    with s2: st.markdown('<div class="step-box"><b>2. Brief hochladen</b><br><small>Foto oder PDF hochladen.<br>Wir lesen das "Amtsdeutsch".</small></div>', unsafe_allow_html=True)
    with s3: st.markdown('<div class="step-box"><b>3. Antwort nutzen</b><br><small>Antwort kopieren, Aktenzeichen ergänzen & abschicken.</small></div>', unsafe_allow_html=True)
    
    st.divider()

    # Neustart-Button wenn Ergebnis da ist
    if st.session_state.last_analysis:
        if st.button("🔄 Nächsten Brief bearbeiten"):
            st.session_state.last_analysis = ""
            st.rerun()

    # Upload & Analyse
    if not st.session_state.last_analysis:
        st.subheader("Hier Brief hochladen:")
        st.info("💡 **Sicherheitshinweis:** Du kannst sensible private Daten (wie Geburtsdatum oder Kontonummer) auf dem Foto vor dem Hochladen schwärzen. Aktenzeichen sollten für eine präzise Antwort lesbar bleiben.")
        
        upload = st.file_uploader("", type=['pdf', 'png', 'jpg', 'jpeg'])
        
        if upload:
            if st.session_state.credits > 0:
                if st.button("🚀 Analyse starten"):
                    with st.spinner("Amtsschimmel wird vertrieben..."):
                        # Hier würde deine Textextraktions-Logik stehen
                        st.session_state.last_analysis = "Analyse-Beispiel: Ihr Brief wurde erkannt. Aktenzeichen: 12345. Bitte antworten Sie bis zum 15. des Monats..." 
                        st.session_state.credits -= 1
                        st.rerun()
            else:
                st.error("Guthaben leer. Bitte wähle ein Paket in der Seitenleiste (Einmalzahlung).")

    # Ergebnis-Darstellung
    if st.session_state.last_analysis:
        st.success("Analyse abgeschlossen!")
        st.markdown(f'<div class="result-box">{st.session_state.last_analysis}</div>', unsafe_allow_html=True)
        st.divider()
        st.subheader("📲 Text kopieren & speichern")
        st.code(st.session_state.last_analysis, language="text")
        st.download_button("💾 Als .txt Datei herunterladen", st.session_state.last_analysis, "antwortbrief.txt")

with tab2:
    st.subheader("⚡ Sofort-Antworten")
    st.info("Kopiere diese Vorlagen direkt für schnelle Reaktionen:")
    with st.expander("⏳ Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren,\nin der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist bis zum [Datum].\n\nMit freundlichen Grüßen,\n[Name]", language="text")
    with st.expander("🛑 Widerspruch (Fristwahrend)"):
        st.code("Sehr geehrte Damen und Herren,\ngegen Ihren Bescheid vom [Datum] lege ich hiermit Widerspruch ein.\n\nMit freundlichen Grüßen,\n[Name]", language="text")

with tab3:
    st.subheader("❓ Häufig gestellte Fragen (FAQ)")
    faq_data = [
        ("Ist das wirklich kein Abonnement?", "Ja, wir garantieren: Jede Zahlung ist eine reine Einmalzahlung (Prepaid). Es gibt keine automatische Verlängerung."),
        ("Sollte ich sensible Daten schwärzen?", "Ja, gerne! Private Details wie Geburtsdaten können unkenntlich gemacht werden. Anliegen und Aktenzeichen müssen lesbar bleiben."),
        ("Was passiert mit meinen Dokumenten?", "Dokumente werden verschlüsselt verarbeitet und nach der Analyse sofort gelöscht. Keine dauerhafte Speicherung."),
        ("Ersetzt diese App eine Rechtsberatung?", "Nein. Die App ist eine Formulierungshilfe und kein Ersatz für einen Anwalt."),
        ("Wie erreiche ich den Support?", "Schreiben Sie uns an: amtsschimmel-killer@proton.me")
    ]
    for question, answer in faq_data:
        st.markdown(f'<div class="faq-question">{question}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="faq-answer">{answer}</div>', unsafe_allow_html=True)

# --- 7. FOOTER ---
st.divider()
c1, c2 = st.columns(2)
with c1:
    with st.expander("🏢 Impressum"):
        st.markdown(f"""<div class="legal-box"><b>Betreiberin:</b> Elisabeth Reinecke<br>Ringelsweide 9, 40223 Düsseldorf<br>Tel: +49 211 15821329<br>E-Mail: amtsschimmel-killer@proton.me<br>Web: amtsschimmel-killer.streamlit.app</div>""", unsafe_allow_html=True)
with c2:
    with st.expander("⚖️ Datenschutz"):
        st.markdown(f"""<div class="legal-box">Verantwortlich: Elisabeth Reinecke. Datenübertragung via SSL. Keine dauerhafte Speicherung von Scans. Zahlungsabwicklung via Stripe.</div>""", unsafe_allow_html=True)
