@echo off
echo Iniciando servidor MapBiomas Alert API...

REM Verificar se o ambiente virtual existe
if not exist ".venv" (
    echo Criando ambiente virtual...
    python -m venv .venv
    echo Ambiente virtual criado.
)

REM Ativar o ambiente virtual
echo Ativando ambiente virtual...
call .venv\Scripts\activate

REM Instalar dependências se necessário
echo Verificando dependências...
pip install fastapi uvicorn pydantic requests

REM Configurar PYTHONPATH para incluir a pasta src
echo Configurando PYTHONPATH...
set PYTHONPATH=%CD%\src;%PYTHONPATH%

REM Navegar para a pasta src
cd src

REM Executar o servidor uvicorn
echo Iniciando servidor na porta 8000...
uvicorn mapbiomas_api_server:app --reload --host 0.0.0.0 --port 8000

REM Voltar para o diretório original
cd ..

echo Servidor encerrado.
pause