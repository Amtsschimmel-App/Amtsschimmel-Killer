import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Amtsschimmel-Killer", layout="wide")

# --- 2. EXPORT-FUNKTIONEN (Stabil & Auto-Fit) ---
def create_excel(data_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([data_dict])
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(column_len, 60))
    return output.getvalue()

def create_ics_manual(summary, date_str):
    clean_date = "".join(filter(str.isdigit, date_str)) 
    formatted_date = f"{clean_date[4:]}{clean_date[2:4]}{clean_date[:2]}" if len(clean_date) == 8 else datetime.now().strftime("%Y%m%d")
    return f"BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nDTSTART;VALUE=DATE:{formatted_date}\nSUMMARY:Frist: {summary[:30]}...\nEND:VEVENT\nEND:VCALENDAR"

# --- 3. RECHTLICHES & VORLAGEN (Oben fixiert) ---
c_top1, c_top2, c_top3, c_top4 = st.columns(4)
with c_top1:
    with st.expander("⚖️ Impressum"):
        st.markdown("**Amtsschimmel-Killer**\n\nElisabeth Reinecke\nRingelsweide 9\n40223 Düsseldorf\n\n+49 211 15821329\namtsschimmel-killer@proton.me")
with c_top2:
    with st.expander("🛡️ Datenschutz"):
        st.markdown("Verschlüsselt an OpenAI. Keine Speicherung. DSGVO-konform.")
with c_top3:
    with st.expander("❓ FAQ"):
        st.markdown("KEIN ABO. Einmalzahlung für Scans.")
with c_top4:
    with st.expander("📝 Vorlagen"):
        st.code("Widerspruch: Sehr geehrte Damen und Herren...")

st.divider()

# --- 4. HAUPT-LAYOUT (Drei Spalten) ---
col_left, col_mid, col_right = st.columns([1, 1.5, 1.5])

# LINKS: Logo, Sprachen & Pakete
with col_left:
    try:
        st.image("icon_final_blau.png", width=120)
    except:
        st.markdown("🏛️ **Amtsschimmel-Killer**")
    
    st.markdown("### 🌐 Sprachen")
    st.selectbox("Sprache wählen", ["DE Deutsch", "EN English", "TR Türkçe", "PL Polski", "UA Українська", "AR العربية"], label_visibility="collapsed")
    
    st.write("") 
    # Paket 1
    st.markdown("""<div style="background-color: #fdebd0; padding: 10px; border-radius: 10px; border: 1px solid #f8c471;">
        <h5 style="margin:0;">📄 Analyse (1 Dok.)</h5><b>3,99 €</b><br><small>KEIN ABO</small></div>""", unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02", use_container_width=True)
    
    # Paket 2
    st.markdown("""<div style="background-color: #ebf5fb; padding: 10px; border-radius: 10px; border: 1px solid #a9cce3; margin-top:10px;">
        <h5 style="margin:0;">🥈 Spar-Paket (3 Dok.)</h5><b>9,99 €</b><br><small>KEIN ABO</small></div>""", unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/8x228retRbj50paalq1gs03", use_container_width=True)
    
    # Paket 3
    st.markdown("""<div style="background-color: #fef9e7; padding: 10px; border-radius: 10px; border: 1px solid #f7dc6f; margin-top:10px;">
        <h5 style="margin:0;">🥇 Sorglos-Paket (10 Dok.)</h5><b>19,99 €</b><br><small>KEIN ABO</small></div>""", unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04", use_container_width=True)

# MITTE & RECHTS: Dokument & Analyse (Erscheint nach Upload)
with col_mid:
    st.markdown("### 📑 Upload & Vorschau")
    st.success("👑 Admin Guthaben: 999 Scans")
    uploaded_file = st.file_uploader("Dokument hochladen", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.info("📄 PDF geladen. Analyse läuft...")
        else:
            st.image(uploaded_file, use_column_width=True, caption="Vorschau")

with col_right:
    st.markdown("### 🔍 Analyse & Antwort")
    if uploaded_file:
        # Getrennte Boxen untereinander
        st.warning("📅 **Frist erkannt: 24.12.2024**")
        
        with st.container(border=True):
            st.markdown("**Inhaltliche Analyse:**")
            st.write("Die Behörde fordert eine Stellungnahme zu Ihrem Antrag bis zum oben genannten Datum.")
            
        with st.container(border=True):
            st.markdown("**Vorgeschlagener Entwurf:**")
            st.info("Sehr geehrte Damen und Herren, bezugnehmend auf Ihr Schreiben vom...")

# --- 5. DOWNLOAD BEREICH (Ganz unten über volle Breite) ---
if uploaded_file:
    st.divider()
    st.markdown("### 📥 Dokumente herunterladen")
    d1, d2, d3, d4 = st.columns(4)
    
    with d1:
        st.button("📄 PDF Export", use_container_width=True)
    with d2:
        st.button("📝 Word (.docx)", use_container_width=True)
    with d3:
        ex_data = create_excel({"Frist": "24.12.2024", "Analyse": "Stellungnahme erforderlich"})
        st.download_button("📊 Excel (Auto-Fit)", ex_data, "Amtsschimmel_Check.xlsx", use_container_width=True)
    with d4:
        ics_data = create_ics_manual("Behördenfrist", "24.12.2024")
        st.download_button("📅 Kalender (.ics)", ics_data, "Termin.ics", use_container_width=True)

# --- 6. IMPRESSUM & DATENSCHUTZ (Footer) ---
st.divider()
st.caption("Amtsschimmel-Killer | Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")
