# --- 4. SESSION STATE & ADMIN-LOGIK ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []
if "last_fristen" not in st.session_state: st.session_state.last_fristen = ""
if "last_brief" not in st.session_state: st.session_state.last_brief = ""

params = st.query_params

# ADMIN CHECK
is_admin = params.get("admin") == ADMIN_PASSWORT
if is_admin and st.session_state.credits < 100: 
    st.session_state.credits = 999

# STRIPE RÜCKKEHR LOGIK (SCHÖNER)
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        session = stripe.checkout.Session.retrieve(params["session_id"])
        if session.payment_status in ["paid", "no_payment_required"]:
            pack_size = int(params.get("pack", 1))
            st.session_state.credits += pack_size
            st.session_state.processed_sessions.append(params["session_id"])
            
            # SCHÖNE MELDUNG & EFFEKT
            st.balloons() # Konfetti-Regen! 🎈
            st.success(f"✨ Dankeschön! {pack_size} Analyse(n) wurden deinem Konto gutgeschrieben.")
            
            # URL säubern ohne Seite komplett neu zu laden
            st.query_params.clear()
            st.toast("Guthaben aktualisiert!", icon="💳")
    except Exception as e:
        st.error("Da gab es ein Problem mit der Zahlungsbestätigung.")

# --- 5. SIDEBAR ---
with st.sidebar:
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    if is_admin: st.warning("🔓 Admin-Zugriff aktiv")
    st.divider()
    st.subheader("💳 Guthaben laden")
    st.caption("Einmalzahlung • Kein Abo")
    
    # Deine Links aus den Secrets
    packages = [
        ("📄 1 Analyse", st.secrets["STRIPE_LINK_1"], "3,99 €"),
        ("🚀 Spar-Paket (3)", st.secrets["STRIPE_LINK_3"], "9,99 €"),
        ("💎 Sorglos-Paket (10)", st.secrets["STRIPE_LINK_10"], "19,99 €")
    ]
    
    for title, link, price in packages:
        st.markdown(f'<a href="{link}" target="_blank" class="buy-button"><b>{title}</b><br><small>{price} | Sofort-Freischaltung</small></a>', unsafe_allow_html=True)
