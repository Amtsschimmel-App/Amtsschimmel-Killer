# --- Ausschnitt für Tab 3 (FAQ) ---

with tab3:
    st.subheader("❓ Häufig gestellte Fragen (FAQ)")
    
    faq_data = [
        ("Ist das wirklich kein Abonnement?", 
         "Ja, wir garantieren: Jede Zahlung ist eine reine Einmalzahlung (Prepaid). Es gibt keine versteckten Kosten und keine automatische Verlängerung."),
        
        ("Sollte ich sensible Daten schwärzen?", 
         "Ja, das können Sie gerne tun! Sie können private Details wie Geburtsdaten oder Bankverbindungen auf dem Foto unkenntlich machen. Wichtig für eine gute Antwort der KI ist jedoch, dass das Anliegen der Behörde und – falls vorhanden – das Aktenzeichen lesbar bleiben."),
        
        ("Was passiert mit meinen hochgeladenen Dokumenten?", 
         "Ihre Privatsphäre ist uns wichtig. Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort kurzzeitig verarbeitet und nach der Analyse sofort gelöscht. Wir speichern keine Briefe dauerhaft."),
        
        ("Kann ich die App mehrmals aufrufen?", 
         "Ja! Solange Sie noch Guthaben (Scans) haben, können Sie die App jederzeit nutzen. Ein Scan wird erst abgezogen, wenn Sie die Analyse erfolgreich starten."),
        
        ("Ersetzt diese App eine Rechtsberatung?", 
         "Nein. Der Amtsschimmel-Killer ist eine Formulierungshilfe und ein Werkzeug zum besseren Verständnis von Behördentexten. Er stellt keine Rechtsberatung im Sinne des Gesetzes dar."),
        
        ("Wie erreiche ich den Support?", 
         "Bei Fragen können Sie uns jederzeit eine E-Mail an amtsschimmel-killer@proton.me schreiben.")
    ]
    
    for question, answer in faq_data:
        st.markdown(f'<div class="faq-question">{question}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="faq-answer">{answer}</div>', unsafe_allow_html=True)

# ... (Rest des Codes mit Impressum Elisabeth Reinecke etc. bleibt gleich)
