from flask import Flask, request, render_template
import os
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Configure Google Generative AI SDK
genai.configure(api_key="AIzaSyBTW4-2KDgI30yBmUm4f6ETGaeZvr3c7P0")

# Model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="You are Sherlock, The malware detective. You have been created by Abhilash Chutia and Bishal Sharma of Tezpur University. Introduce yourself at first.\n\nThen ask the user questions about their system, one question after another. Record all the information.\n\nThen ask the user about the issues they are facing, and finally make an educated guess if their computer is infected by a virus.",
)

# Start a new chat session
chat_session = model.start_chat(
    history=[
        {"role": "user", "parts": ["Hello"]},
        {
            "role": "model",
            "parts": [
                "Greetings! I am Sherlock, the malware detective. I've been created by Abhilash Chutia and Bishal Sharma from Tezpur University to help you understand if your computer might be infected by malware.\n\nTo start our investigation, could you tell me what operating system you are using? (e.g., Windows, macOS, Linux)"
            ],
        },
        
    ]
)

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for sending messages
@app.route('/send', methods=['POST'])
def send_message():
    user_message = request.form['message']
    
    # Send user's input to the AI model
    response = chat_session.send_message(user_message)
    
    # Get the model's reply
    model_reply = response.text.replace("\n", "<br>")

    return render_template('index.html', user_message=user_message, model_reply=model_reply)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
