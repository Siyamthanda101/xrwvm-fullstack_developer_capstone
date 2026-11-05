# Best Cars Dealership Capstone

A full-stack dealership application built as a developer capstone. The project combines a Django application and React frontend with a Node.js/Express API backed by MongoDB.

## Features

- Browse dealerships and filter them by state.
- View dealership details and customer reviews.
- Register, sign in, and sign out.
- Submit reviews as an authenticated user.
- Analyze review sentiment with the sentiment-analysis service.

## Project layout

- `server/djangoapp/` — Django views, URL routes, and backend service clients.
- `server/djangoproj/` — Django project configuration.
- `server/frontend/` — React application and static pages.
- `server/database/` — Express API, MongoDB models, and seed data.

## Local development

Run the Django application from the repository root:

```powershell
.\.venv\Scripts\python.exe .\server\manage.py runserver
```

The dealership API and sentiment-analysis service are separate dependencies and must also be running for dealer data and sentiment features.
