#!/usr/bin/env python3
"""
Script de linting usando Ruff para o projeto Serra Penitente.

Este script executa verificações de qualidade de código usando Ruff,
substituindo o Flake8 anteriormente usado no projeto.

Uso:
    python lint.py          # Verificar código
    python lint.py --fix    # Corrigir problemas automaticamente
    python lint.py --format # Formatar código
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Executa um comando e retorna o código de saída."""
    print(f"\n{description}...")
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False, capture_output=False)
    return result.returncode


def main():
    """Função principal do script de linting."""
    # Diretório do projeto
    project_dir = Path(__file__).parent
    src_dir = project_dir / "src"

    if not src_dir.exists():
        print(f"Erro: Diretório {src_dir} não encontrado!")
        sys.exit(1)

    # Verificar argumentos
    fix_mode = "--fix" in sys.argv
    format_mode = "--format" in sys.argv

    exit_code = 0

    if format_mode:
        # Formatar código com Ruff
        cmd = ["ruff", "format", str(src_dir)]
        exit_code = run_command(cmd, "Formatando código com Ruff")
    elif fix_mode:
        # Verificar e corrigir com Ruff
        cmd = ["ruff", "check", str(src_dir), "--fix"]
        exit_code = run_command(cmd, "Verificando e corrigindo código com Ruff")
    else:
        # Apenas verificar com Ruff
        cmd = ["ruff", "check", str(src_dir)]
        exit_code = run_command(cmd, "Verificando código com Ruff")

    if exit_code == 0:
        print("\n✅ Verificação de linting concluída com sucesso!")
    else:
        print("\n❌ Problemas encontrados durante a verificação.")
        if not fix_mode:
            print("Execute 'python lint.py --fix' para corrigir automaticamente.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
