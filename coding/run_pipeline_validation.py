import subprocess
import os
import sys
import subprocess
from variaveis import INPUT_PATHS, OUTPUT_PATHS

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
    ("00_extrair_pib_municipal.py", [OUTPUT_PATHS.pib_ibge_csv]),
    ("01_extrair_gee_municipal_excel.py", [OUTPUT_PATHS.mapbiomas_long_csv]),
    ("02_extrair_alertas_desmatamento.py", [OUTPUT_PATHS.alertas_csv]),
    ("03_extrair_uso_terra_timeseries.py", [INPUT_PATHS.uso_timeseries]),
    ("04_consolidar_modelar_carbono.py", [
        OUTPUT_PATHS.carbono_consolidado_csv,
        OUTPUT_PATHS.model_results_csv
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

for script, outputs in stages:
    print(f"\n=== Running {script} ===")
    result = subprocess.run([sys.executable, script],
                            capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        safe_print(f"[ERROR] {script} failed(exit code {result.returncode}")
        # stderr suppressed to avoid encoding issues
        all_ok = False
        continue

    if outputs:
        print(f"Checking outputs for {script}:")
        if not check_files(outputs):
            all_ok = False
    else:
        # For stage 05, check numbered figures
        fig_dir = os.path.dirname(OUTPUT_PATHS.evolucao_pib_png)
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
