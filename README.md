# Student Wellness API

A comprehensive backend API for tracking student wellness habits, calculating streaks, and managing group challenges.

## Features

- 🔐 **Firebase Authentication** - Secure user authentication
- 📊 **Habit Tracking** - Track sleep, exercise, water intake, and study habits
- 🔥 **Streak Calculation** - Current and best streaks for each habit
- 👥 **Group Challenges** - Create and join wellness groups
- 🏆 **Leaderboards** - Compare progress with friends
- 📱 **API Documentation** - Interactive Swagger UI

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Firebase** - Authentication and Firestore database
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Run locally: `uvicorn app.main:app --reload`
5. Visit: `http://localhost:8000/docs`

## API Endpoints

- **Authentication**: `/auth/verify`, `/auth/me`
- **Habits**: `/habits/log`, `/habits/logs`, `/habits/streak/{type}`
- **Groups**: `/groups/create`, `/groups/join`, `/groups/my-groups`

## Deployment

Ready for deployment on:
- 🚂 **Railway** - Using `railway.toml`
- 🎨 **Render** - Using `render.yaml`
- 🐳 **Docker** - Using `Dockerfile`

## Environment Variables

GOOGLE_APPLICATION_CREDENTIALS=./firebase-key.json
FIREBASE_PROJECT_ID=your-project-id
CORS_ORIGINS=["http://localhost:3000"]


## License

MIT License
