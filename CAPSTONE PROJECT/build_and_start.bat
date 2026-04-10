@echo off
echo ===================================================
echo AgriBlast Full-Stack End-to-End Build System
echo ===================================================
echo.
echo [1/2] Packaging the React Vite Frontend into static files...
cd frontend
call npm install
call npm run build
cd ..

echo.
echo [2/2] Launching the Unified FastAPI Application Server...
echo The application will be available at http://localhost:8000
echo.
cd backend
call .\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
