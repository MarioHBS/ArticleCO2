#!/usr/bin/env python3
"""
Script para executar o servidor MapBiomas Alert API
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    required_packages = ['fastapi', 'uvicorn', 'pydantic', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Dependências faltando: {', '.join(missing_packages)}")
        print("Instalando dependências...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages)
        print("✅ Dependências instaladas")

def setup_environment():
    """Configura o ambiente para execução"""
    # Obter diretório atual
    current_dir = Path(__file__).parent.absolute()
    src_dir = current_dir / "src"
    
    # Configurar PYTHONPATH
    pythonpath = os.environ.get("PYTHONPATH", "")
    src_path = str(src_dir)
    
    if src_path not in pythonpath:
        os.environ["PYTHONPATH"] = f"{src_path}{os.pathsep}{pythonpath}"
        print(f"✅ PYTHONPATH configurado: {src_path}")
    
    # Verificar se o arquivo do servidor existe
    server_file = src_dir / "mapbiomas_api_server.py"
    if not server_file.exists():
        print(f"❌ Arquivo do servidor não encontrado: {server_file}")
        sys.exit(1)
    
    return src_dir

def main():
    """Função principal"""
    print("🚀 Iniciando servidor MapBiomas Alert API...")
    
    # Verificar dependências
    check_dependencies()
    
    # Configurar ambiente
    src_dir = setup_environment()
    
    # Mudar para o diretório src
    os.chdir(src_dir)
    
    print("🌐 Servidor será executado em: http://localhost:8000")
    print("📚 Documentação da API: http://localhost:8000/docs")
    print("⏹️  Para parar o servidor, pressione Ctrl+C")
    print("-" * 50)
    
    try:
        # Executar o servidor uvicorn
        subprocess.run([
            "uvicorn", "mapbiomas_api_server:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Servidor encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
