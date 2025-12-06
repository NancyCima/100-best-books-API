from json import load, dump
from typing import List, Dict

#La estructura de datos utilizada es una lista de diccionarios:
#[{libro1},{libro2},..,{libroN}]

#Agregar signaturas y declaracion de proposito a todas las funciones


#Funcion para cargar los libros del archivo json
def cargar_libros(ruta) -> List[Dict]:
  with open(ruta, "r", encoding="utf-8") as file:
    return load(file)


#Funcion para guardar los libros en el archivo json
def guardar_libros(libros, ruta) -> None:
  with open(ruta, "w", encoding="utf-8") as file:
    dump(libros, file, indent=2)


#Funcion para obtener el indice de un libro
def indice_libro(libros, titulo) -> int:
  i = 0
  for libro in libros:
    if libro["title"] == titulo:
      return i
    i += 1
  return -1


#Funcion para agregar un libro
def agrega_libro(libros, titulo, autor, idioma, paginas,
                  pais, anio, imagen = None, link = None) -> None:

  nuevo_libro = {"author": autor,
                 "country": pais,
                 "imageLink": imagen,
                 "language": idioma,
                 "link": link,
                 "pages": int(paginas),
                 "title": titulo,
                 "year": int(anio)}

  libros.append(nuevo_libro)


#Funcion para actualizar libro
def actualiza_libro(libros, titulo,tituloA, autor = None, idioma = None, paginas = None,
                  pais = None, anio = None, imagen = None, link = None) -> bool:

  indice = indice_libro(libros, titulo)
  
  if autor is None:
    autor = libros[indice]["author"]
  if idioma is None:
    idioma = libros[indice]["language"]
  if paginas is None:
    paginas = libros[indice]["pages"] 
  if pais is None:
    pais = libros[indice]["country"]
  if anio is None:
    anio = libros[indice]["year"]
  if imagen is None:
    imagen = libros[indice]["imageLink"]
  if link is None:
    link = libros[indice]["link"]
  
  libro_actualizado = {"author": autor,
                 "country": pais,
                 "imageLink": imagen,
                 "language": idioma,
                 "link": link,
                 "pages": int(paginas),
                 "title": tituloA,
                 "year": int(anio)}

  if indice != -1:
    libros[indice] = libro_actualizado
    return True
  return False


#Funcion para eliminar un libro
def eliminar_titulo(libros, titulo) -> bool:
  indice = indice_libro(libros, titulo)
  if indice != -1:
    libros.pop(indice)
    return True
  return False


#Funcion para buscar un libro 
def mostrar_titulo(libros, titulo):
  indice = indice_libro(libros, titulo)
  libro = libros[indice]
  if indice != -1:
    return libro
  else:
    return None


#Funcion para filtrar libros 
def filtrar_libros(libros, autor = None, idioma = None, pais= None, anioMin = None, anioMax = None) -> List[Dict]:

  if anioMin is None:
    anioMin=-9999

  if anioMax is None:
    anioMax=9999
  
  filtro = libros
  
  if autor is not None:
    filtro = [libro for libro in filtro if libro["author"] == autor]

  if idioma is not None:
    filtro = [libro for libro in filtro if libro["language"] == idioma]

  if pais is not None:
    filtro = [libro for libro in filtro if libro["country"] == pais]

  filtro = [libro for libro in filtro if libro["year"] >= int(anioMin) and libro["year"] <= int(anioMax)]

  return filtro

