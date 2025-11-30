# Translation App (Frontend + Backend)

## Overview
Simple translation UI (React) + Node/Express backend using Azure Translator Text API.

## Setup

### Backend
1. `cd backend`
2. `npm install`
3. copy `.env.example` to `.env` and fill `TRANSLATOR_KEY` and `TRANSLATOR_ENDPOINT` (and `TRANSLATOR_REGION` if needed)
4. `npm run dev` (or `npm start`)

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`
4. Open the Vite dev URL (usually `http://localhost:5173`) and ensure backend runs at `http://localhost:3000`.

## Notes
- The frontend posts to `/api/translate`. If you run frontend and backend on different hosts/ports in production, update the fetch URL or set up a proxy.
- To use Google Cloud Translate instead, replace backend call with `@google-cloud/translate` client and set `GOOGLE_APPLICATION_CREDENTIALS`.
- Protect your API keys and monitor usage/quota.
