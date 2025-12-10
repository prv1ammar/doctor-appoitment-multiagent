@echo off
echo Starting Doctor Appointment System...
echo.

echo 1. Starting FastAPI backend on http://127.0.0.1:8003
start cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8003"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo 2. Starting Streamlit frontend on http://localhost:8501
start cmd /k "streamlit run frontend/app.py"

echo.
echo Both servers are now running.
echo - Backend: http://127.0.0.1:8003
echo - Frontend: http://localhost:8501
echo.
echo Open your browser to http://localhost:8501 to use the application.
pause
