#Creacion del servidor con los metodos
from fastapi import FastAPI, HTTPException
from typing import List, Optional
import json
from libros import *

app = FastAPI()

@app.get("/")
def bienvenida():
    libros = cargar_libros("data/copybooks.json")
    cantidad = len(libros)
    return {"Bienvenido a la Biblioteca Online" : "Cantidad de libros: " + str(cantidad)}
    

@app.get("/libros/")
def get_filtrar_libros(autor=None,idioma=None, pais=None, 
                       anioMin=None, anioMax = None) -> List[dict]:
    
    libros = cargar_libros("data/copybooks.json")
    filtrado = filtrar_libros(libros, autor, idioma, pais, anioMin, anioMax)
    if filtrado != []:
        return filtrado
    else:
        raise HTTPException(
            status_code=404,
            detail="No hay libros disponibles para los filtros seleccionados")


# Ruta para obtener un libro por su índice
@app.get("/libros/{titulo}")
def get_libro(titulo: str) -> dict:
    libros = cargar_libros("data/copybooks.json")
    libro = mostrar_titulo(libros, titulo)

    if libro is not None:
        return libro
    else:
        raise HTTPException(status_code=404, detail="Libro no encontrado")


@app.post("/libros/{titulo}")
def agregar_libro(titulo, autor, idioma, paginas, pais,
            anio, imagen = None, link = None):
    libros = cargar_libros("data/copybooks.json")
    agrega_libro(libros, titulo, autor, idioma, paginas, pais, anio, imagen, link)
    guardar_libros(libros,"data/copybooks.json")
    return {"message": "Libro agregado exitosamente"}



@app.put("/libros/{titulo}")
def actualizar_libro(titulo,tituloAct, autor, idioma,
                paginas, pais, anio, imagen = None, link = None):
    libros = cargar_libros("data/copybooks.json")
    indice = indice_libro(libros, titulo)
    if indice != -1:
        actualiza_libro(libros,titulo,tituloAct, autor, idioma, paginas, pais, anio, imagen, link)
        guardar_libros(libros,"data/copybooks.json")
        return {"message": "Libro actualizado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Libro no encontrado")



@app.delete("/libros/{titulo}")
def eliminar_libro(titulo):
    
    data = cargar_libros("data/copybooks.json")

    eliminado = eliminar_titulo(data, titulo)

    if eliminado:
        guardar_libros(data, "data/copybooks.json")
        return {"message": "Libro eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Libro no encotrado")
