"""
Cliente API con soporte para autenticación Basic
"""
import requests
from requests.auth import HTTPBasicAuth
from getpass import getpass


# Configuración del servidor
URL = "http://localhost:8000"

# Variables globales para credenciales
USERNAME = None
PASSWORD = None

def mostrar_libro(libro):
    """Muestra la información de un libro"""
    print("Título: ", libro["title"])
    print("Autor: ", libro["author"])
    print("Idioma: ", libro["language"])
    print("Páginas: ", libro["pages"])
    print("País: ", libro["country"])
    print("Año: ", libro["year"])
    print("Imagen: ", libro["imageLink"] if libro["imageLink"] else "No disponible")
    print("Link: ", libro["link"] if libro["link"] else "No disponible")

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
    print("\n" + "="*50)
    print("BIBLIOTECA ONLINE - MENÚ PRINCIPAL")
    print("="*50)
    print("\nOpciones:")
    print("\t1. Buscar libro por título")
    print("\t2. Filtrar libros (autor, idioma, país, año)")
    print("\t3. Agregar nuevo libro")
    print("\t4. Actualizar libro existente")
    print("\t5. Eliminar libro")
    print("\t6. Salir")
    
    while True:
        try:
            opc_str = input("\nIngrese una opción (1-6) > ").strip()
            if not opc_str:
                print("❌ Error: Debe ingresar un número")
                continue
            opc = int(opc_str)
            if 1 <= opc <= 6:
                return opc
            else:
                print("❌ Error: Opción inválida. Ingrese un número entre 1 y 6")
        except ValueError:
            print("❌ Error: Debe ingresar un número válido entre 1 y 6")

def solicitar_credenciales(max_intentos: int = 3) -> tuple:
    """
    Solicita credenciales al usuario y valida contra .env
    
    Args:
        max_intentos: Número máximo de intentos permitidos
        
    Returns:
        tuple: (username, password) si son válidas
        
    Raises:
        ValueError: Si se exceden los intentos o credenciales inválidas
    """
    # Obtener credenciales correctas del .env
    username_correcto = "admin"
    password_correcto = "redes2025"
    
    # Validar que existan en el .env
    if not username_correcto or not password_correcto:
        raise ValueError(
            "ERROR: Credenciales no configuradas en .env\n"
            "   Asegúrate de tener USERNAME y PASSWORD definidos"
        )
    
    for intento in range(1, max_intentos + 1):
        print(f"\nIntento {intento} de {max_intentos}")
        print("-"*50)
        
        username = input("Usuario: ").strip()
        # Usar getpass para ocultar la contraseña al escribir
        password = getpass("Contraseña: ").strip()
        
        # Validar credenciales
        if username == username_correcto and password == password_correcto:
            print("✅ Autenticación exitosa\n")
            return username, password
        else:
            if intento < max_intentos:
                print("❌ Credenciales incorrectas. Intenta nuevamente.")
            else:
                print("❌ Credenciales incorrectas.")
    
    # Si llegamos aquí, se excedieron los intentos
    raise ValueError(
        f"❌ ERROR: Máximo de intentos ({max_intentos}) excedido.\n"
        "   Acceso denegado."
    )

def obtener_entero(mensaje: str, obligatorio: bool = True, minimo: int = None, maximo: int = None):
    """
    Solicita un número entero al usuario con validación
    
    Args:
        mensaje: Texto a mostrar
        obligatorio: Si es True, no acepta entrada vacía
        minimo: Valor mínimo permitido (opcional)
        maximo: Valor máximo permitido (opcional)
    
    Returns:
        int o None: Número ingresado, o None si no es obligatorio y se dejó vacío
    """
    while True:
        valor_str = input(mensaje).strip()
        
        # Si no es obligatorio y está vacío, retorna None
        if not valor_str and not obligatorio:
            return None
        
        # Si es obligatorio y está vacío, muestra error
        if not valor_str and obligatorio:
            print("❌ Error: Este campo es obligatorio")
            continue
        
        # Intentar convertir a entero
        try:
            valor = int(valor_str)
        except ValueError:
            print("❌ Error: Debe ingresar un número entero válido")
            continue
        
        # Validar rango mínimo
        if minimo is not None and valor < minimo:
            print(f"❌ Error: El valor debe ser mayor o igual a {minimo}")
            continue
        
        # Validar rango máximo
        if maximo is not None and valor > maximo:
            print(f"❌ Error: El valor debe ser menor o igual a {maximo}")
            continue
        
        return valor

def obtener_filtros() -> dict:
    """Solicita filtros de búsqueda al usuario"""
    print("\n" + "-"*40)
    print("FILTROS DE BÚSQUEDA")
    print("(Deje vacío cualquier filtro que no desee aplicar)")
    print("-"*40)
    
    filtros = {}
    
    # Campos de texto
    autor = input("Autor: ").strip()
    if autor:
        filtros['autor'] = autor
    
    idioma = input("Idioma: ").strip()
    if idioma:
        filtros['idioma'] = idioma
    
    pais = input("País: ").strip()
    if pais:
        filtros['pais'] = pais
    
    # Campos numéricos
    anio_min = obtener_entero("Año mínimo: ", obligatorio=False, minimo=-5000)
    if anio_min is not None:
        filtros['anioMin'] = anio_min
    
    anio_max = obtener_entero("Año máximo: ", obligatorio=False, minimo=-5000)
    if anio_max is not None:
        filtros['anioMax'] = anio_max
    
    return filtros

def obtener_datos_libro(tipo: str = "nuevo") -> tuple:
    """
    Solicita datos de un libro al usuario
    
    Args:
        tipo: "nuevo" para agregar, "actualizar" para modificar
    
    Returns:
        tuple: (titulo, params) o (titulo_original, titulo_nuevo, params)
    """
    print("\n" + "-"*40)
    print(f"INGRESE LOS DATOS DEL LIBRO ({tipo.upper()})")
    print("(*) Campos obligatorios")
    print("-"*40)
    
    # Título (manejo especial para actualización)
    if tipo == "actualizar":
        titulo_original = input("Título del libro a actualizar (*) > ").strip()
        if not titulo_original:
            print("❌ Error: El título original es obligatorio")
            return None, None, None
        
        titulo_nuevo = input("Nuevo título (*) > ").strip()
        if not titulo_nuevo:
            print("❌ Error: El nuevo título es obligatorio")
            return None, None, None
    else:
        titulo = input("Título (*) > ").strip()
        if not titulo:
            print("❌ Error: El título es obligatorio")
            return None, None
    
    # Campos obligatorios de texto
    autor = input("Autor (*) > ").strip()
    if not autor:
        print("❌ Error: El autor es obligatorio")
        return (None, None) if tipo == "nuevo" else (None, None, None)
    
    idioma = input("Idioma (*) > ").strip()
    if not idioma:
        print("❌ Error: El idioma es obligatorio")
        return (None, None) if tipo == "nuevo" else (None, None, None)
    
    pais = input("País (*) > ").strip()
    if not pais:
        print("❌ Error: El país es obligatorio")
        return (None, None) if tipo == "nuevo" else (None, None, None)
    
    # Campos obligatorios numéricos
    paginas = obtener_entero("Número de páginas (*) > ", obligatorio=True, minimo=1)
    if paginas is None:
        return (None, None) if tipo == "nuevo" else (None, None, None)
    
    anio = obtener_entero("Año (*) > ", obligatorio=True, minimo=-5000, maximo=2100)
    if anio is None:
        return (None, None) if tipo == "nuevo" else (None, None, None)
    
    # Campos opcionales
    imagen = input("Link de imagen (opcional) > ").strip()
    link = input("Link del libro (opcional) > ").strip()
    
    # Construir parámetros
    params = {
        'autor': autor,
        'idioma': idioma,
        'pais': pais,
        'paginas': paginas,
        'anio': anio
    }
    
    # Campos específicos por tipo
    if tipo == "actualizar":
        params['tituloAct'] = titulo_nuevo
    
    # Agregar campos opcionales si no están vacíos
    if imagen:
        params['imagen'] = imagen
    if link:
        params['link'] = link
    
    # Retornar según el tipo
    if tipo == "nuevo":
        return titulo, params
    else:
        return titulo_original, titulo_nuevo, params

def main():
    """Función principal del cliente"""
    global USERNAME, PASSWORD
    
    print("\n" + "="*60)
    print("CLIENTE API - BIBLIOTECA ONLINE")
    print("="*60)
    
    # Verificar conexión con el servidor
    try:
        print("\nConectando con el servidor...")
        response = requests.get(URL, timeout=5)
        
        if response.status_code == 200:
            bienvenida = response.json()
            print("Conexión exitosa con el servidor")
            print(f"   Servidor: {bienvenida.get('servidor', 'Desconocido')}")
            print(f"   Libros disponibles: {bienvenida.get('cantidad_libros', 0)}")
        else:
            print(f"⚠️ Servidor respondió con código: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: No se puede conectar con el servidor en {URL}")
        print("   Asegúrate de que el servidor esté ejecutándose")
        return
    except requests.exceptions.Timeout:
        print("❌ Error: Tiempo de espera agotado al conectar con el servidor")
        return
    except Exception as e:
        print(f"❌ Error al conectar con el servidor: {e}")
        return
    
    # Bucle principal del menú
    opc = menu()
    
    while opc != 6:
        try:
            if opc == 1:  # Buscar libro por título
                print("\nBUSCAR LIBRO POR TÍTULO")
                titulo = input("Ingrese el título del libro: ").strip()
                
                if not titulo:
                    print("❌ Error: Debe ingresar un título")
                else:
                    response = requests.get(f"{URL}/libros/{titulo}")
                    
                    if response.status_code == 200:
                        libro = response.json()
                        print(f"\n✅ Libro encontrado:")
                        mostrar_libro(libro)
                    elif response.status_code == 404:
                        print("❌ Libro no encontrado")
                    else:
                        error = response.json()
                        print(f"❌ Error del servidor: {error.get('detail', 'Error desconocido')}")
            
            elif opc == 2:  # Filtrar libros
                print("\nFILTRAR LIBROS")
                filtros = obtener_filtros()
                
                if filtros:
                    response = requests.get(f"{URL}/libros/", params=filtros)
                else:
                    response = requests.get(f"{URL}/libros/")
                
                if response.status_code == 200:
                    libros = response.json()
                    if libros:
                        print(f"\n✅ Se encontraron {len(libros)} libro(s):")
                        mostrar_todos(libros)
                    else:
                        print("❌ No se encontraron libros con esos filtros")
                else:
                    error = response.json()
                    print(f"❌ Error: {error.get('detail', 'Error desconocido')}")
            
            elif opc == 3:  # Agregar libro (REQUIERE AUTENTICACIÓN)
                print("\n AGREGAR NUEVO LIBRO")
                
                # Solicitar credenciales
                if not USERNAME or not PASSWORD:
                    USERNAME, PASSWORD = solicitar_credenciales()
                
                # Obtener datos del libro
                resultado = obtener_datos_libro("nuevo")
                if resultado[0] is None:  # Error en la entrada
                    continue
                
                titulo, params = resultado
                
                # Enviar solicitud con autenticación
                auth = HTTPBasicAuth(USERNAME, PASSWORD)
                response = requests.post(
                    f"{URL}/libros/{titulo}",
                    params=params,
                    auth=auth,
                    timeout=10
                )
                
                if response.status_code == 200:
                    resultado = response.json()
                    print(f"\n✅ {resultado['message']}")
                    if 'usuario_autenticado' in resultado:
                        print(f"   Usuario: {resultado['usuario_autenticado']}")
                elif response.status_code == 401:
                    print("❌ Error de autenticación: Credenciales incorrectas")
                    USERNAME = PASSWORD = None  # Resetear credenciales
                else:
                    error = response.json()
                    print(f"❌ Error: {error.get('detail', 'Error desconocido')}")
            
            elif opc == 4:  # Actualizar libro
                print("\n ACTUALIZAR LIBRO")

                # Solicitar credenciales si no están guardadas
                if not USERNAME or not PASSWORD:
                    USERNAME, PASSWORD = solicitar_credenciales()
                
                # Obtener datos del libro
                resultado = obtener_datos_libro("actualizar")
                if resultado[0] is None:  # Error en la entrada
                    continue
                
                titulo_original, titulo_nuevo, params = resultado
                
                # Enviar solicitud (sin autenticación para PUT según el proyecto)
                response = requests.put(
                    f"{URL}/libros/{titulo_original}",
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    resultado = response.json()
                    print(f"\n✅ {resultado['message']}")
                else:
                    error = response.json()
                    print(f"❌ Error: {error.get('detail', 'Error desconocido')}")
            
            elif opc == 5:  # Eliminar libro (REQUIERE AUTENTICACIÓN)
                print("\n ELIMINAR LIBRO")
                
                # Solicitar título
                titulo = input("Ingrese el título del libro a eliminar: ").strip()
                if not titulo:
                    print("❌ Error: Debe ingresar un título")
                    continue
                
                # Solicitar credenciales si no están guardadas
                if not USERNAME or not PASSWORD:
                    USERNAME, PASSWORD = solicitar_credenciales()
                
                # Confirmar eliminación
                confirmar = input(f"¿Está seguro de eliminar '{titulo}'? (s/n): ").strip().lower()
                if confirmar != 's':
                    print("❌ Eliminación cancelada")
                    continue
                
                # Enviar solicitud con autenticación
                auth = HTTPBasicAuth(USERNAME, PASSWORD)
                response = requests.delete(
                    f"{URL}/libros/{titulo}",
                    auth=auth,
                    timeout=10
                )
                
                if response.status_code == 200:
                    resultado = response.json()
                    print(f"\n✅ {resultado['message']}")
                    if 'usuario_autenticado' in resultado:
                        print(f"   Usuario: {resultado['usuario_autenticado']}")
                elif response.status_code == 401:
                    print("❌ Error de autenticación: Credenciales incorrectas")
                    USERNAME = PASSWORD = None  # Resetear credenciales
                else:
                    error = response.json()
                    print(f"❌ Error: {error.get('detail', 'Error desconocido')}")
            
            else:
                print("❌ Opción no válida")
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la solicitud HTTP: {e}")
        except ValueError as e:
            print(f"❌ Error de validación: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        # Volver al menú
        opc = menu()
    
    print("\n" + "="*50)
    print("¡Gracias por usar la Biblioteca Online!")
    print("Hasta pronto")
    print("="*50)

if __name__ == "__main__":
    main()