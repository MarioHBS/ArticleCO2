#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Iniciar o Servidor MapBiomas API

Este script inicia o servidor local da API MapBiomas em um terminal separado
e verifica se o servidor está funcionando corretamente.

Funcionalidades:
- Inicia o servidor em segundo plano
- Verifica a saúde do servidor
- Monitora logs de erro
- Permite parar o servidor

Uso:
    python start_mapbiomas_server.py [--stop]
"""

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import requests


class MapBiomasServerManager:
    """Gerenciador do servidor MapBiomas API."""

    def __init__(self):
        self.server_process = None
        self.server_url = "http://localhost:8000"
        self.health_endpoint = f"{self.server_url}/health"
        self.mapbiomas_dir = Path("mapbiomas-alert-api")
        self.server_script = self.mapbiomas_dir / "run_server.py"
        self.pid_file = Path("mapbiomas_server.pid")

    def print_header(self, title):
        """Imprime cabeçalho formatado."""
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)

    def print_step(self, step_num, description):
        """Imprime passo da operação."""
        print(f"\n[{step_num}] {description}")
        print("-" * 40)

    def validate_environment(self):
        """Valida se o ambiente está configurado corretamente."""
        self.print_step(1, "Validando ambiente")

        if not self.mapbiomas_dir.exists():
            print(f"❌ Diretório {self.mapbiomas_dir} não encontrado")
            return False

        if not self.server_script.exists():
            print(f"❌ Script {self.server_script} não encontrado")
            return False

        # Verificar se as dependências estão instaladas
        try:
            __import__('fastapi')
            __import__('uvicorn')
            print("✅ Dependências FastAPI/Uvicorn encontradas")
        except ImportError:
            print("❌ Dependências FastAPI/Uvicorn não encontradas")
            print("💡 Execute: pip install -r requirements.txt")
            return False

        print("✅ Ambiente validado")
        return True

    def check_server_running(self):
        """Verifica se o servidor já está rodando."""
        try:
            response = requests.get(self.health_endpoint, timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        return False

    def start_server(self):
        """Inicia o servidor MapBiomas API."""
        self.print_step(2, "Iniciando servidor MapBiomas API")

        # Verificar se já está rodando
        if self.check_server_running():
            print("⚠️  Servidor já está rodando")
            print(f"🌐 Acesse: {self.server_url}")
            return True

        try:
            # Iniciar servidor em segundo plano
            print("🚀 Iniciando servidor...")

            # Usar o script run_server.py do projeto MapBiomas
            self.server_process = subprocess.Popen(
                [sys.executable, str(self.server_script)],
                cwd=self.mapbiomas_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Salvar PID para poder parar depois
            with open(self.pid_file, 'w') as f:
                f.write(str(self.server_process.pid))

            print(f"📝 PID do servidor: {self.server_process.pid}")
            print("⏳ Aguardando servidor inicializar...")

            return True

        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
            return False

    def wait_for_server(self, max_attempts=30, delay=1):
        """Aguarda o servidor ficar disponível."""
        self.print_step(3, "Verificando saúde do servidor")

        for attempt in range(max_attempts):
            try:
                response = requests.get(self.health_endpoint, timeout=2)
                if response.status_code == 200:
                    health_data = response.json()
                    print("✅ Servidor está funcionando!")
                    print(f"📊 Status: {health_data.get('status', 'unknown')}")
                    print(f"🌐 URL: {self.server_url}")
                    print(f"📖 Documentação: {self.server_url}/docs")
                    return True
            except requests.exceptions.RequestException:
                pass

            print(f"⏳ Tentativa {attempt + 1}/{max_attempts}...")
            time.sleep(delay)

        print("❌ Servidor não respondeu no tempo esperado")
        return False

    def show_server_info(self):
        """Mostra informações do servidor."""
        self.print_step(4, "Informações do servidor")

        try:
            # Verificar endpoints disponíveis
            response = requests.get(f"{self.server_url}/docs", timeout=5)
            if response.status_code == 200:
                print("📚 Endpoints disponíveis:")
                print(f"   - Health Check: {self.server_url}/health")
                print(f"   - Autenticação: {self.server_url}/token")
                print(f"   - Alertas: {self.server_url}/alerts")
                print(f"   - Documentação: {self.server_url}/docs")

        except requests.exceptions.RequestException:
            print("⚠️  Não foi possível obter informações detalhadas")

        print("\n💡 DICAS DE USO:")
        print("   - Configure suas credenciais no arquivo .env")
        print("   - Use a documentação interativa em /docs")
        print("   - Para parar o servidor: python start_mapbiomas_server.py --stop")

    def stop_server(self):
        """Para o servidor MapBiomas API."""
        self.print_header("PARANDO SERVIDOR MAPBIOMAS API")

        # Tentar parar usando PID salvo
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())

                print(f"🛑 Parando servidor (PID: {pid})...")

                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
                else:
                    os.kill(pid, signal.SIGTERM)

                self.pid_file.unlink()  # Remove arquivo PID
                print("✅ Servidor parado com sucesso")
                return True

            except (ValueError, ProcessLookupError, subprocess.CalledProcessError) as e:
                print(f"⚠️  Erro ao parar servidor: {e}")

        # Verificar se ainda está rodando
        if self.check_server_running():
            print("⚠️  Servidor ainda está rodando")
            print("💡 Tente parar manualmente ou reiniciar o terminal")
            return False
        else:
            print("✅ Servidor não está rodando")
            return True

    def run(self, stop=False):
        """Executa o gerenciador do servidor."""
        if stop:
            return self.stop_server()

        self.print_header("INICIANDO SERVIDOR MAPBIOMAS API")

        # Validar ambiente
        if not self.validate_environment():
            return False

        # Iniciar servidor
        if not self.start_server():
            return False

        # Aguardar servidor ficar disponível
        if not self.wait_for_server():
            return False

        # Mostrar informações
        self.show_server_info()

        print("\n🎉 Servidor MapBiomas API iniciado com sucesso!")
        print("\n⚠️  IMPORTANTE: Mantenha este terminal aberto")
        print("   O servidor está rodando em segundo plano")

        return True


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Gerenciador do Servidor MapBiomas API"
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Para o servidor MapBiomas API"
    )

    args = parser.parse_args()

    # Verificar se estamos no diretório correto
    if not Path("mapbiomas-alert-api").exists():
        print("❌ Execute este script na raiz do projeto")
        print("   Certifique-se de que a pasta mapbiomas-alert-api existe")
        sys.exit(1)

    manager = MapBiomasServerManager()
    success = manager.run(stop=args.stop)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
