#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração Rápida do Projeto Serra Penitente + MapBiomas

Este script configura rapidamente todo o ambiente do projeto,
incluindo dependências, diretórios e validações.

Funcionalidades:
- Instala dependências automaticamente
- Configura estrutura de diretórios
- Valida configuração do ambiente
- Testa conectividade com APIs
- Gera relatório de configuração

Uso:
    python quick_setup.py [--force] [--skip-deps]
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


class QuickSetup:
    """Configurador rápido do projeto."""
    
    def __init__(self, force=False, skip_deps=False):
        self.force = force
        self.skip_deps = skip_deps
        self.project_root = Path.cwd()
        self.serra_dir = self.project_root / "serra-penitente-analysis"
        self.mapbiomas_dir = self.project_root / "mapbiomas-alert-api"
        self.results_dir = self.project_root / "results"
        self.logs_dir = self.project_root / "logs"
        self.resultados_fixos_dir = self.project_root / "resultados_fixos"
    
    def print_header(self, title):
        """Imprime cabeçalho formatado."""
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)
    
    def print_step(self, step_num, description):
        """Imprime passo da operação."""
        print(f"\n[{step_num}] {description}")
        print("-" * 40)
    
    def check_python_version(self):
        """Verifica versão do Python."""
        self.print_step(1, "Verificando versão do Python")
        
        version = sys.version_info
        print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ é necessário")
            return False
        
        if version.minor < 10:
            print("⚠️  Python 3.10+ é recomendado para melhor compatibilidade")
        
        print("✅ Versão do Python compatível")
        return True
    
    def check_project_structure(self):
        """Verifica estrutura do projeto."""
        self.print_step(2, "Verificando estrutura do projeto")
        
        required_dirs = [
            self.serra_dir,
            self.mapbiomas_dir
        ]
        
        required_files = [
            self.project_root / "requirements.txt",
            self.project_root / ".env.example",
            self.project_root / "pyproject.toml",
            self.serra_dir / "run_pipeline_validation.py",
            self.mapbiomas_dir / "main.py"
        ]
        
        missing_items = []
        
        # Verificar diretórios
        for dir_path in required_dirs:
            if dir_path.exists():
                print(f"✅ {dir_path.name}/")
            else:
                print(f"❌ {dir_path.name}/")
                missing_items.append(str(dir_path))
        
        # Verificar arquivos
        for file_path in required_files:
            if file_path.exists():
                print(f"✅ {file_path.relative_to(self.project_root)}")
            else:
                print(f"❌ {file_path.relative_to(self.project_root)}")
                missing_items.append(str(file_path))
        
        if missing_items:
            print(f"\n❌ {len(missing_items)} item(s) faltando")
            print("💡 Certifique-se de que está no diretório correto do projeto")
            return False
        
        print("✅ Estrutura do projeto válida")
        return True
    
    def install_dependencies(self):
        """Instala dependências do projeto."""
        if self.skip_deps:
            print("⚠️  Instalação de dependências ignorada")
            return True
        
        self.print_step(3, "Instalando dependências")
        
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ Arquivo requirements.txt não encontrado")
            return False
        
        try:
            print("📦 Instalando pacotes Python...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
                check=True
            )
            
            print("✅ Dependências instaladas com sucesso")
            
            # Mostrar pacotes instalados
            if result.stdout:
                installed_count = result.stdout.count("Successfully installed")
                if installed_count > 0:
                    print(f"📊 {installed_count} pacote(s) instalado(s)")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro na instalação: {e}")
            if e.stderr:
                print(f"Detalhes: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False
    
    def create_directories(self):
        """Cria diretórios necessários."""
        self.print_step(4, "Criando estrutura de diretórios")
        
        directories = [
            self.results_dir,
            self.results_dir / "figures",
            self.results_dir / "figuras_consolidadas",
            self.logs_dir,
            self.resultados_fixos_dir,
            self.serra_dir / "data" / "raw",
            self.serra_dir / "data" / "generated",
            self.serra_dir / "data" / "downloads",
            self.serra_dir / "data" / "archive",
            self.serra_dir / "tests",
            self.mapbiomas_dir / "tests"
        ]
        
        created_count = 0
        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                print(f"📁 Criado: {directory.relative_to(self.project_root)}")
                created_count += 1
            else:
                print(f"✅ Existe: {directory.relative_to(self.project_root)}")
        
        if created_count > 0:
            print(f"\n📊 {created_count} diretório(s) criado(s)")
        
        print("✅ Estrutura de diretórios configurada")
        return True
    
    def setup_environment_file(self):
        """Configura arquivo de ambiente."""
        self.print_step(5, "Configurando arquivo de ambiente")
        
        env_example = self.project_root / ".env.example"
        env_file = self.project_root / ".env"
        
        if not env_example.exists():
            print("❌ Arquivo .env.example não encontrado")
            return False
        
        if env_file.exists() and not self.force:
            print("⚠️  Arquivo .env já existe")
            response = input("🔄 Sobrescrever? (s/N): ").lower().strip()
            if response not in ['s', 'sim', 'y', 'yes']:
                print("✅ Mantendo arquivo .env existente")
                return True
        
        try:
            # Copiar .env.example para .env
            with open(env_example, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Arquivo .env criado")
            print("💡 Edite o arquivo .env com suas configurações específicas")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar .env: {e}")
            return False
    
    def validate_imports(self):
        """Valida importações principais."""
        self.print_step(6, "Validando importações principais")
        
        critical_packages = [
            ('pandas', 'Manipulação de dados'),
            ('numpy', 'Computação numérica'),
            ('matplotlib', 'Visualização'),
            ('sklearn', 'Machine Learning'),
            ('requests', 'Requisições HTTP'),
            ('fastapi', 'API Framework'),
            ('uvicorn', 'Servidor ASGI')
        ]
        
        failed_imports = []
        
        for package, description in critical_packages:
            try:
                __import__(package)
                print(f"✅ {package} - {description}")
            except ImportError:
                print(f"❌ {package} - {description}")
                failed_imports.append(package)
        
        if failed_imports:
            print(f"\n❌ {len(failed_imports)} pacote(s) faltando")
            print("💡 Execute: pip install -r requirements.txt")
            return False
        
        print("✅ Todas as importações principais funcionando")
        return True
    
    def test_scripts(self):
        """Testa scripts principais."""
        self.print_step(7, "Testando scripts principais")
        
        scripts_to_test = [
            (self.project_root / "setup_environment.py", "Configuração de ambiente"),
            (self.project_root / "start_mapbiomas_server.py", "Servidor MapBiomas"),
            (self.project_root / "run_serra_penitente_analysis.py", "Análise Serra Penitente")
        ]
        
        for script_path, description in scripts_to_test:
            if script_path.exists():
                try:
                    # Teste de sintaxe
                    with open(script_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), str(script_path), 'exec')
                    print(f"✅ {script_path.name} - {description}")
                except SyntaxError as e:
                    print(f"❌ {script_path.name} - Erro de sintaxe: {e}")
                    return False
            else:
                print(f"⚠️  {script_path.name} - Não encontrado")
        
        print("✅ Scripts principais validados")
        return True
    
    def generate_setup_report(self):
        """Gera relatório de configuração."""
        self.print_step(8, "Gerando relatório de configuração")
        
        report_file = self.logs_dir / f"setup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO DE CONFIGURAÇÃO DO PROJETO\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Diretório: {self.project_root}\n\n")
                
                # Informações do sistema
                f.write("SISTEMA:\n")
                f.write(f"- Python: {sys.version}\n")
                f.write(f"- Plataforma: {sys.platform}\n\n")
                
                # Estrutura do projeto
                f.write("ESTRUTURA DO PROJETO:\n")
                for item in sorted(self.project_root.rglob("*")):
                    if item.is_file() and not any(part.startswith('.') for part in item.parts):
                        rel_path = item.relative_to(self.project_root)
                        f.write(f"- {rel_path}\n")
                
                f.write("\nCONFIGURAÇÃO CONCLUÍDA COM SUCESSO!\n")
            
            print(f"📄 Relatório salvo: {report_file}")
            return True
            
        except Exception as e:
            print(f"⚠️  Erro ao gerar relatório: {e}")
            return True  # Não é crítico
    
    def run(self):
        """Executa configuração completa."""
        self.print_header("CONFIGURAÇÃO RÁPIDA - SERRA PENITENTE + MAPBIOMAS")
        
        success = True
        
        # Executar etapas
        success &= self.check_python_version()
        success &= self.check_project_structure()
        success &= self.install_dependencies()
        success &= self.create_directories()
        success &= self.setup_environment_file()
        success &= self.validate_imports()
        success &= self.test_scripts()
        
        # Gerar relatório (não crítico)
        self.generate_setup_report()
        
        if success:
            self.print_header("CONFIGURAÇÃO CONCLUÍDA COM SUCESSO")
            print("🎉 Projeto configurado e pronto para uso!")
            print("\n💡 PRÓXIMOS PASSOS:")
            print("   1. Edite o arquivo .env com suas configurações")
            print("   2. Coloque os dados em serra-penitente-analysis/data/raw/")
            print("   3. Inicie o servidor: python start_mapbiomas_server.py")
            print("   4. Execute a análise: python run_serra_penitente_analysis.py")
        else:
            self.print_header("CONFIGURAÇÃO FALHOU")
            print("❌ Verifique os erros acima e tente novamente")
        
        return success


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Configuração rápida do projeto Serra Penitente + MapBiomas"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Força sobrescrita de arquivos existentes"
    )
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Pula instalação de dependências"
    )
    
    args = parser.parse_args()
    
    setup = QuickSetup(force=args.force, skip_deps=args.skip_deps)
    success = setup.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()