from requests import *

# Configuración del servidor
URL = "http://localhost:8000"  # URL local para desarrollo

#Funcion para mostrar un libro
def mostrar_libro(libro):

  print("Titulo: ", libro["title"])
  print("Autor: ", libro["author"])
  print("Idioma: ", libro["language"])
  print("Paginas: ", libro["pages"])
  print("Pais: ", libro["country"])
  print("Año: ", libro["year"])
  print("Imagen: ", libro["imageLink"])
  print("Link: ", libro["link"])

#Funcion para mostrar todos los libros
def mostrar_todos(libros):
  i = 1
  print("\t-----Listado de libros:-----")
  for libro in libros:
    print("Indice: ", i)
    mostrar_libro(libro)
    print("------------------------------\n")
    i += 1

#Funcion para validar opcion
def valida(opc):
  while opc < 1 or opc > 6:
    print("Opción inválida")
    opc = int(input("Ingrese una opción válida >"))
  return opc

#Menu de opciones 
def menu() -> int:
  print("Opciones:\n")
  print("\t1. Buscar libro")
  print("\t2. Filtrar libros")
  print("\t3. Agregar libro")
  print("\t4. Actualizar libro")
  print("\t5. Eliminar libro")
  print("\t6. Salir")
  opc = int(input("\nIngrese una opcion >"))
  opc = valida(opc)
  return opc

#Funcion para armar la url de un filtrado de libros
def armar_url_filtro(url):

  print(
      "\nAclaracion: si no desea ingresar un filtro, deje en blanco el mismo\n"
  )
  autor = input("Ingrese el autor >")
  idioma = input("Ingrese el idioma >")
  pais = input("Ingrese el pais >")
  anioMin = input("Ingrese el año minimo >")
  anioMax = input("Ingrese el año maximo >")

  if autor != "" or idioma != "" or pais != "" or anioMin != "" or anioMax != "":
    url += "?"

  if autor != "":
    autor = autor.replace(" ", "%20")
    url += "autor=" + autor

  if idioma != "":
    idioma = idioma.replace(" ", "%20")
    url += "&idioma=" + idioma

  if pais != "":
    pais = pais.replace(" ", "%20")
    url += "&pais=" + pais

  if anioMin != "":
    url += "&anioMin=" + anioMin

  if anioMax != "":
    url += "&anioMax=" + anioMax

  return url

#Funcion para armar url de un agregado de libro
def armar_url_agregar(url):

  print("\nAclaracion: los campos no requeridos se pueden dejar en blanco\n")
  titulo = input("Ingrese el titulo (*requerido) >")
  autor = input("Ingrese el autor (*requerido) >")
  idioma = input("Ingrese el idioma (*requerido) >")
  paginas = input("Ingrese el numero de paginas (*requerido) >")
  pais = input("Ingrese el pais (*requerido) >")
  anio = input("Ingrese el año (*requerido) >")
  imagen = input("Ingrese el link de la imagen >")
  link = input("Ingrese el link del libro >")

  titulo = titulo.replace(" ", "%20")
  url += titulo

  url += "?"

  autor = autor.replace(" ", "%20")
  url += "&autor=" + autor

  idioma = idioma.replace(" ", "%20")
  url += "&idioma=" + idioma

  url += "&paginas=" + paginas

  pais = pais.replace(" ", "%20")
  url += "&pais=" + pais

  url += "&anio=" + anio

  if imagen != "":
    url += "&imagen=" + imagen

  if link != "":
    url += "&link=" + link

  return url

#Funcion para armar url de una actualización de libro
def armar_url_actualizar(url):

  print("Aclaracion: los campos no requeridos se pueden dejar en blanco")

  titulo = input("Ingrese el título del libro a actualizar (*requerido) >")
  tituloAct = input("Ingrese el nuevo título del libro (*requerido) >")
  autor = input("Ingrese el autor (*requerido) >")
  idioma = input("Ingrese el idioma (*requerido) >")
  paginas = input("Ingrese el numero de paginas (*requerido) >")
  pais = input("Ingrese el pais (*requerido) >")
  anio = input("Ingrese el año (*requerido) >")
  imagen = input("Ingrese el link de la imagen >")
  link = input("Ingrese el link del libro >")

  titulo = titulo.replace(" ", "%20")
  url += titulo

  url += "?"

  tituloAct = tituloAct.replace(" ", "%20")
  url += "tituloAct=" + tituloAct

  autor = autor.replace(" ", "%20")
  url += "&autor=" + autor

  idioma = idioma.replace(" ", "%20")
  url += "&idioma=" + idioma

  url += "&paginas=" + paginas

  pais = pais.replace(" ", "%20")
  url += "&pais=" + pais

  url += "&anio=" + anio

  if imagen != "":
    url += "&imagen=" + imagen

  if link != "":
    url += "&link=" + link

  return url


def main():

  # Mensaje de bienvenida con manejo de errores
  try:
    response = get(URL)
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response content: {response.text}")
    
    response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
    bienvenida = response.json()
    
    print("\n--- Respuesta del servidor ---")
    for key, value in bienvenida.items():
      print(f"{key}: {value}")
    print("----------------------------\n")
  except Exception as e:
    print(f"Error al conectar con el servidor: {e}")
    print(f"Asegúrate de que el servidor esté ejecutándose en {URL}")
    return

  opc = menu()

  while opc != 6:

    url = URL + "/libros/"

    if opc == 1:  #Buscar libro
      titulo = input("Ingrese el título del libro >")
      if " " in titulo:
        titulo = titulo.replace(" ", "%20")
      url += titulo
      rta = get(url)
      print()
      libro = rta.json()
      if rta.status_code == 200:
        mostrar_libro(libro)
      else: 
        for i in libro:
          print(">>>",libro[i])
        

    if opc == 2:  #Filtrar libros

      url = armar_url_filtro(url)

      rta = get(url)
      libros = get(url).json()
      
      print()
      if rta.status_code == 200:
        mostrar_todos(libros)
      else:
        for i in libros:
          print(">>>",libros[i])

    if opc == 3:  #Agregar libro
      
      url = armar_url_agregar(url)

      msj = post(url).json()
      
      print()
      for i in msj:
        print(msj[i])

    if opc == 4:  #Actualizar libro

      url = armar_url_actualizar(url)

      msj = put(url).json()

      print()
      for i in msj:
        print(msj[i])

    if opc == 5:  #Eliminar libro
      titulo = input("Ingrese el título del libro a eliminar >")
      titulo = titulo.replace(" ", "%20")

      url += titulo

      msj = delete(url).json()

      print()
      for i in msj:
        print(msj[i])

    print()
    opc = menu()


if __name__ == "__main__":
  main()
