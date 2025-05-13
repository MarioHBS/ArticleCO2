@echo off

REM Ativar o ambiente virtual
call .venv\Scripts\activate

REM Ensure the PYTHONPATH includes the src folder
set PYTHONPATH=src;%PYTHONPATH%

REM Run the uvicorn command
uvicorn mapbiomas_api_server:app --reload --host 0.0.0.0 --port 8000