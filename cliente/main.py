"""
Cliente API con autenticación Basic
"""
import requests
from requests.auth import HTTPBasicAuth
from getpass import getpass
import sys

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
    """Muestra el menú de opciones"""
    print("\n" + "="*50)
    print("BIBLIOTECA ONLINE - MENÚ PRINCIPAL")
    print("="*50)
    print("\nOpciones:")
    print("\t1. Buscar libro por título")
    print("\t2. Filtrar libros (autor, idioma, país, año)")
    print("\t3. Actualizar libro existente")
    print("\t4. Agregar nuevo libro")
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
    Solicita credenciales al usuario
    
    Args:
        max_intentos: Número máximo de intentos permitidos
        
    Returns:
        tuple: (username, password)
        
    Raises:
        SystemExit: Si se exceden los intentos
    """

    print("Esta operación requiere credenciales de autenticación")
    print(f"Intentos disponibles: {max_intentos}")
    print("─"*50)
    
    for intento in range(1, max_intentos + 1):
        print(f"\nIntento {intento} de {max_intentos}")
        print("-"*50)
        
        username = input("Usuario: ").strip()
        if not username:
            print("❌ El usuario no puede estar vacío")
            continue
        
        # Usar getpass para ocultar la contraseña al escribir
        password = getpass("Contraseña: ").strip()
        if not password:
            print("❌ La contraseña no puede estar vacía")
            continue
        
        # Probar credenciales con el servidor
        print("Verificando credenciales...")
        try:
            auth = HTTPBasicAuth(username, password)
            response = requests.get(f"{URL}/auth/test", auth=auth, timeout=5)
            
            if response.status_code == 200:
                resultado = response.json()
                print(f"✅ Autenticación exitosa!")
                print(f"   Bienvenido, {resultado.get('usuario', username)}!")
                return username, password
            elif response.status_code == 401:
                if intento < max_intentos:
                    print("❌ Credenciales incorrectas. Intenta nuevamente.")
                else:
                    print("❌ Credenciales incorrectas.")
            else:
                print(f"Error inesperado del servidor: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            if intento < max_intentos:
                continuar = input("¿Desea intentar nuevamente? (s/n): ").strip().lower()
                if continuar != 's':
                    break
    
    # Si llegamos aquí, se excedieron los intentos
    print(f"\n❌ Máximo de intentos ({max_intentos}) excedido.")
    print("   Acceso denegado. Volviendo al menú principal...")
    return None, None

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
    print("\n" + "="*60)
    print("FILTROS DE BÚSQUEDA")
    print("="*60)
    print("Deje vacío cualquier filtro que no desee aplicar")
    print("─"*60)
    
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
    print("\n" + "="*60)
    print(f"INGRESE LOS DATOS DEL LIBRO ({tipo.upper()})")
    print("="*60)
    print("(*) Campos obligatorios")
    print("─"*60)
    
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
        titulo_para_params = titulo_nuevo  # Para PUT, usamos el nuevo título
    else:
        titulo = input("Título (*) > ").strip()
        if not titulo:
            print("❌ Error: El título es obligatorio")
            return None, None
        titulo_para_params = titulo  # Para POST, usamos el título ingresado
    
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
        'titulo': titulo_para_params,
        'autor': autor,
        'idioma': idioma,
        'pais': pais,
        'paginas': paginas,
        'anio': anio
    }
    
    # Campos específicos por tipo
    # Solo para actualizar necesitamos tituloAct
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
            if opc == 1:  # Buscar libro por título (PÚBLICO)
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
                        print(f"❌ Error: {error.get('detail', 'Error desconocido')}")
            
            elif opc == 2:  # Filtrar libros (PÚBLICO)
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
            
            elif opc == 3:  # Actualizar libro (PÚBLICO)
                print("\nACTUALIZAR LIBRO")
                
                resultado = obtener_datos_libro("actualizar")
                if resultado[0] is None:
                    continue
                
                titulo_original, titulo_nuevo, params = resultado
                
                response = requests.put(
                    f"{URL}/libros/{titulo_original}",
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    resultado = response.json()
                    print(f"\n✅ {resultado.get('message', 'Libro actualizado exitosamente')}")
                else:
                    error = response.json()
                    print(f"❌ Error: {error.get('detail', 'Error desconocido')}")
            
            elif opc == 4:  # Agregar libro (PROTEGIDO)
                # Solicitar credenciales si no están guardadas
                if not USERNAME or not PASSWORD:
                    USERNAME, PASSWORD = solicitar_credenciales()
                    if not USERNAME:  # Falló la autenticación
                        opc = menu()

                print("\nAGREGAR NUEVO LIBRO")    
                
                # Obtener datos del libro
                resultado = obtener_datos_libro("nuevo")
                if resultado[0] is None:
                    continue
                
                titulo, params = resultado
                
                # Enviar solicitud con autenticación
                auth = HTTPBasicAuth(USERNAME, PASSWORD)
                response = requests.post(
                    f"{URL}/libros/",
                    params=params,
                    auth=auth,
                    timeout=10
                )
                
                if response.status_code == 200:
                    resultado = response.json()
                    print(f"\n✅ {resultado.get('mensaje', 'Libro agregado exitosamente')}")
                    if 'usuario_autenticado' in resultado:
                        print(f"   Usuario: {resultado['usuario_autenticado']}")
                elif response.status_code == 401:
                    print("❌ Error de autenticación: Credenciales incorrectas")
                    USERNAME = PASSWORD = None  # Resetear credenciales
                else:
                    error = response.json()
                    print(f"❌ Error: {error.get('detail', 'Error desconocido')}")
            
            elif opc == 5:  # Eliminar libro (PROTEGIDO)
                # Solicitar credenciales si no están guardadas
                if not USERNAME or not PASSWORD:
                    USERNAME, PASSWORD = solicitar_credenciales()
                    if not USERNAME:  # Falló la autenticación
                        opc = menu()

                print("\nELIMINAR LIBRO")
                
                titulo = input("Ingrese el título del libro a eliminar: ").strip()
                if not titulo:
                    print("❌ Error: Debe ingresar un título")
                    continue
                
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
                    print(f"\n✅ {resultado.get('mensaje', 'Libro eliminado exitosamente')}")
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
        input("\nPresione ENTER para continuar...")
        opc = menu()
    
    print("\n" + "="*60)
    print("¡Gracias por usar la Biblioteca Online!")
    print("Hasta pronto")
    print("="*60)

if __name__ == "__main__":
    main()