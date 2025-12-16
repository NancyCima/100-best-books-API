"""
SERVIDOR 2 - Almacenamiento de datos
API simple sin autenticación ni rate limiting
Gestiona directamente el archivo JSON
"""
from fastapi import FastAPI, HTTPException
from typing import List
import json

app = FastAPI()

# Ruta al archivo de datos
DATA_FILE = "data/copybooks.json"

# Funciones auxiliares
def cargar_libros():
    """Carga los libros del archivo JSON"""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def guardar_libros(libros):
    """Guarda los libros en el archivo JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(libros, file, indent=2, ensure_ascii=False)

def indice_libro(libros, titulo):
    """Obtiene el índice de un libro por título (case-insensitive)"""
    titulo_lower = titulo.lower().strip()
    for i, libro in enumerate(libros):
        if libro["title"].lower() == titulo_lower:
            return i
    return -1

def filtrar_libros(libros, autor=None, idioma=None, pais=None, anioMin=None, anioMax=None):
    """Filtra libros según criterios (case-insensitive con búsqueda parcial)"""
    # Convertir límites de año
    anioMin = int(anioMin) if anioMin is not None else -9999
    anioMax = int(anioMax) if anioMax is not None else 9999
    
    # Normalizar filtros de texto
    filtro_autor = autor.lower().strip() if autor else None
    filtro_idioma = idioma.lower().strip() if idioma else None
    filtro_pais = pais.lower().strip() if pais else None
    
    filtro = libros
    
    # Filtrar por autor (case-insensitive, búsqueda parcial)
    if filtro_autor:
        filtro = [libro for libro in filtro 
                 if filtro_autor in libro.get("author", "").lower().strip()]
    
    # Filtrar por idioma (case-insensitive, búsqueda parcial)
    if filtro_idioma:
        filtro = [libro for libro in filtro 
                 if filtro_idioma in libro.get("language", "").lower().strip()]
    
    # Filtrar por país (case-insensitive, búsqueda parcial)
    if filtro_pais:
        filtro = [libro for libro in filtro 
                 if filtro_pais in libro.get("country", "").lower().strip()]
    
    # Filtrar por rango de años
    filtro = [libro for libro in filtro 
             if anioMin <= libro.get("year", 0) <= anioMax]
    
    return filtro

# ENDPOINTS

@app.get("/")
def bienvenida():
    """Endpoint raíz - información del servidor"""
    libros = cargar_libros()
    return {
        "servidor": "Servidor 2 - Datos",
        "cantidad_libros": len(libros),
        "estado": "activo"
    }

@app.get("/libros/")
def get_filtrar_libros(
    autor: str = None,
    idioma: str = None,
    pais: str = None,
    anioMin: int = None,
    anioMax: int = None
) -> List[dict]:
    """Obtiene libros filtrados"""
    libros = cargar_libros()
    filtrado = filtrar_libros(libros, autor, idioma, pais, anioMin, anioMax)
    
    if filtrado:
        return filtrado
    else:
        raise HTTPException(
            status_code=404,
            detail="No hay libros para los filtros seleccionados"
        )

@app.get("/libros/{titulo}")
def get_libro(titulo: str) -> dict:
    """Obtiene un libro específico"""
    libros = cargar_libros()
    
    # Normalizar búsqueda: quitar espacios y convertir a minúsculas
    titulo_normalizado = titulo.strip().lower()
    
    # Buscar coincidencia exacta (case-insensitive)
    for libro in libros:
        if libro["title"].strip().lower() == titulo_normalizado:
            return libro
    
    # Si no encuentra exacto, buscar parcial
    libros_coincidentes = []
    for libro in libros:
        if titulo_normalizado in libro["title"].strip().lower():
            libros_coincidentes.append(libro)
    
    if len(libros_coincidentes) == 1:
        return libros_coincidentes[0]
    elif len(libros_coincidentes) > 1:
        # Si hay múltiples coincidencias, devolver el primero
        print(f"⚠️  Múltiples coincidencias para '{titulo}'. Mostrando la primera.")
        return libros_coincidentes[0]
    else:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

@app.post("/libros/")
def agregar_libro(
    titulo: str,
    autor: str,
    idioma: str,
    paginas: int,
    pais: str,
    anio: int,
    imagen: str = None,
    link: str = None
):
    """Agrega un nuevo libro"""

    libros = cargar_libros()
    
    nuevo_libro = {
        "author": autor,
        "country": pais,
        "imageLink": imagen,
        "language": idioma,
        "link": link,
        "pages": int(paginas),
        "title": titulo,
        "year": int(anio)
    }
    
    libros.append(nuevo_libro)
    guardar_libros(libros)
    
    return {"message": "Libro agregado exitosamente", "libro": titulo}

@app.put("/libros/{titulo}")
def actualizar_libro(
    titulo: str,
    tituloAct: str,
    autor: str,
    idioma: str,
    paginas: int,
    pais: str,
    anio: int,
    imagen: str = None,
    link: str = None
):
    """Actualiza un libro existente"""
    libros = cargar_libros()
    indice = indice_libro(libros, titulo)
    
    if indice == -1:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    libro_actualizado = {
        "author": autor,
        "country": pais,
        "imageLink": imagen,
        "language": idioma,
        "link": link,
        "pages": int(paginas),
        "title": tituloAct,
        "year": int(anio)
    }
    
    libros[indice] = libro_actualizado
    guardar_libros(libros)
    
    return {"message": "Libro actualizado exitosamente", "libro": tituloAct}

@app.delete("/libros/{titulo}")
def eliminar_libro(titulo: str):
    """Elimina un libro"""
    libros = cargar_libros()
    indice = indice_libro(libros, titulo)
    
    if indice == -1:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    libros.pop(indice)
    guardar_libros(libros)
    
    return {"message": "Libro eliminado exitosamente", "libro": titulo}