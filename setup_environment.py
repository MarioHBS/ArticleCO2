#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Configuração do Ambiente - Projeto Serra do Penitente + MapBiomas API

Este script automatiza a configuração inicial do ambiente para ambos os projetos:
1. Serra Penitente Analysis
2. MapBiomas Alert API Server

Funcionalidades:
- Verifica e instala dependências Python
- Cria diretórios necessários
- Configura arquivos de ambiente (.env)
- Valida configuração

Uso:
    python setup_environment.py
"""

import shutil
import subprocess
import sys
from pathlib import Path


def print_header(title):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_step(step_num, description):
    """Imprime passo da configuração."""
    print(f"\n[{step_num}] {description}")
    print("-" * 40)


def check_python_version():
    """Verifica se a versão do Python é compatível."""
    print_step(1, "Verificando versão do Python")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("⚠️  Este projeto requer Python 3.10 ou superior")
        print("📥 Baixe em: https://www.python.org/downloads/")
        return False

    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True


def install_dependencies():
    """Instala dependências do projeto."""
    print_step(2, "Instalando dependências")

    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ Arquivo requirements.txt não encontrado")
        return False

    try:
        print("📦 Instalando dependências...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        print(f"Saída do erro: {e.stderr}")
        return False


def create_directories():
    """Cria diretórios necessários para o projeto."""
    print_step(3, "Criando diretórios")

    directories = [
        "results",
        "results/figures",
        "results/figuras_consolidadas",
        "serra-penitente-analysis/data/generated",
        "serra-penitente-analysis/data/archive",
        "serra-penitente-analysis/data/downloads",
        "logs"
    ]

    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Criado: {directory}")
        else:
            print(f"📁 Já existe: {directory}")

    print("✅ Diretórios configurados")
    return True


def setup_environment_files():
    """Configura arquivos de ambiente (.env)."""
    print_step(4, "Configurando arquivos de ambiente")

    env_example = Path(".env.example")
    env_file = Path(".env")

    if not env_example.exists():
        print("❌ Arquivo .env.example não encontrado")
        return False

    if not env_file.exists():
        shutil.copy(env_example, env_file)
        print("📄 Arquivo .env criado a partir de .env.example")
        print("⚠️  IMPORTANTE: Configure suas credenciais no arquivo .env")
        print("   - MAPBIOMAS_EMAIL: seu email do MapBiomas Alert")
        print("   - MAPBIOMAS_PASSWORD: sua senha do MapBiomas Alert")
    else:
        print("📄 Arquivo .env já existe")

    print("✅ Arquivos de ambiente configurados")
    return True


def validate_mapbiomas_api():
    """Valida se o servidor MapBiomas API pode ser iniciado."""
    print_step(5, "Validando MapBiomas API Server")

    mapbiomas_dir = Path("mapbiomas-alert-api")
    server_script = mapbiomas_dir / "src" / "mapbiomas_api_server.py"

    if not mapbiomas_dir.exists():
        print("❌ Diretório mapbiomas-alert-api não encontrado")
        return False

    if not server_script.exists():
        print("❌ Script do servidor MapBiomas não encontrado")
        return False

    print("✅ MapBiomas API Server - OK")
    return True


def validate_serra_penitente():
    """Valida se o projeto Serra Penitente está configurado."""
    print_step(6, "Validando Serra Penitente Analysis")

    serra_dir = Path("serra-penitente-analysis")
    src_dir = serra_dir / "src"
    data_dir = serra_dir / "data" / "raw"

    if not serra_dir.exists():
        print("❌ Diretório serra-penitente-analysis não encontrado")
        return False

    if not src_dir.exists():
        print("❌ Diretório src não encontrado")
        return False

    # Verificar arquivos de dados essenciais
    required_data_files = [
        "pib_municipios_ibge_2002_2009.xls",
        "pib_municipios_ibge_2010_2021.xlsx",
        "cobertura_solo_mapbiomas_municipios_brasil.xlsx",
        "precos_carbono_eu_ets.xlsx"
    ]

    missing_files = []
    for file_name in required_data_files:
        file_path = data_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)

    if missing_files:
        print("⚠️  Arquivos de dados faltando:")
        for file_name in missing_files:
            print(f"   - {file_name}")
        print("📥 Coloque os arquivos em serra-penitente-analysis/data/raw/")
    else:
        print("✅ Todos os arquivos de dados encontrados")

    print("✅ Serra Penitente Analysis - OK")
    return True


def print_next_steps():
    """Imprime próximos passos para o usuário."""
    print_header("CONFIGURAÇÃO CONCLUÍDA")

    print("🎉 Ambiente configurado com sucesso!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("\n1. Configure suas credenciais:")
    print("   - Edite o arquivo .env")
    print("   - Adicione seu email e senha do MapBiomas Alert")

    print("\n2. Para iniciar o servidor MapBiomas API:")
    print("   python start_mapbiomas_server.py")

    print("\n3. Para executar a análise Serra Penitente:")
    print("   cd serra-penitente-analysis")
    print("   python run_pipeline_validation.py")

    print("\n4. Para executar testes:")
    print("   pytest serra-penitente-analysis/tests/")

    print("\n📚 DOCUMENTAÇÃO:")
    print("   - README.md (raiz do projeto)")
    print("   - serra-penitente-analysis/README.md")
    print("   - mapbiomas-alert-api/README.md")

    print("\n" + "=" * 60)


def main():
    """Função principal do script de configuração."""
    print_header("CONFIGURAÇÃO DO AMBIENTE - SERRA DO PENITENTE + MAPBIOMAS API")

    # Verificar se estamos no diretório correto
    if not Path("serra-penitente-analysis").exists() or not Path("mapbiomas-alert-api").exists():
        print("❌ Execute este script na raiz do projeto")
        print("   Certifique-se de que as pastas serra-penitente-analysis e mapbiomas-alert-api existem")
        sys.exit(1)

    success = True

    # Executar etapas de configuração
    success &= check_python_version()
    success &= install_dependencies()
    success &= create_directories()
    success &= setup_environment_files()
    success &= validate_mapbiomas_api()
    success &= validate_serra_penitente()

    if success:
        print_next_steps()
    else:
        print("\n❌ Configuração falhou. Verifique os erros acima.")
        sys.exit(1)


if __name__ == "__main__":
    main()
