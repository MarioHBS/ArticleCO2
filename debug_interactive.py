# debug_interactive.py
# -*- coding: utf-8 -*-
"""
Script de Debug Interativo

Este script fornece um ambiente interativo para debug e exploração
dos componentes do projeto Serra Penitente + MapBiomas.

Funcionalidades:
- Carregamento automático de módulos principais
- Funções de utilidade para debug
- Acesso rápido a dados e configurações
- Testes interativos de componentes

Uso:
    python debug_interactive.py
"""

import sys
from pathlib import Path

# Adicionar caminhos ao PYTHONPATH
project_root = Path(__file__).parent
serra_path = project_root / "serra-penitente-analysis"
mapbiomas_path = project_root / "mapbiomas-alert-api"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(serra_path))
sys.path.insert(0, str(mapbiomas_path))

# Imports principais
try:
    from datetime import datetime

    import pandas as pd
    import requests
    print("✅ Bibliotecas principais carregadas")
except ImportError as e:
    print(f"❌ Erro ao importar bibliotecas: {e}")

# Tentar carregar módulos do projeto
try:
    # Módulos Serra Penitente
    if (serra_path / "variaveis.py").exists():
        sys.path.insert(0, str(serra_path))
        import variaveis as serra_vars
        print("✅ Variáveis Serra Penitente carregadas")
    else:
        serra_vars = None
        print("⚠️  Módulo variaveis.py não encontrado")
except ImportError as e:
    serra_vars = None
    print(f"⚠️  Erro ao carregar variaveis.py: {e}")

# Configurações
SERVER_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{SERVER_URL}/health"


def print_header(title):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def check_environment():
    """Verifica o ambiente do projeto."""
    print_header("VERIFICAÇÃO DO AMBIENTE")

    # Verificar Python
    print(f"🐍 Python: {sys.version}")

    # Verificar diretórios
    dirs_to_check = [
        ("Serra Penitente", serra_path),
        ("MapBiomas API", mapbiomas_path),
        ("Results", project_root / "results"),
        ("Logs", project_root / "logs")
    ]

    for name, path in dirs_to_check:
        status = "✅" if path.exists() else "❌"
        print(f"{status} {name}: {path}")

    # Verificar arquivos importantes
    files_to_check = [
        ("requirements.txt", project_root / "requirements.txt"),
        (".env", project_root / ".env"),
        ("variaveis.py", serra_path / "variaveis.py"),
        ("main.py (MapBiomas)", mapbiomas_path / "main.py")
    ]

    for name, path in files_to_check:
        status = "✅" if path.exists() else "❌"
        print(f"{status} {name}: {path}")


def check_server():
    """Verifica status do servidor MapBiomas."""
    print_header("STATUS DO SERVIDOR MAPBIOMAS")

    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Servidor MapBiomas disponível")
            print(f"📊 Status: {data.get('status', 'unknown')}")
            print(f"🌐 URL: {SERVER_URL}")
            return True
        else:
            print(f"❌ Servidor retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Servidor não disponível: {e}")
        print("💡 Inicie com: python start_mapbiomas_server.py")
        return False


def show_serra_variables():
    """Mostra variáveis do projeto Serra Penitente."""
    print_header("VARIÁVEIS SERRA PENITENTE")

    if serra_vars is None:
        print("❌ Módulo variaveis.py não carregado")
        return

    # Mostrar municípios alvo
    if hasattr(serra_vars, 'MUNICIPIOS_ALVO'):
        print(f"🏘️  Municípios Alvo: {len(serra_vars.MUNICIPIOS_ALVO)}")
        for municipio in serra_vars.MUNICIPIOS_ALVO:
            print(f"   - {municipio}")

    # Mostrar caminhos
    if hasattr(serra_vars, 'INPUT_PATHS'):
        print(f"\n📁 Caminhos de Entrada: {len(serra_vars.INPUT_PATHS)}")
        for key, path in serra_vars.INPUT_PATHS.items():
            exists = "✅" if Path(path).exists() else "❌"
            print(f"   {exists} {key}: {path}")

    if hasattr(serra_vars, 'RESULT_PATHS'):
        print(f"\n📊 Caminhos de Resultado: {len(serra_vars.RESULT_PATHS)}")
        for key, path in serra_vars.RESULT_PATHS.items():
            print(f"   - {key}: {path}")


def test_data_loading():
    """Testa carregamento de dados."""
    print_header("TESTE DE CARREGAMENTO DE DADOS")

    if serra_vars is None:
        print("❌ Módulo variaveis.py não carregado")
        return

    if not hasattr(serra_vars, 'INPUT_PATHS'):
        print("❌ INPUT_PATHS não encontrado")
        return

    for name, path in serra_vars.INPUT_PATHS.items():
        file_path = Path(path)
        if file_path.exists():
            try:
                if file_path.suffix in ['.xlsx', '.xls']:
                    df = pd.read_excel(file_path, nrows=5)
                    print(f"✅ {name}: {df.shape} (primeiras 5 linhas)")
                    print(f"   Colunas: {list(df.columns)[:5]}...")
                elif file_path.suffix == '.csv':
                    df = pd.read_csv(file_path, nrows=5)
                    print(f"✅ {name}: {df.shape} (primeiras 5 linhas)")
                    print(f"   Colunas: {list(df.columns)[:5]}...")
                else:
                    print(f"⚠️  {name}: Formato não testado ({file_path.suffix})")
            except Exception as e:
                print(f"❌ {name}: Erro ao carregar - {e}")
        else:
            print(f"❌ {name}: Arquivo não encontrado - {path}")


def show_project_stats():
    """Mostra estatísticas do projeto."""
    print_header("ESTATÍSTICAS DO PROJETO")

    # Contar arquivos Python
    py_files = list(project_root.rglob("*.py"))
    print(f"🐍 Arquivos Python: {len(py_files)}")

    # Contar arquivos de dados
    data_extensions = ['.xlsx', '.xls', '.csv', '.json']
    data_files = []
    for ext in data_extensions:
        data_files.extend(list(project_root.rglob(f"*{ext}")))
    print(f"📊 Arquivos de Dados: {len(data_files)}")

    # Verificar resultados
    results_dir = project_root / "results"
    if results_dir.exists():
        csv_files = list(results_dir.rglob("*.csv"))
        png_files = list(results_dir.rglob("*.png"))
        pdf_files = list(results_dir.rglob("*.pdf"))
        print(f"📈 Resultados CSV: {len(csv_files)}")
        print(f"🖼️  Figuras PNG: {len(png_files)}")
        print(f"📄 Figuras PDF: {len(pdf_files)}")

    # Verificar logs
    logs_dir = project_root / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.rglob("*.log"))
        print(f"📝 Arquivos de Log: {len(log_files)}")


def interactive_menu():
    """Menu interativo para debug."""
    while True:
        print_header("MENU DE DEBUG INTERATIVO")
        print("1. 🔍 Verificar Ambiente")
        print("2. 🌐 Status Servidor MapBiomas")
        print("3. 📊 Variáveis Serra Penitente")
        print("4. 🧪 Testar Carregamento de Dados")
        print("5. 📈 Estatísticas do Projeto")
        print("6. 🐍 Console Python Interativo")
        print("0. ❌ Sair")

        choice = input("\n🔢 Escolha uma opção: ").strip()

        if choice == "1":
            check_environment()
        elif choice == "2":
            check_server()
        elif choice == "3":
            show_serra_variables()
        elif choice == "4":
            test_data_loading()
        elif choice == "5":
            show_project_stats()
        elif choice == "6":
            print("\n🐍 Entrando no console Python...")
            print("💡 Variáveis disponíveis: serra_vars, pd")
            print("💡 Funções disponíveis: check_environment(), check_server()")
            print("💡 Digite 'exit()' para voltar ao menu")
            import code
            code.interact(local=locals())
        elif choice == "0":
            print("👋 Saindo do debug interativo...")
            break
        else:
            print("❌ Opção inválida")

        input("\n⏸️  Pressione Enter para continuar...")


def main():
    """Função principal."""
    print_header("DEBUG INTERATIVO - SERRA PENITENTE + MAPBIOMAS")
    print("🔧 Ambiente de debug carregado")
    print(f"📁 Diretório: {project_root}")
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Verificação inicial rápida
    print("\n🔍 Verificação inicial:")
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    print(f"{'✅' if serra_path.exists() else '❌'} Serra Penitente")
    print(f"{'✅' if mapbiomas_path.exists() else '❌'} MapBiomas API")
    print(f"{'✅' if serra_vars else '❌'} Variáveis carregadas")

    # Menu interativo
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Debug interativo interrompido")
    except Exception as e:
        print(f"\n❌ Erro no debug interativo: {e}")


if __name__ == "__main__":
    main()
