import subprocess
import webbrowser
import time

# Ejecutar app.py (en un proceso aparte)
process = subprocess.Popen(["python", "run_env.py"])

# Esperar un poco para que arranque el servidor
time.sleep(3)

# Abrir navegador
webbrowser.open("http://127.0.0.1:8000/static/index.html")

# Opcional: esperar a que el servidor termine (Ctrl+C en consola)
process.wait()
