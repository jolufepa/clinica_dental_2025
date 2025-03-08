# Documentación de la Aplicación de Gestión Dental

## Descripción
Esta es una aplicación de gestión para una clínica dental, desarrollada en Python utilizando Tkinter para la interfaz gráfica, SQLite para la base de datos, y organizada en módulos (vistas, controladores, servicios, y modelos). Está diseñada para gestionar pacientes, citas, visitas, y pagos, con roles como "admin" para acceder a funcionalidades avanzadas. La aplicación sigue un enfoque modular, con una vista principal (`pacientes_view.py`) que centraliza la gestión de pacientes y abre ventanas secundarias para tareas específicas (crear, editar, gestionar citas, visitas, y pagos).

## Funcionalidades Actuales (Implementadas al 26/02/2025)

### Gestión de Pacientes
- **Búsqueda:** Busca pacientes por ID, nombre o teléfono, mostrando sus datos en un notebook con pestañas (Información Personal, Historial Médico, Citas, Visitas, Pagos y Deudas).
- **Creación:** Permite crear nuevos pacientes con validaciones para DNI/NIE españoles, formato de fecha (DD/MM/AAAA), y campos obligatorios (Identificador, Nombre, Fecha nacimiento, etc.).
- **Edición:** Permite editar datos de pacientes existentes, con el identificador (DNI/NIE) en modo de solo lectura y validaciones similares a la creación.
- **Interfaz Mejorada:** Las ventanas de "Nuevo Paciente" y "Editar Paciente" tienen un diseño optimizado con secciones ("Información Personal" y "Historial Médico"), tamaño fijo (600x700), y todos los campos visibles sin redimensionar manualmente.

### Gestión de Citas, Visitas y Pagos
- Cada pestaña en `pacientes_view.py` muestra datos básicos y un botón "Gestionar" que abre vistas separadas:
  - **Citas:** Lista y gestiona citas de un paciente específico, mostrando solo las citas del paciente seleccionado al abrir desde `pacientes_view.py`, con botones "Nueva Cita" y "Enviar Recordatorio". Incluye validaciones para fecha y hora (YYYY-MM-DD, HH:MM).
  - **Visitas:** Lista y gestiona visitas de un paciente específico, mostrando solo las visitas del paciente seleccionado al abrir desde `pacientes_view.py`, con botón "Nueva Visita". Incluye validaciones para fecha (YYYY-MM-DD).
  - **Pagos:** Lista y gestiona pagos de un paciente específico, mostrando solo los pagos del paciente seleccionado al abrir desde `pacientes_view.py`, con botón "Nuevo Pago". Incluye validaciones para montos numéricos y fecha (YYYY-MM-DD).
- Todas las vistas secundarias están sincronizadas con `MainController` para actualizar listas automáticamente tras crear, editar o gestionar registros.

### Base de Datos
- Utiliza SQLite con tablas para pacientes, citas, visitas, y pagos, conectadas por claves foráneas (`identificador` como clave primaria en pacientes y foránea en citas, visitas, pagos).
- Incluye métodos CRUD (Crear, Leer, Actualizar, Eliminar) en `services/database_service.py`, con manejo de errores y restricciones de integridad (FOREIGN KEY).

### Estilo y Usabilidad
- Usa estilos globales con `configurar_estilos` desde `views/styles.py` para una apariencia consistente.
- Incluye tooltips en algunas vistas para mejorar la experiencia del usuario.
- Las ventanas son modales, con centrado automático y diseño responsive en las vistas principales.

## Requisitos de Instalación
- Python 3.8 o superior
- Bibliotecas requeridas:
  - `tkinter` (incluido en la instalación estándar de Python)
  - `sqlite3` (incluido en la instalación estándar de Python)
  - reportlab
  - tkcalendar

## Instrucciones de Instalación
1. Clona o descarga el repositorio del proyecto.
2. Asegúrate de tener Python instalado en tu sistema.
3. No se requiere instalación adicional de bibliotecas, ya que utiliza módulos estándar de Python.
4. Ejecuta el archivo principal `main.py` desde la terminal o un entorno IDE:
5. Inicia sesión con rol "admin" (credenciales definidas en `services/database_service.py` o en el código).

## Uso
- **Inicio:** La aplicación abre un menú principal (`MenuPrincipalView`) donde puedes seleccionar "Gestión de Pacientes" para acceder a `pacientes_view.py`.
- **Gestión de Pacientes:** Busca pacientes, crea nuevos, edita existentes, o elimina (pendiente de completar eliminación por restricciones de clave foránea).
- **Gestión de Citas/Visitas/Pagos:** Desde las pestañas en `pacientes_view.py`, usa "Gestionar" para abrir vistas detalladas y crear o gestionar registros específicos del paciente seleccionado.

## Progreso Actual y Tareas Pendientes
- **Progreso (26/02/2025):**
  - Implementadas y optimizadas las funcionalidades de búsqueda, creación, edición de pacientes, y gestión de citas, visitas, y pagos desde `pacientes_view.py`.
  - Ajustadas las vistas (`citas_view.py`, `visitas_view.py`, `pagos_view.py`) para mostrar solo datos del paciente seleccionado cuando se abre desde `pacientes_view.py`, eliminando `Treeview` de pacientes y buscadores redundantes.
  - Mejorada la apariencia de `NuevoPacienteView` y `EditarPacienteView` con un diseño más claro y compacto.

- **Tareas Pendientes:**
  1. **Eliminación de Pacientes:** Resolver la restricción de clave foránea (`FOREIGN KEY constraint failed`) al eliminar pacientes en `pacientes_view.py`. Esto implica modificar `_eliminar_paciente` para eliminar primero las citas, visitas, y pagos relacionados antes de eliminar el paciente.
  2. **Funcionalidades Futuras:** Añadir un botón en `MenuPrincipalView` para un resumen de pacientes o pagos del mes, y posibles mejoras como validaciones adicionales (disponibilidad de odontólogos, límites de montos, etc.) o edición directa en los `Treeview` de `pacientes_view.py`.
  3. **Optimización y Limpieza:** Revisar y eliminar métodos o archivos redundantes tras completar las integraciones, mejorar performance y usabilidad (ajustes de estilos, mensajes de error, etc.).

## Notas para Desarrolladores
- El código está organizado en directorios: `views/` (interfaz), `controllers/` (lógica), `services/` (base de datos), y `models/` (clases de datos).
- Usa depuración (`print` statements) en la consola para rastrear problemas; considera reemplazarlos por logging para producción.
- La base de datos (`clinica_dental.db`) se crea automáticamente al iniciar la aplicación si no existe, con tablas predefinidas en `services/database_service.py`.
- Los estilos se aplican globalmente con `configurar_estilos`; modifica `views/styles.py` para personalizar colores, fuentes, etc.
**`_crear_odontograma`:** 
  - Usa un `Canvas` de 600x500 píxeles para dibujar una cuadrícula de 32 dientes (4 filas x 8 columnas).
  - Cada diente es un círculo (`create_oval`) con un número y un color inicial ("lightgray").
  - Botones permiten cambiar el estado (sano, caries, extracción, tratamiento) con colores asociados.
  - Un campo de notas y un botón de guardar completan la interfaz.

- **Interactividad:**
  - Al hacer clic en un diente, cambia su estado y se actualiza el color.
  - Las notas se asocian al diente seleccionado (por simplicidad, al diente 1 por ahora; se puede expandir).

- **Carga y Guardado:**
  - `_cargar_odontograma` recupera los datos del paciente desde la base de datos.
  - `_guardar_odontograma` guarda los cambios usando `DatabaseService`.
## Contacto
Para preguntas o colaboraciones, contacta al desarrollador principal (Jose Luis Fernandez P. email. jolufepa@gmail.com).

