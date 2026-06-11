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
    "Algorta": "Mala Testa CH de clima frío (Mulchen), Mala Testa GSM Garnacha Syrah Mourvedre , Winemaker Series Wild Carmenere, Winemaker The Blend, y una sorpresa",
"Almawine": "Sin info",
"Andes Vineyards": "Sin info",
"Chateau Potrero Seco": "Cabernet Franc 2015 , Cabernet Sauvignon 2018, Carmenere 2019 , Petit Verdot. 2018, Red Blend 2018 (Sy, Cr, Cs) , Blend 2022 (55%Mb 45%PV) , GSM 2025 Rosé, GSM Red Blend 2025",
"De Toro Alexander": "Cabernet 2022 Unoaked, Cabernet 2022 Gran Reserva, Carignan Gran Reserva 2022, Ensamblaje Mediterráneo gran reserva 2022 (73% Syrah, 20% Carignan, 7%Garnacha), Cabernet Gran Reserva 2021",
"Epifania Mines": "Sin info",
"Erizo": "Merlot, Chardonnay, Sauvignon Blanc , Syrah, Red Blend,",
"Faraday": "Peti Verdot Ícono",
"Garibaldi": "Sin info",
"Gillmore": "Mariposa Rose, Mariposa Red Blend, Hacedor de Mundos Cabernet Franc, Hacedor de Mundos Merlot, Vigno Carignan",
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

# 5. CHAT LOGIC
placeholder_text = "Type your email here..." if st.session_state.waiting_for_email else "Type your question here..."

# Create a designated container for the main chat and bot responses
chat_container = st.container()

# Place the input box at the bottom of the chat flow
user_input = st.chat_input(placeholder_text)
final_input = button_pressed if button_pressed else user_input

if final_input:
    # Append the user message to history
    st.session_state.messages.append({"role": "user", "content": final_input})
    
    # Process the bot response
    with chat_container:
        with st.chat_message("user"):
            st.markdown(final_input)
            
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            time.sleep(0.6)
            
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

            st.markdown(bot_response)
            
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    st.rerun()

# 6. SECRET ADMIN PANEL (Now pinned cleanly below the input box area)
st.write("") # Adds a tiny spacer
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
