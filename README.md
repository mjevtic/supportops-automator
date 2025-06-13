# SupportOps Automator

A flexible automation tool for customer support operations that connects support platforms (like Zendesk and Freshdesk) with various action platforms (Slack, Trello, Google Sheets, Notion, Linear, Discord).

## Project Structure

```
├── backend/               # FastAPI backend
│   ├── modules/           # Integration modules
│   │   ├── slack/         # Slack integration
│   │   ├── trello/        # Trello integration
│   │   ├── google_sheets/ # Google Sheets integration
│   │   ├── notion/        # Notion integration
│   │   ├── linear/        # Linear integration
│   │   └── discord/       # Discord integration
│   ├── routes/            # API routes
│   └── services/          # Core services
└── frontend/             # React frontend
    └── Ops-automator/     # Vite + React + TypeScript + Tailwind
```

## Features

- **Rule-based Automation**: Create rules that trigger actions based on events in support platforms
- **Multiple Integrations**: Connect with various platforms for both triggers and actions
- **User-friendly Interface**: Easy-to-use UI for creating and managing rules
- **Webhook Testing Console**: Test webhooks directly from the UI

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend/Ops-automator
npm install
npm run dev
```

## Supported Platforms

### Trigger Platforms
- Zendesk
- Freshdesk

### Action Platforms
- Slack
- Trello
- Google Sheets
- Notion
- Linear
- Discord

## Deployment

The application is designed to be deployed on Railway with separate services for the backend and frontend.