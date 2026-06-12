import streamlit as st
import os
import time
from datetime import datetime
from rapidfuzz import process, fuzz

# 1. Setup the website title & page config (Adds a nice browser tab icon)
st.set_page_config(page_title="Wine Lover Assistant", page_icon="🍷")
st.title("🤖 Hola Wine Lover! 🍷")

# 2. Define your automated questions and answers
qa_pairs = {
    "Algorta": "Mala Testa Chardonnay, Mala Testa GSM Mezcla Garnacha Syrah Mourvedre , Winemaker Series Wild Carmenere, Winemaker The Blend, y una sorpresa",
"Almawine": "Sin info",
"Andes Vineyards": "Sin info",
"Chateau Potrero Seco": "Cabernet Franc 2015 , Cabernet Sauvignon 2018, Carmenere 2019 , Petit Verdot. 2018, Mezcla Tinta 2018 (Sy, Cr, Cs) , Mezcla Tinta 2022 (55% Malbec 45% Petit Verdot) , Rosé 2025 GSM, Mezcla Tinta 2025 GSM",
"De Toro Alexander": "Cabernet 2022 Unoaked, Cabernet 2022 Gran Reserva, Carignan Gran Reserva 2022, Ensamblaje Mediterráneo gran reserva 2022 (73% Syrah, 20% Carignan, 7%Garnacha), Cabernet Gran Reserva 2021",
"Epifania Wines": "Epifanía The Blend, Oowl Carmenere Gran Reserva, Oowl Cabernet Sauvignon Gran Reserva.",
"Erizo": "Merlot, Chardonnay, Sauvignon Blanc , Syrah, Red Blend,",
"Faraday": "Peti Verdot Ícono",
"Garibaldi": "Sin info",
"Gillmore": "Mariposa Rose, Mariposa Red Blend, Hacedor de Mundos Cabernet Franc, Hacedor de Mundos Merlot, Vigno Carignan",
"Inawines": "Galla de Pelea 2022, Sauvignon Blanc 2025, Rose 2025, Gravita 2022",
"Las Perdices": "Sin info",
"Las Veletas": "Sin info",
"Laura Hartwig": "Sin info",
"Le Coq": "Sin info",
"Moretta Wines": "Carigno del Maule (Carignan)",
"MOVI": "Sin info",
"Peralillo Wines": "Sin info",
"Schwaderer": "Kimbao Malbec, Pinot Noir, Cabernet Sauvignon, Rose, Chardonnay, Syrah",
"Token": "Sin info",
"Viña Choapa": "Sin info",
"Viña Los Quiscos": "Sin info",
"Rondó Viña y Bodega": "Gran Reserva Cabernet Franc 2025, Gran Reserva Cabernet Sauvignon 2019, Gran Reserva Cabernet Sauvignon 2020, Carmenere  2021 Gran Reserva , Airoso Mezcla Tinta , Sauvignon Blanc",
"Viña Testaruda": "LasLarra (Merlot  petit verdot), DisTinto (Syrah Sauvignon Blanc), Zorro Correteado (Carmenere Cabernet Franc), Cabra Suelta (Carignan, Syrah, Gernacha), Testaruda (Cabernet Sauvignon, Malbec, Petit Verdot), RaRo (Cabernet Sauvignon, Syrah, Petit Syrah)",
"Weichafe Wines": "Sauvignon Blanc (varias cosechas), Chardonnay, Pinot Noir 2018 y 1209, Syrah 2022, Cabernet Sauvignon 2023, Syrah 2023, Mezcla Tinta 2022, Fortificado Pinot Noir 2014",
}

# 3. Create the user chat history & Welcome Message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Estoy acá para ayudarte! Abajo están las viñas presentes, si haces click en una, te diré qué vinos tienen hoy para que vayas a conocerlos, que disfrutes!"}
    ]

if "waiting_for_email" not in st.session_state:
    st.session_state.waiting_for_email = None

# Display past conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. PREDEFINED BUTTONS INTERFACE
st.write("---") # Adds a clean dividing line
st.write("💡 **Las viñas que están hoy:**")
button_pressed = None

# Only show buttons if we aren't in the middle of capturing an email
if not st.session_state.waiting_for_email:
    questions_list = list(qa_pairs.keys())
    max_buttons_per_row = 5
    
    # Loop through the questions in chunks of 5
    for i in range(0, len(questions_list), max_buttons_per_row):
        # Get the next chunk of up to 5 questions
        row_questions = questions_list[i : i + max_buttons_per_row]
        
        # Create the exact number of columns needed for this specific row
        cols = st.columns(len(row_questions))
        
        # Render the buttons in this row
        for idx, question in enumerate(row_questions):
            with cols[idx]:
                # Unique key using the global index (i + idx) to prevent Streamlit duplicate errors
                global_idx = i + idx
                if st.button(question, key=f"btn_{global_idx}", use_container_width=True):
                    button_pressed = question

# 5. CHAT LOGIC (Using a standard layout box instead of a floating input)
st.write("---")
st.write("💬 **Chat Room:**")

# Create a clean side-by-side layout for typing and submitting
placeholder_text = "Type your email here..." if st.session_state.waiting_for_email else "Type your question here..."

# Form layout forces the text input box and send button to sit on a fixed row
with st.form(key="chat_form", clear_on_submit=True):
    chat_cols = st.columns([4, 1]) # 4 parts text box, 1 part button
    with chat_cols[0]:
        user_typed_input = st.text_input("", placeholder=placeholder_text, label_visibility="collapsed")
    with chat_cols[1]:
        submit_button = st.form_submit_button(label="Send", use_container_width=True)

# Determine what action triggered the message
final_input = None
if button_pressed:
    final_input = button_pressed
elif submit_button and user_typed_input:
    final_input = user_typed_input

if final_input:
    # Append user message to history
    st.session_state.messages.append({"role": "user", "content": final_input})
    
    # Process the bot response
    if st.session_state.waiting_for_email:
        user_email = final_input.strip()
        unanswered_question = st.session_state.waiting_for_email
        
        log_entry = f"Date: {datetime.now()} | Email: {user_email} | Question: {unanswered_question}\n"
        with open("leads_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
            
        bot_response = "Thank you! I have saved your details. Our team will email you an answer shortly."
        st.session_state.waiting_for_email = None
    else:
        clean_input = final_input.lower().strip()
        questions_list = list(qa_pairs.keys())
        
        best_match = process.extractOne(clean_input, questions_list, scorer=fuzz.WRatio, score_cutoff=70)
        
        if best_match:
            matched_question = best_match[0]
            bot_response = qa_pairs[matched_question]
        else:
            bot_response = "I'm not quite sure about that one. Would you mind leaving your email address so our team can get back to you directly?"
            st.session_state.waiting_for_email = final_input

    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.rerun()

# 6. SECRET ADMIN PANEL (Now physically guaranteed to be at the bottom)
st.write("---")
with st.expander("🔒 Admin Panel (Leads Log)"):
    password = st.text_input("Enter Admin Password:", type="password")
    
    if password == "mysecret123":
        if os.path.exists("leads_log.txt"):
            with open("leads_log.txt", "r", encoding="utf-8") as f:
                leads_data = f.read()
            
            st.text_area("Current Leads:", leads_data, height=200)
            
            st.download_button(
                label="📥 Download leads_log.txt",
                data=leads_data,
                file_name="leads_log.txt",
                mime="text/plain"
            )
        else:
            st.write("No leads collected yet!")
