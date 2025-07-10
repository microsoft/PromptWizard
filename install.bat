@echo off
echo Installing PromptWizard UI dependencies...

echo Installing backend dependencies...
cd api
pip install -r requirements.txt
cd ..

echo Installing frontend dependencies...
cd ui
npm install
cd ..

echo Installation complete!
echo Run 'start.bat' to start the application.
