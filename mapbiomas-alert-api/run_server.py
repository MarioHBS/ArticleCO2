import os
import subprocess

if __name__ == "__main__":
    # Ensure the PYTHONPATH includes the src folder
    pythonpath = os.environ.get("PYTHONPATH", "")
    if "src" not in pythonpath:
        os.environ["PYTHONPATH"] = f"src{os.pathsep}" + pythonpath

    # Run the uvicorn command
    subprocess.run([
        "uvicorn", "mapbiomas_api_server:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
    ])
