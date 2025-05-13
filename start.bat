@echo off
echo Starting PromptWizard UI...

echo Starting backend API...
start cmd /k "cd api && python app.py"

echo Starting frontend...
start cmd /k "cd ui && npm run dev"

echo PromptWizard UI started!
echo Backend API: http://localhost:5000
echo Frontend: http://localhost:3000
