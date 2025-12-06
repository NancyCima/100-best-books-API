"""
SERVIDOR 1 - Gateway/Proxy
API intermedia con autenticación y rate limiting
Reenvía peticiones a Servidor 2 (datos)
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import secrets
import requests

# Configuración del Servidor 2 (datos)
SERVIDOR2_URL = "http://localhost:9000"  # Puerto diferente

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Autenticación Basic
security = HTTPBasic()
USERNAME = "admin"
PASSWORD = "redes2025"

def verificar_credenciales(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifica credenciales para POST y DELETE"""
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# ENDPOINTS - Actúan como proxy hacia Servidor 2

@app.get("/")
@limiter.limit("10/second")
def bienvenida(request: Request):
    """Endpoint raíz con información del sistema"""
    try:
        # Consultar estado de Servidor 2
        response = requests.get(f"{SERVIDOR2_URL}/", timeout=5)
        servidor2_info = response.json()
        
        return {
            "mensaje": "Bienvenido a la Biblioteca Online",
            "servidor": "Servidor 1 - Gateway",
            "cantidad_libros": servidor2_info.get("cantidad_libros", 0),
            "servidor_datos": "activo",
            "info": "Use /docs para ver la documentación"
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Servidor de datos no disponible: {str(e)}"
        )

@app.get("/libros/")
@limiter.limit("20/second")
def get_filtrar_libros(
    request: Request,
    autor: str = None,
    idioma: str = None,
    pais: str = None,
    anioMin: int = None,
    anioMax: int = None
) -> List[dict]:
    """Filtra libros (proxy a Servidor 2)"""
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
@limiter.limit("20/second")
def get_libro(request: Request, titulo: str) -> dict:
    """Obtiene un libro (proxy a Servidor 2)"""
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

@app.post("/libros/{titulo}")
@limiter.limit("5/second")
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
    username: str = Depends(verificar_credenciales)  # AUTENTICACIÓN
):
    """Agrega libro (proxy a Servidor 2) - REQUIERE AUTENTICACIÓN"""
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
            resultado['usuario_autenticado'] = username
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

@app.put("/libros/{titulo}")
@limiter.limit("10/second")
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
    """Actualiza libro (proxy a Servidor 2)"""
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

@app.delete("/libros/{titulo}")
@limiter.limit("5/second")
def eliminar_libro(
    request: Request,
    titulo: str,
    username: str = Depends(verificar_credenciales)  # AUTENTICACIÓN
):
    """Elimina libro (proxy a Servidor 2) - REQUIERE AUTENTICACIÓN"""
    try:
        response = requests.delete(f"{SERVIDOR2_URL}/libros/{titulo}", timeout=5)
        
        if response.status_code == 200:
            resultado = response.json()
            resultado['usuario_autenticado'] = username
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
