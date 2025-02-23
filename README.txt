=== Clínica Dental - Manual de Uso ===

Este programa gestiona una clínica dental, permitiendo registrar pacientes, visitas, pagos, recetas y citas.

Requisitos:
- Python 3.8 o superior
- ReportLab (instalar con: pip install reportlab)

Instrucciones:
1. Ejecuta clinica_dental.py con Python (python clinica_dental.py).
2. Usa el menú superior para acceder a cada módulo:
   - Pacientes: Registra nuevos pacientes con DNI/NIE único.
   - Visitas: Registra visitas y revisa el historial.
   - Pagos: Registra pagos asociados a visitas y consulta el historial.
   - Recetas: Crea recetas y genera PDFs automáticamente.
   - Citas: Agenda citas y revisa el historial.
3. Guarda los datos en cada formulario con el botón "Guardar".
4. Los PDFs de recetas se guardan en la carpeta "recetas".

Notas:
- Los identificadores deben ser DNI (8 números + letra) o NIE (X/Y/Z + 7 números + letra).
- Usa un visor de SQLite para inspeccionar clinica_dental.db si es necesario.
Paso 4: Empaquetado opcional




Si quieres convertir el programa en un ejecutable para usarlo sin Python instalado:
Instala PyInstaller:
En la terminal, ejecuta: pip install pyinstaller.
Genera el ejecutable:
Navega a la carpeta clinica_dental en la terminal (cd d:\clinica_dental_2025).
Ejecuta: pyinstaller --onefile clinica_dental.py.
Esto creará una carpeta dist con un archivo clinica_dental.exe.
Prueba el ejecutable:
Ve a dist y haz doble clic en clinica_dental.exe para ejecutarlo.
Tarea para ti: Si quieres un ejecutable, sigue estos pasos y dime si funcionó o si hubo errores. Si no lo necesitas, solo di "No quiero ejecutable".
