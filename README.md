# BMCC StudyTogether

BMCC StudyTogether is a student collaboration platform created for a Database Systems class project. The application helps students access course materials, study resources, videos, and collaboration tools in one place.

# Youtube
https://www.youtube.com/watch?v=WClV8SrQPr8

## Screenshots

### Registration Page
<img width="1462" height="827" alt="create Account" src="https://github.com/user-attachments/assets/4fd3fca6-030b-45b2-ac82-8dba40af5056" />

### Dashboard
<img width="1470" height="920" alt="Dashboard 1" src="https://github.com/user-attachments/assets/302535c2-110f-4bb1-9cee-02d48a1019b4" />


## Features

- Student registration and login
- Course dashboard
- Study session scheduling
- Live study rooms
- AI Study Assistant
- Course resources and videos
- SQLite database integration

## Technologies Used

- Python
- Flask
- SQLite
- HTML/CSS
- JavaScript
- OpenAI API

## Run Locally

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Then add your OpenAI API key inside `.env`:

```text
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Start the Flask app:

```bash
python app.py
```

Then open the login page:

```text
http://127.0.0.1:5002/login
```

You can also open:

```text
http://127.0.0.1:5002/
```

The home route redirects to the login page.

## AI Study Assistant

The AI Study Assistant uses the official OpenAI Python SDK through `ai_helper.py`.

- API provider: OpenAI
- SDK package: `openai`
- Environment loader: `python-dotenv`
- API key variable: `OPENAI_API_KEY`
- Optional model variable: `OPENAI_MODEL`
- Default model: `gpt-4o-mini`

Student questions are sent to OpenAI with course context from the Flask app. The assistant returns a study response with a short summary, explanation, three practice questions, and study tips.

Do not upload your real `.env` file or API key to GitHub. Use `.env.example` as the public template.



## Author

Created by Evis Saliaj for BMCC Database Systems coursework.
