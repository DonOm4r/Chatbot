import streamlit as st
from openai import OpenAI
import os
import dotenv
import time

# Cargar la clave API de OpenAI desde el archivo .env
dotenv.load_dotenv()
API_KEY = os.environ.get('OPENAI_API_KEY')
ASSISTANT_ID = os.environ.get('ASSISTANT_ID')
VECTORST_ID= os.environ.get('VECTORST_ID')


# Configurar OpenAI con la clave API
client = OpenAI(api_key=API_KEY)

# Función para generar respuesta del chatbot
def get_response(query):
    # Crear un hilo con el mensaje del usuario
    thread = client.beta.threads.create(
        messages=[{"role": "user", "content": query}],
        tool_resources={
            "file_search": {
                "vector_store_ids": [VECTORST_ID]
        }
        }
    )

    # Enviar el hilo al asistente y esperar la respuesta
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(1)

    # Obtener la respuesta del asistente
    response = client.beta.threads.messages.list(thread_id=thread.id)
    return response.data[0].content[0].text.value

# Inicializar la sesión de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Chatbot plagio")
st.markdown("---")

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario
if prompt := st.chat_input("Ingresa tu consulta:"):
    # Agregar mensaje de usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            message_placeholder = st.empty()
            full_response = ""

            response = get_response(prompt)

            for char in response:
                full_response += char
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.05)

            message_placeholder.markdown(full_response)

    # Agregar respuesta al historial
    st.session_state.messages.append({"role": "assistant", "content": response})