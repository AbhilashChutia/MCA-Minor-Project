from flask import Flask, request, render_template, session, redirect, url_for
from translate import Translator
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

genai.configure(api_key="AIzaSyAJWMd37V47V5M8_OYmtK41u6ONLnL7yuI")
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=(
        "You are Sherlock, The malware detective. You have been created by "
        "Abhilash Chutia and Bishal Sharma of Tezpur University. Introduce yourself at first.\n\n"
        "Then ask the user questions about their system, one question after another. Record all the information.\n\n"
        "Then ask the user about the issues they are facing, and finally make an educated guess if their computer is infected by a virus."
    ),
)

chat_session = model.start_chat(
    history=[
        {"role": "user", "parts": ["Hello"]},
        {
            "role": "model",
            "parts": [
                "Greetings! I am Sherlock, the malware detective. I've been created by Abhilash Chutia and Bishal Sharma from Tezpur University to help you understand if your computer might be infected by malware.\n\n"
                "To start our investigation, could you tell me what operating system you are using? (e.g., Windows, macOS, Linux)"
            ],
        },
    ]
)

translator = Translator(to_lang="as")  

def translate_text_free(text):
    """Translates text into Assamese using the free translate library."""
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text 

@app.route('/select_language')
def select_language():
    """Renders the language selection page."""
    return render_template('select_language.html')

@app.route('/set_language/<language>')
def set_language(language):
    """Sets the language and initializes the chat session."""
    session['language'] = language
    session['chat_history'] = [
        {"role": "user", "text": "Hello"},
        {
            "role": "model",
            "text": (
                "Greetings! I am Sherlock, the malware detective. I've been created by Abhilash Chutia and Bishal Sharma from Tezpur University to help you understand if your computer might be infected by malware.\n\n"
                "To start our investigation, could you tell me what operating system you are using? (e.g., Windows, macOS, Linux)"
            ),
        },
    ]
    return redirect(url_for('home'))

@app.route('/')
def home():
    """Renders the chatbot page based on the selected language."""
    if 'language' not in session:
        return redirect(url_for('select_language'))

    chat_history = session.get('chat_history', [])
    return render_template('index.html', chat_history=chat_history, language=session['language'])

@app.route('/send', methods=['POST'])
def send_message():
    """Handles user input and updates the chatbot session."""
    user_message = request.form['message']
    language = session.get('language', 'en')

    response = chat_session.send_message(user_message)
    model_reply = response.text.replace("\n", "<br>")

    translated_reply = translate_text_free(model_reply) if language == 'as' else model_reply

    session['chat_history'].append({"role": "user", "text": user_message})
    session['chat_history'].append({"role": "model", "text": translated_reply})
    session.modified = True

    return render_template('index.html', chat_history=session['chat_history'], language=language)

if __name__ == '__main__':
    app.run(debug=True)
