"""
Cliente API con soporte para autenticación Basic
Versión corregida con mejor manejo de errores en input
"""
import requests
from requests.auth import HTTPBasicAuth

# Configuración del servidor
URL = "http://localhost:8000"  # Cambiar por IP del servidor remoto

# Credenciales para métodos POST y DELETE
USERNAME = "admin"
PASSWORD = "redes2025"

def mostrar_libro(libro):
    """Muestra la información de un libro"""
    print("Titulo: ", libro["title"])
    print("Autor: ", libro["author"])
    print("Idioma: ", libro["language"])
    print("Páginas: ", libro["pages"])
    print("País: ", libro["country"])
    print("Año: ", libro["year"])
    print("Imagen: ", libro["imageLink"])
    print("Link: ", libro["link"])

def mostrar_todos(libros):
    """Muestra todos los libros de una lista"""
    i = 1
    print("\t-----Listado de libros:-----")
    for libro in libros:
        print("Índice: ", i)
        mostrar_libro(libro)
        print("------------------------------\n")
        i += 1

def menu() -> int:
    """Muestra el menú de opciones con validación mejorada"""
    print("Opciones:\n")
    print("\t1. Buscar libro")
    print("\t2. Filtrar libros")
    print("\t3. Agregar libro (requiere autenticación)")
    print("\t4. Actualizar libro")
    print("\t5. Eliminar libro (requiere autenticación)")
    print("\t6. Salir")
    
    while True:
        try:
            opc_str = input("\nIngrese una opción (1-6) > ").strip()
            if not opc_str:
                print("Error: Debe ingresar un número")
                continue
            opc = int(opc_str)
            if 1 <= opc <= 6:
                return opc
            else:
                print("Error: Opción inválida. Ingrese un número entre 1 y 6")
        except ValueError:
            print("Error: Debe ingresar un número válido entre 1 y 6")

def armar_url_filtro(url):
    """Construye la URL para filtrar libros"""
    print("\nAclaración: si no desea ingresar un filtro, deje en blanco el mismo\n")
    autor = input("Ingrese el autor >")
    idioma = input("Ingrese el idioma >")
    pais = input("Ingrese el país >")
    anioMin = input("Ingrese el año mínimo >")
    anioMax = input("Ingrese el año máximo >")

    params = {}
    if autor:
        params['autor'] = autor
    if idioma:
        params['idioma'] = idioma
    if pais:
        params['pais'] = pais
    if anioMin:
        params['anioMin'] = anioMin
    if anioMax:
        params['anioMax'] = anioMax

    return url, params

def armar_url_agregar(url):
    """Construye la URL y parámetros para agregar un libro"""
    print("\nAclaración: los campos no requeridos se pueden dejar en blanco\n")
    titulo = input("Ingrese el título (*requerido) >")
    autor = input("Ingrese el autor (*requerido) >")
    idioma = input("Ingrese el idioma (*requerido) >")
    paginas = input("Ingrese el número de páginas (*requerido) >")
    pais = input("Ingrese el país (*requerido) >")
    anio = input("Ingrese el año (*requerido) >")
    imagen = input("Ingrese el link de la imagen >")
    link = input("Ingrese el link del libro >")

    url = f"{url}{titulo}"
    
    params = {
        'autor': autor,
        'idioma': idioma,
        'paginas': paginas,
        'pais': pais,
        'anio': anio
    }
    
    if imagen:
        params['imagen'] = imagen
    if link:
        params['link'] = link

    return url, params

def armar_url_actualizar(url):
    """Construye la URL y parámetros para actualizar un libro"""
    print("Aclaración: los campos no requeridos se pueden dejar en blanco")

    titulo = input("Ingrese el título del libro a actualizar (*requerido) >")
    tituloAct = input("Ingrese el nuevo título del libro (*requerido) >")
    autor = input("Ingrese el autor (*requerido) >")
    idioma = input("Ingrese el idioma (*requerido) >")
    paginas = input("Ingrese el número de páginas (*requerido) >")
    pais = input("Ingrese el país (*requerido) >")
    anio = input("Ingrese el año (*requerido) >")
    imagen = input("Ingrese el link de la imagen >")
    link = input("Ingrese el link del libro >")

    url = f"{url}{titulo}"
    
    params = {
        'tituloAct': tituloAct,
        'autor': autor,
        'idioma': idioma,
        'paginas': paginas,
        'pais': pais,
        'anio': anio
    }
    
    if imagen:
        params['imagen'] = imagen
    if link:
        params['link'] = link

    return url, params

def main():
    """Función principal del cliente"""
    # Mensaje de bienvenida con manejo de errores
    try:
        response = requests.get(URL)
        print(f"Status code: {response.status_code}")
        
        response.raise_for_status()
        bienvenida = response.json()
        
        print("\n--- Respuesta del servidor ---")
        for key, value in bienvenida.items():
            print(f"{key}: {value}")
        print("----------------------------\n")
    except requests.exceptions.ConnectionError:
        print(f"Error: No se puede conectar con el servidor en {URL}")
        print("Asegúrate de que el servidor esté ejecutándose")
        return
    except Exception as e:
        print(f"Error al conectar con el servidor: {e}")
        return

    opc = menu()

    while opc != 6:
        url = f"{URL}/libros/"

        try:
            if opc == 1:  # Buscar libro
                titulo = input("Ingrese el título del libro >")
                url = f"{url}{titulo}"
                rta = requests.get(url)
                print()
                
                if rta.status_code == 200:
                    libro = rta.json()
                    mostrar_libro(libro)
                else:
                    error = rta.json()
                    print(f"Error: {error.get('detail', 'Error desconocido')}")

            elif opc == 2:  # Filtrar libros
                url, params = armar_url_filtro(url)
                rta = requests.get(url, params=params)
                print()
                
                if rta.status_code == 200:
                    libros = rta.json()
                    mostrar_todos(libros)
                else:
                    error = rta.json()
                    print(f"Error: {error.get('detail', 'Error desconocido')}")

            elif opc == 3:  # Agregar libro (CON AUTENTICACIÓN)
                url, params = armar_url_agregar(url)
                auth = HTTPBasicAuth(USERNAME, PASSWORD)
                rta = requests.post(url, params=params, auth=auth)
                print()
                
                if rta.status_code == 200:
                    msj = rta.json()
                    print(f"✓ {msj['message']}")
                else:
                    error = rta.json()
                    print(f"Error: {error.get('detail', 'Error desconocido')}")

            elif opc == 4:  # Actualizar libro
                url, params = armar_url_actualizar(url)
                rta = requests.put(url, params=params)
                print()
                
                if rta.status_code == 200:
                    msj = rta.json()
                    print(f"✓ {msj['message']}")
                else:
                    error = rta.json()
                    print(f"Error: {error.get('detail', 'Error desconocido')}")

            elif opc == 5:  # Eliminar libro (CON AUTENTICACIÓN)
                titulo = input("Ingrese el título del libro a eliminar >")
                url = f"{url}{titulo}"
                auth = HTTPBasicAuth(USERNAME, PASSWORD)
                rta = requests.delete(url, auth=auth)
                print()
                
                if rta.status_code == 200:
                    msj = rta.json()
                    print(f"✓ {msj['message']}")
                else:
                    error = rta.json()
                    print(f"Error: {error.get('detail', 'Error desconocido')}")

        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud: {e}")
        except Exception as e:
            print(f"Error: {e}")

        print()
        opc = menu()

    print("\n¡Hasta luego!")

if __name__ == "__main__":
    main()
