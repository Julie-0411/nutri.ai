# Diet Plan Chatbot(Nutri.ai) with FastAPI
![logo](https://github.com/user-attachments/assets/5818ea7f-63a8-46cd-974b-646c72258c4e)
## Overview

This project is a chatbot application developed using FastAPI that generates personalized diet plans based on user inputs. The chatbot utilizes the Groq API for natural language processing and sends the generated diet plan via email.

## Features

- **User Interaction**: 
  - The bot interacts with users by asking questions individually to gather details about their name, age, gender, height, weight, and activity level.
  - It prompts users whether they would like a diet plan based on a specific cuisine.

- **Diet Plan Generation**: 
  - After collecting user details, the bot generates a detailed meal plan with precise timings.
  - The bot can also ask whether the user needs exercise recommendations.

- **Email Sending**: 
  - The generated diet plan is sent to the user’s email address as an HTML formatted email with an inline logo image.
  - Users can trigger the email sending by typing "send mail".

- **Motivational Quotes**: 
  - The bot can provide motivational quotes to encourage users.

## Technologies Used

- FastAPI: For building the API.
- Groq API: For natural language processing and diet plan generation.
- SMTP: For sending emails.
- Pydantic: For data validation.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/diet-plan-chatbot.git
   cd diet-plan-chatbot

2. **Create virtual environment**:
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
3. **Install the required packages**
   
4. **Run the application**:

   uvicorn app:app --reload

6. **Access the API**:

  Open your browser and navigate to http://127.0.0.1:8000/docs to view the interactive API documentation.



