"""
SERVIDOR 1 - Gateway/Proxy
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Dict
import secrets
import requests
import time
from collections import defaultdict

# Configuración del Servidor 2 (datos)
SERVIDOR2_URL = "http://localhost:9000"

app = FastAPI(
    title="Biblioteca Online - Gateway",
    description="API Gateway con autenticación Basic para gestión de biblioteca"
)

# AUTENTICACIÓN BASIC
security = HTTPBasic()

# Base de usuarios
USUARIOS: Dict[str, str] = {
    "admin": "redes2025"
}

def verificar_credenciales(
    credenciales: HTTPBasicCredentials = Depends(security)
) -> str:
    """
    Valida las credenciales enviadas por el cliente.
    
    - Usa secrets.compare_digest para evitar ataques de timing
    - Lanza HTTP 401 si usuario/contraseña no son correctos
    
    Returns:
        str: Nombre del usuario autenticado
    """
    pwd_correcta = USUARIOS.get(credenciales.username)
    
    # Validación segura contra timing attacks
    if not pwd_correcta or not secrets.compare_digest(
        credenciales.password, pwd_correcta
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credenciales.username

# RATE LIMITING
request_counts = defaultdict(list)
RATE_LIMIT = 2  # requests
RATE_WINDOW = 15  # segundos

def check_rate_limit(client_ip: str):
    """Verifica si el cliente ha excedido el límite de requests en la ventana de tiempo"""
    now = time.time()
    
    # Limpiar requests antiguos (fuera de la ventana de tiempo)
    request_counts[client_ip] = [
        timestamp for timestamp in request_counts[client_ip]
        if now - timestamp < RATE_WINDOW
    ]
    
    # Verificar límite
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        oldest_request = min(request_counts[client_ip])
        wait_time = RATE_WINDOW - (now - oldest_request)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit excedido: {RATE_LIMIT} requests por {RATE_WINDOW}s. "
                   f"Intenta en {wait_time:.1f}s"
        )
    
    # Registrar request
    request_counts[client_ip].append(now)

#  ENDPOINTS PÚBLICOS (SIN AUTENTICACIÓN)

@app.get("/")
def bienvenida(request: Request):
    """Endpoint raíz - acceso público"""
    client_ip = request.client.host
    check_rate_limit(client_ip)  # RATE LIMITING
    
    try:
        response = requests.get(f"{SERVIDOR2_URL}/", timeout=5)
        servidor2_info = response.json()
        
        return {
            "mensaje": "Bienvenido a la Biblioteca Online",
            "servidor": "Servidor 1 - Gateway",
            "cantidad_libros": servidor2_info.get("cantidad_libros", 0),
            "servidor_datos": "activo",
            "endpoints_publicos": ["/", "/libros/", "/libros/{titulo}"],
            "endpoints_protegidos": ["/libros/{titulo} (POST)", "/libros/{titulo} (DELETE)"],
            "info": "Use /docs para ver la documentación completa"
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Servidor de datos no disponible: {str(e)}"
        )

@app.get("/auth/test")
def test_auth(usuario: str = Depends(verificar_credenciales)):
    return {"mensaje": "Autenticación exitosa", "usuario": usuario}

@app.get("/libros/")
def get_filtrar_libros(
    request: Request,
    autor: str = None,
    idioma: str = None,
    pais: str = None,
    anioMin: int = None,
    anioMax: int = None
) -> List[dict]:
    """Filtra libros - acceso público"""
    client_ip = request.client.host
    check_rate_limit(client_ip)  # RATE LIMITING
    
    try:
        params = {}
        if autor: params['autor'] = autor
        if idioma: params['idioma'] = idioma
        if pais: params['pais'] = pais
        if anioMin: params['anioMin'] = anioMin
        if anioMax: params['anioMax'] = anioMax
        
        response = requests.get(f"{SERVIDOR2_URL}/libros/", params=params, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get('detail', 'Error en servidor de datos')
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error comunicando con servidor de datos: {str(e)}"
        )

@app.get("/libros/{titulo}")
def get_libro(request: Request, titulo: str) -> dict:
    """Obtiene un libro específico - acceso público"""
    client_ip = request.client.host
    check_rate_limit(client_ip)  # RATE LIMITING
    
    try:
        response = requests.get(f"{SERVIDOR2_URL}/libros/{titulo}", timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get('detail', 'Error en servidor de datos')
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error comunicando con servidor de datos: {str(e)}"
        )

@app.put("/libros/{titulo}")
def actualizar_libro(
    request: Request,
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
    """Actualiza libro - acceso público"""
    client_ip = request.client.host
    check_rate_limit(client_ip)  # RATE LIMITING
    
    try:
        params = {
            'tituloAct': tituloAct,
            'autor': autor,
            'idioma': idioma,
            'paginas': paginas,
            'pais': pais,
            'anio': anio
        }
        if imagen: params['imagen'] = imagen
        if link: params['link'] = link
        
        response = requests.put(
            f"{SERVIDOR2_URL}/libros/{titulo}",
            params=params,
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get('detail', 'Error en servidor de datos')
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error comunicando con servidor de datos: {str(e)}"
        )


# ENDPOINTS PROTEGIDOS (REQUIEREN AUTENTICACIÓN)

@app.post("/libros/")
def agregar_libro(
    request: Request,
    titulo: str,
    autor: str,
    idioma: str,
    paginas: int,
    pais: str,
    anio: int,
    imagen: str = None,
    link: str = None,
    usuario: str = Depends(verificar_credenciales)  # AUTENTICACIÓN REQUERIDA
):
    """
    Agrega un nuevo libro - REQUIERE AUTENTICACIÓN
    
    El parámetro 'usuario' contiene el nombre del usuario autenticado
    """
    client_ip = request.client.host
    check_rate_limit(client_ip)
    
    try:
        params = {
            'titulo': titulo,
            'autor': autor,
            'idioma': idioma,
            'paginas': paginas,
            'pais': pais,
            'anio': anio
        }
        if imagen: params['imagen'] = imagen
        if link: params['link'] = link
        
        response = requests.post(f"{SERVIDOR2_URL}/libros/", params=params, timeout=5)
        
        if response.status_code == 200:
            resultado = response.json()
            resultado['usuario_autenticado'] = usuario
            resultado['mensaje'] = f"✅ Libro agregado exitosamente por {usuario}"
            return resultado
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get('detail', 'Error en servidor de datos')
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error comunicando con servidor de datos: {str(e)}"
        )

@app.delete("/libros/{titulo}")
def eliminar_libro(
    request: Request,
    titulo: str,
    usuario: str = Depends(verificar_credenciales)  # AUTENTICACIÓN REQUERIDA
):
    """
    Elimina un libro - REQUIERE AUTENTICACIÓN
    
    El parámetro 'usuario' contiene el nombre del usuario autenticado
    """
    client_ip = request.client.host
    check_rate_limit(client_ip)  # RATE LIMITING
    
    try:
        response = requests.delete(f"{SERVIDOR2_URL}/libros/{titulo}", timeout=5)
        
        if response.status_code == 200:
            resultado = response.json()
            resultado['usuario_autenticado'] = usuario
            resultado['mensaje'] = f" Libro eliminado exitosamente por {usuario}"
            return resultado
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get('detail', 'Error en servidor de datos')
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error comunicando con servidor de datos: {str(e)}"
        )