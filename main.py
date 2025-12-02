from json import load, dump
from typing import List, Dict
import fastapi
#La estructura de datos utilizada es una lista de diccionarios:
#[{libro1},{libro2},..,{libroN}]


def cargar_libros(ruta) -> List[Dict]:
  with open(ruta, "r", encoding="utf-8") as file:
    return load(file)



def guardar_libros(libros, ruta):
  with open(ruta, "w", encoding="utf-8") as file:
    dump(libros, file, indent=2)



def indice_libro(libros, titulo):
  i = 0
  for libro in libros:
    if libro["title"] == titulo:
      return i
    i += 1
  return -1



def agregar_libro(libros, titulo, autor = None, idioma = None, paginas = None,
                  pais = None, anio = None, imagen = None, link = None):

  nuevo_libro = {"author": autor,
                 "country": pais,
                 "imageLink": imagen,
                 "language": idioma,
                 "link": link,
                 "pages": paginas,
                 "title": titulo,
                 "year": anio}

  libros.append(nuevo_libro)
  print("Libro agregado exitosamente")



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
    print("Libro actualizado perri")
    return True
    
  return False


def eliminar_titulo(libros, titulo):
  indice = indice_libro(libros, titulo)
  if indice != -1:
    libros.pop(indice)
    print("Libro eliminado exitosamente")
    return True
  print("Libro no encontrado, no se pudo eliminar")
  return False


#No se si hara falta esta función 
def eliminar_indice(
    libros,
    indice):  #Recordar en la llamada restar 1 si ingresa el usuario
  if indice >= 0 and indice < len(libros):
    libros.pop(indice)
    print("Libro eliminado exitosamente")
    return True
  print("Libro no encontrado, no se pudo eliminar")
  return False


def mostrar_libro(libro): 
  libro = "Titulo: " + libro["title"] + "\n" + "Autor: " + libro["author"] + "\n" + "Idioma: " + libro["language"] + "\n" + "Paginas: " + str(libro["pages"]) + "\n" + "Pais: " + libro["country"] + "\n" + "Año: " + str(libro["year"]) + "\n" + "Imagen: " + libro["imageLink"] + "\n" + "Link: " + libro["link"]
  return libro

def mostrar_libro2(libro):
  
  print("Titulo: ", libro["title"])
  print("Autor: ", libro["author"])
  print("Idioma: ", libro["language"])
  print("Paginas: ", libro["pages"])
  print("Pais: ", libro["country"])
  print("Año: ", libro["year"])
  print("Imagen: ", libro["imageLink"])
  print("Link: ", libro["link"])

def mostrar_titulo(libros, titulo):
  indice = indice_libro(libros, titulo)
  libro = libros[indice]
  if indice != -1:
    return mostrar_libro(libro)
  else:
    return None


def mostrar_todos(libros):
  i = 1
  todos = ""
  print("\t-----Listado de libros:-----")
  for libro in libros:
    todos += "Indice: " + str(i) + "\n" + mostrar_libro(libro) + "\n------------------------------\n"
    i += 1

  return todos


def mostrar_todos2(libros):
  i = 1
  print("\t-----Listado de libros:-----")
  for libro in libros:
    print("Indice: ", i)
    mostrar_libro2(libro)
    print("------------------------------\n")
    i += 1


def filtrar_libros(libros, autor = None, idioma = None, pais= None, anio= None):

  filtro = libros
  
  if autor is not None:
    filtro = [libro for libro in libros if libro["author"] == autor]

  if idioma is not None:
    filtro = [libro for libro in filtro if libro["language"] == idioma]

  if pais is not None:
    filtro = [libro for libro in filtro if libro["country"] == pais]

  if anio is not None:
    filtro = [libro for libro in filtro if libro["year"] == anio]

  return filtro



def filtrar_libros2(libros, autor = None, idioma = None, pais= None, anio= None):

  filtro = libros
  
  if autor is not None:
    filtro = [libro for libro in libros if libro["author"] == autor]

  if idioma is not None:
    filtro = [libro for libro in filtro if libro["language"] == idioma]

  if pais is not None:
    filtro = [libro for libro in filtro if libro["country"] == pais]

  if anio is not None:
    filtro = [libro for libro in filtro if libro["year"] == anio]

  mostrar_todos(filtro)



def main():

  libros = cargar_libros("servidor/data/copybooks.json")
  mostrar_todos2(libros)
  #filtrar_libros(libros, idioma="English", pais="United Kingdom")
  #print(filtrar_libros(libros, "Dante Alighieri"))
  #Probar agregar y actualizar y guardar todo
  #Agregar filtrados
  #agregar_libro(libros,"Pepe el Grillo")
  #indice = indice_libro(libros,"Berserk")
  #print(indice)
  #Si todo funciona bien, hacer menu
  

if __name__ == "__main__":
  main()
