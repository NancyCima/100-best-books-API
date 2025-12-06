Nota: Se recomienda instalar los paquetes en un entorno virtual.

Antes de ejecutar la API se deben ejecutar el siguiente comando:
> pip install -r requirements.txt

Ejecución:
1 - Ejecutar el comando:

uvicorn main:app --reload


Propósito del `main.py` raíz
--------------------------------
El proyecto contiene también un archivo `main.py` en la raíz del repositorio que sirve como
script de prueba y como conjunto de utilidades para manipular el archivo de datos 
(`copybooks.json`) desde la consola. Ese `main.py` raíz implementa funciones similares a 
las que están en `servidor/libros.py` (cargar/guardar/filtrar/actualizar/eliminar), 
por lo que su funcionalidad está duplicada.

Recomendaciones:
- Para ejecutar la API use `uvicorn` desde la carpeta `servidor` (como se indica arriba). 
El servidor FastAPI importa y usa `servidor/libros.py` para la lógica de los libros.
- Use `servidor/libros.py` como fuente de verdad de la lógica compartida. 
El `main.py` raíz es opcional y sólo útil para pruebas locales o desarrollo rápido; 
puede refactorizarse para importar `servidor/libros.py` o eliminarse si no lo necesita.
