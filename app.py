from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from groq import Groq
import random

app = FastAPI()

# Groq client initialization
client = Groq(api_key='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')

# In-memory store for user chat sessions
user_sessions: Dict[str, Dict] = {}

# Request body for the chat endpoint
class ChatRequest(BaseModel):
    name: str
    user_message: str
    email: str  # Add user's email to the request model

# Helper function to format responses
def format_response(response: str) -> str:
    # Split sentences and add newline after each
    formatted = response.replace('. ', '.\n')
    return formatted.strip()

# Function to generate a random motivational quote
def generate_random_quote() -> str:
    quotes = [
        "Believe you can and you're halfway there.",
        "The only way to do great work is to love what you do.",
        "You are never too old to set another goal or to dream a new dream.",
        "Act as if what you do makes a difference. It does.",
        "Success is not how high you have climbed, but how you make a positive difference to the world."
    ]
    return random.choice(quotes)

# Function to send an email with the diet plan and logo as inline image
def send_email_with_diet_plan(to_email: str, diet_plan: str, logo_path: str):
    try:
        # Email credentials (replace these with your credentials)
        from_email = "71762108016@cit.edu.in"
        password = "cit202110"

        # Create email message
        msg = MIMEMultipart("related")  # Use "related" for inline images
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = "Your Diet Plan"

        # Create the HTML body with the diet plan and logo
        body = f"""
        <html>
            <body>
                <p>Here is your diet plan:</p>
                <p>{diet_plan}</p>
                <img src="cid:logo" alt="Logo" />
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Attach the logo image as inline
        with open(logo_path, 'rb') as img:
            logo = MIMEImage(img.read())
            logo.add_header('Content-ID', '<logo>')
            msg.attach(logo)

        # Send email using SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")

# Helper function to check if diet plan has been generated
def has_diet_plan(chat_history):
    for chat in chat_history:
        if chat["role"] == "assistant" and "breakfast" in chat["content"].lower():
            return True
    return False

# Helper function to extract diet plan from chat history
def extract_diet_plan(chat_history):
    for chat in chat_history:
        if chat["role"] == "assistant" and "breakfast" in chat["content"].lower():
            return chat["content"]
    return "No diet plan found."

# Endpoint to handle user responses dynamically
@app.post("/chat/")
async def chat(request: ChatRequest):
    name = request.name
    user_message = request.user_message
    user_email = request.email

    # Initialize a session for a new user
    if name not in user_sessions:
        user_sessions[name] = {
            "chat_history": [{"role": "system", "content": """
1. Ask the user questions individually to gather details about:
   - name
   - age
   - gender
   - height
   - weight
   - activity level (sedentary, moderately active, very active)

2. After gathering user details, ask:
   - "Would you like a diet plan based on a specific cuisine?"

3. Once the user confirms, provide a detailed meal plan with precise timings (e.g., breakfast at 6:00 am, lunch at 12:00 pm).

4. After giving the diet plan, ask:
   - whether the user needs exercise recommendations as well
                              
5. Ask the user whether they want to gain or lose weight before giving diet plan

Response format:
- The response should be in neat format that each sentence should be in a newline.
- The diet plan and exercise plans should be shorter at most 200 words.
- Always respond with concise, precise, and formatted outputs.
- Sound like a human, not like a robot.
"""}],
            "details": {},
            "state": "awaiting_details"
        }

    # Conversation flow management
    session = user_sessions[name]
    state = session["state"]

    # Add user message to chat history
    session["chat_history"].append({"role": "user", "content": user_message})

    # Debugging information
    print(f"User message: {user_message}")
    print(f"User details: {session['details']}")

    # Check if the user says "send mail" to trigger the email sending
    if "send mail" in user_message.lower():
        # Check if the diet plan has been generated
        if has_diet_plan(session["chat_history"]):
            # Extract the diet plan from the chat history
            diet_plan = extract_diet_plan(session["chat_history"])

            # Path to the logo image
            logo_image_path = "logo.png"  # Replace with your actual logo path

            # Send the diet plan via email
            send_email_with_diet_plan(user_email, diet_plan, logo_image_path)
            # Acknowledge the email has been sent
            return {
                "status": "success",
                "message": "Your diet plan has been sent to your email."
            }
        else:
            return {
                "status": "error",
                "message": "No diet plan has been generated yet."
            }

    # Perform inference using Groq and Llama to get the next question or recommendation
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=session["chat_history"],
            temperature=1,  # Lower temperature for more deterministic responses
            max_tokens=1024,  # Limit to short responses
            top_p=1,
            stream=True,
            stop=None,
        )

        # Collect the model's response
        next_question = ""
        for chunk in completion:
            next_question += chunk.choices[0].delta.content or ""

        # Format the response using the helper function
        formatted_response = format_response(next_question)

        # Add the assistant's response to chat history
        session["chat_history"].append({"role": "assistant", "content": formatted_response})

        return {
            "status": "success",
            "message": formatted_response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "message": str(e).replace('\n', ' ')
        })

# Run the FastAPI server using `uvicorn main:app --reload`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
