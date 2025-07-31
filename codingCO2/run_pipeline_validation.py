import subprocess
import os
import sys
import subprocess
# Paths are hardcoded below to avoid import/exec issues.

# Utility to safely print possibly non-ASCII output without encoding errors


def safe_print(s: str):
    try:
        # We may have multiline strings
        sys.stdout.write(s)
    except UnicodeEncodeError:
        # Fallback: replace unencodable chars
        clean = s.encode(sys.stdout.encoding, errors='replace').decode(
            sys.stdout.encoding)
        sys.stdout.write(clean)


# Define each stage script and its expected output files
stages = [
    ("00_extrair_pib_municipal.py", ["data/partial/pib_municipal_serra_penitente_ibge.csv"]),
    ("01_extrair_gee_municipal_excel.py", ["data/partial/mapbiomas_cobertura_municipal_long.csv"]),
    ("02_extrair_alertas_desmatamento.py", ["data/partial/alertas_serra_penitente.csv"]),
    ("04_consolidar_dados_carbono.py", [
        "data/generated/carbono_serra_penitente.csv",
        "results/carbon_price_model_all_results.csv"
    ]),
    ("05_gerar_figuras_carbono.py", None),  # Outputs checked dynamically
]

# Helper to check file existence


def check_files(files):
    status = True
    for f in files:
        if not os.path.exists(f):
            print(f"[MISSING] {f}")
            status = False
        else:
            print(f"[OK]      {f}")
    return status


all_ok = True

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

for script, outputs in stages:
    print(f"\n=== Running {script} ===")
    script_path = os.path.join(project_root, 'codingCO2', script)
    result = subprocess.run([sys.executable, script_path],
                            cwd=project_root,
                            capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(result.stdout)
    if result.returncode != 0:
        safe_print(f"[ERROR] {script} failed(exit code {result.returncode})\n")
        safe_print(result.stderr)
        all_ok = False
        continue

    if outputs:
        print(f"Checking outputs for {script}:")
        if not check_files(outputs):
            all_ok = False
    else:
        # For stage 05, check numbered figures
        fig_dir = "results/figures"
        expected = []
        # Figures 01-05
        for i in range(1, 6):
            expected.append(os.path.join(fig_dir, f"Figura{i:02d}_*.png"))
        # Scatters Figura07_1..9
        for i in range(1, 10):
            expected.append(os.path.join(fig_dir, f"Figura07_{i}_*.png"))
        # Figura08 and Figura09
        expected.append(os.path.join(
            fig_dir, "Figura08_Importancia_Variaveis.png"))
        expected.append(os.path.join(
            fig_dir, "Figura09_Evolucao_Preco_Carbono.png"))
        print(f"Checking figures in {fig_dir}:")
        import glob
        for pattern in expected:
            matches = glob.glob(pattern)
            if matches:
                print(f"[OK]      Pattern {pattern} -> {len(matches)} file(s)")
            else:
                print(f"[MISSING] Pattern {pattern}")
                all_ok = False

print("\nPipeline validation completed.")
if not all_ok:
    print("Some steps failed or outputs are missing.")
    sys.exit(1)
else:
    print("All steps ran successfully and outputs are present.")
