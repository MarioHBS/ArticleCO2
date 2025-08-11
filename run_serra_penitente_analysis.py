#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Executar Análise Serra Penitente

Este script executa o pipeline completo de análise do projeto Serra Penitente,
verificando previamente se o servidor MapBiomas API está disponível.

Funcionalidades:
- Verifica disponibilidade do servidor MapBiomas API
- Executa pipeline de validação completo
- Monitora progresso e erros
- Gera relatório de execução

Uso:
    python run_serra_penitente_analysis.py [--skip-server-check]
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests


class SerraAnalysisRunner:
    """Executor da análise Serra Penitente."""

    def __init__(self, skip_server_check=False):
        self.skip_server_check = skip_server_check
        self.server_url = "http://localhost:8000"
        self.health_endpoint = f"{self.server_url}/health"
        self.serra_dir = Path("serra-penitente-analysis")
        self.pipeline_script = self.serra_dir / "run_pipeline_validation.py"
        self.results_dir = Path("results")
        self.logs_dir = Path("logs")

    def print_header(self, title):
        """Imprime cabeçalho formatado."""
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)

    def print_step(self, step_num, description):
        """Imprime passo da operação."""
        print(f"\n[{step_num}] {description}")
        print("-" * 40)

    def check_environment(self):
        """Verifica se o ambiente está configurado."""
        self.print_step(1, "Verificando ambiente")

        # Verificar se estamos no diretório correto
        if not self.serra_dir.exists():
            print(f"❌ Diretório {self.serra_dir} não encontrado")
            print("💡 Execute este script na raiz do projeto")
            return False

        # Verificar script principal
        if not self.pipeline_script.exists():
            print(f"❌ Script {self.pipeline_script} não encontrado")
            return False

        # Verificar dependências críticas
        try:
            __import__('pandas')
            __import__('numpy')
            __import__('matplotlib')
            __import__('sklearn')
            print("✅ Dependências principais encontradas")
        except ImportError as e:
            print(f"❌ Dependência faltando: {e}")
            print("💡 Execute: pip install -r requirements.txt")
            return False

        # Criar diretórios se necessário
        self.results_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        print("✅ Ambiente validado")
        return True

    def check_mapbiomas_server(self):
        """Verifica se o servidor MapBiomas está disponível."""
        if self.skip_server_check:
            print("⚠️  Verificação do servidor MapBiomas ignorada")
            return True

        self.print_step(2, "Verificando servidor MapBiomas API")

        try:
            response = requests.get(self.health_endpoint, timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Servidor MapBiomas disponível")
                print(f"📊 Status: {health_data.get('status', 'unknown')}")
                print(f"🌐 URL: {self.server_url}")
                return True
            else:
                print(f"❌ Servidor retornou status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Servidor MapBiomas não disponível: {e}")
            print("\n💡 SOLUÇÕES:")
            print("   1. Inicie o servidor: python start_mapbiomas_server.py")
            print("   2. Ou ignore a verificação: --skip-server-check")
            return False

    def check_data_files(self):
        """Verifica se os arquivos de dados estão disponíveis."""
        self.print_step(3, "Verificando arquivos de dados")

        data_dir = self.serra_dir / "data" / "raw"
        required_files = [
            "pib_municipios_ibge_2002_2009.xls",
            "pib_municipios_ibge_2010_2021.xlsx",
            "cobertura_solo_mapbiomas_municipios_brasil.xlsx",
            "precos_carbono_eu_ets.xlsx",
            "idhm_municipios_serra_penitente.xlsx"
        ]

        missing_files = []
        for file_name in required_files:
            file_path = data_dir / file_name
            if file_path.exists():
                print(f"✅ {file_name}")
            else:
                print(f"❌ {file_name}")
                missing_files.append(file_name)

        if missing_files:
            print(f"\n⚠️  {len(missing_files)} arquivo(s) faltando")
            print("💡 Coloque os arquivos em serra-penitente-analysis/data/raw/")
            return False

        print("✅ Todos os arquivos de dados encontrados")
        return True

    def clean_previous_results(self):
        """Limpa resultados anteriores se solicitado."""
        self.print_step(4, "Preparando ambiente de execução")

        # Verificar se há resultados anteriores
        generated_dir = self.serra_dir / "data" / "generated"

        if generated_dir.exists() and any(generated_dir.iterdir()):
            print("📁 Dados gerados anteriores encontrados")
            response = input("🗑️  Limpar dados anteriores? (s/N): ").lower().strip()

            if response in ['s', 'sim', 'y', 'yes']:
                import shutil
                if generated_dir.exists():
                    shutil.rmtree(generated_dir)
                    generated_dir.mkdir(exist_ok=True)
                    print("✅ Dados anteriores removidos")

                # Limpar também results/
                if self.results_dir.exists():
                    for item in self.results_dir.iterdir():
                        if item.is_file() and item.suffix in ['.csv', '.txt']:
                            item.unlink()
                        elif item.is_dir() and item.name in ['figures', 'figuras_consolidadas']:
                            shutil.rmtree(item)
                    print("✅ Resultados anteriores removidos")
            else:
                print("⚠️  Mantendo dados anteriores (pode causar conflitos)")

        # Criar diretórios necessários
        (self.results_dir / "figures").mkdir(parents=True, exist_ok=True)
        (self.results_dir / "figuras_consolidadas").mkdir(parents=True, exist_ok=True)
        generated_dir.mkdir(parents=True, exist_ok=True)

        print("✅ Ambiente preparado")
        return True

    def run_analysis(self):
        """Executa o pipeline de análise."""
        self.print_step(5, "Executando análise Serra Penitente")

        # Initialize analysis
        start_time, log_file = self._initialize_analysis()

        try:
            # Run the pipeline and monitor progress
            success = self._run_pipeline_with_monitoring(log_file, start_time)

            # Generate completion summary
            self._generate_completion_summary(start_time, success)

            return success

        except Exception as e:
            print(f"❌ Erro durante execução: {e}")
            return False

    def _initialize_analysis(self):
        """Initialize analysis and create log file."""
        start_time = datetime.now()
        log_file = self.logs_dir / f"serra_analysis_{start_time.strftime('%Y%m%d_%H%M%S')}.log"

        print("🚀 Iniciando pipeline de análise...")
        print(f"📝 Log: {log_file}")
        print(f"⏰ Início: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        return start_time, log_file

    def _run_pipeline_with_monitoring(self, log_file, start_time):
        """Run the analysis pipeline with progress monitoring."""

        # Initialize pipeline process
        process = self._create_pipeline_process()

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Análise Serra Penitente - {start_time}\n")
            f.write("=" * 50 + "\n\n")

            print("\n📊 PROGRESSO EM TEMPO REAL:")
            print("-" * 50)

            # Monitor and log progress
            success = self._monitor_pipeline_progress(process, f)

        return success

    def _create_pipeline_process(self):
        """Create and return the pipeline subprocess."""
        return subprocess.Popen(
            [sys.executable, "run_pipeline_validation.py"],
            cwd=self.serra_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='cp1252',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )

    def _monitor_pipeline_progress(self, process, log_file):
        """Monitor pipeline progress and return success status."""

        step_count = 0

        for line in process.stdout:
            line_clean = line.rstrip()
            if not line_clean:
                continue

            step_count = self._process_pipeline_output(line_clean, step_count)

            # Write to log
            log_file.write(line)
            log_file.flush()

        # Wait for completion
        return_code = process.wait()

        # Log completion info
        end_time = datetime.now()
        log_file.write(f"\n\nConcluído em: {end_time}\n")
        log_file.write(f"Código de saída: {return_code}\n")

        # Display final status
        print(f"\n📊 Etapas processadas: {step_count}")

        if return_code == 0:
            print("🎉 Análise concluída com sucesso!")
            return True
        else:
            print(f"❌ Análise falhou (código: {return_code})")
            return False

    def _process_pipeline_output(self, line_clean, step_count):
        """Process a single line of pipeline output and return updated step count."""

        # Detect new step
        if re.search(r'Etapa \d+', line_clean):
            step_count += 1
            print(f"\n🔄 {line_clean}")
            print("   " + "-" * 40)
            return step_count

        # Detect script execution
        elif re.search(r'Executando.*\.py', line_clean):
            script_name = re.search(r'(\d+_.*\.py)', line_clean)
            if script_name:
                print(f"   ⚙️  Executando: {script_name.group(1)}")
            else:
                print(f"   ⚙️  {line_clean}")

        # Detect file operations
        elif re.search(r'Salvando.*\.(csv|png|pdf)', line_clean):
            self._display_file_operation(line_clean)

        # Detect figure generation
        elif re.search(r'Figura\d+', line_clean):
            print(f"   📊 {line_clean}")

        # Detect status messages
        elif any(pattern in line_clean for pattern in ['✅', '❌', 'SUCESSO', 'ERRO', 'WARNING', 'FALHA']):
            self._display_status_message(line_clean)

        # Other important lines
        elif any(keyword in line_clean.lower() for keyword in ['processando', 'carregando', 'gerando', 'validando']):
            print(f"   ℹ️  {line_clean}")

        return step_count

    def _display_file_operation(self, line_clean):
        """Display file operation message with appropriate icon."""

        file_match = re.search(r'Salvando (.+)', line_clean)
        if file_match:
            file_name = file_match.group(1)
            if '.csv' in file_name:
                print(f"   💾 Dados salvos: {file_name}")
            elif '.png' in file_name:
                print(f"   🖼️  Figura salva: {file_name}")
            elif '.pdf' in file_name:
                print(f"   📄 PDF salvo: {file_name}")

    def _display_status_message(self, line_clean):
        """Display status message with appropriate icon."""

        if re.search(r'✅.*concluída', line_clean):
            print(f"   ✅ {line_clean}")
        elif re.search(r'❌.*falhou', line_clean):
            print(f"   ❌ {line_clean}")
        elif 'SUCESSO' in line_clean.upper():
            print(f"   🎉 {line_clean}")
        elif any(keyword in line_clean.upper() for keyword in ['ERRO', 'FALHA']):
            print(f"   🚨 {line_clean}")
        elif 'WARNING' in line_clean.upper():
            print(f"   ⚠️  {line_clean}")

    def _generate_completion_summary(self, start_time, success):
        """Generate and display completion summary with execution metrics."""
        end_time = datetime.now()
        duration = end_time - start_time

        # Display timing info
        self._display_timing_info(end_time, duration)

        # Display status
        self._display_completion_status(success)

    def _display_timing_info(self, end_time, duration):
        """Display execution timing information."""
        print("\n" + "=" * 50)
        print(f"⏰ Fim: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⌛ Duração: {duration}")

    def _display_completion_status(self, success):
        """Display final execution status with appropriate message."""
        if success:
            self._display_success_message()
        else:
            self._display_failure_message()

    def _display_success_message(self):
        """Display success completion message."""
        print("🎉 Análise concluída com sucesso!")

    def _display_failure_message(self):
        """Display failure completion message."""
        print("❌ Análise falhou")
        print("📝 Verifique o log em logs/")

    def generate_summary(self):
        """Gera resumo dos resultados."""
        self.print_step(6, "Gerando resumo dos resultados")

        # Verificar arquivos gerados
        csv_files = list(self.results_dir.glob("*.csv"))
        png_files = list((self.results_dir / "figures").glob("*.png")) if (self.results_dir / "figures").exists() else []
        pdf_files = list((self.results_dir / "figuras_consolidadas").glob("*.pdf")) if (self.results_dir / "figuras_consolidadas").exists() else []
        txt_files = list(self.results_dir.glob("*.txt"))

        print("📊 RESULTADOS GERADOS:")
        print(f"   📈 Arquivos CSV: {len(csv_files)}")
        print(f"   🖼️  Figuras PNG: {len(png_files)}")
        print(f"   📄 Figuras PDF: {len(pdf_files)}")
        print(f"   📝 Relatórios TXT: {len(txt_files)}")

        if csv_files:
            print("\n📈 DADOS GERADOS:")
            for csv_file in sorted(csv_files):
                print(f"   - {csv_file.name}")

        if png_files:
            print("\n🖼️  FIGURAS PNG:")
            for png_file in sorted(png_files):
                print(f"   - {png_file.name}")

        if pdf_files:
            print("\n📄 FIGURAS PDF:")
            for pdf_file in sorted(pdf_files):
                print(f"   - {pdf_file.name}")

        if txt_files:
            print("\n📝 RELATÓRIOS:")
            for txt_file in sorted(txt_files):
                print(f"   - {txt_file.name}")

        print("\n💡 PRÓXIMOS PASSOS:")
        print("   - Verifique os resultados na pasta results/")
        print("   - Consulte os relatórios em resultados_fixos/")
        print("   - Execute testes: pytest serra-penitente-analysis/tests/")

        return True

    def run(self):
        """Executa o runner completo."""
        self.print_header("ANÁLISE SERRA PENITENTE - PIPELINE COMPLETO")

        success = True

        # Executar etapas
        success &= self.check_environment()
        success &= self.check_mapbiomas_server()
        success &= self.check_data_files()
        success &= self.clean_previous_results()

        if success:
            success &= self.run_analysis()
            self.generate_summary()

        if success:
            self.print_header("ANÁLISE CONCLUÍDA COM SUCESSO")
            print("🎉 Pipeline executado com sucesso!")
        else:
            self.print_header("ANÁLISE FALHOU")
            print("❌ Verifique os erros acima e tente novamente")

        return success


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Executor da Análise Serra Penitente"
    )
    parser.add_argument(
        "--skip-server-check",
        action="store_true",
        help="Pula verificação do servidor MapBiomas API"
    )

    args = parser.parse_args()

    # Verificar se estamos no diretório correto
    if not Path("serra-penitente-analysis").exists():
        print("❌ Execute este script na raiz do projeto")
        print("   Certifique-se de que a pasta serra-penitente-analysis existe")
        sys.exit(1)

    runner = SerraAnalysisRunner(skip_server_check=args.skip_server_check)
    success = runner.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
