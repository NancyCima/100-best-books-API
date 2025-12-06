"""
SERVIDOR 1 - Gateway/Proxy
Versión con rate limiting manual (sin slowapi)
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List
import secrets
import requests
import time
from collections import defaultdict

# Configuración del Servidor 2 (datos)
SERVIDOR2_URL = "http://localhost:9000"

app = FastAPI()

# Autenticación Basic
security = HTTPBasic()
USERNAME = "admin"
PASSWORD = "redes2025"

# Rate limiting manual - simple pero efectivo
request_counts = defaultdict(list)
RATE_LIMIT = 2  # requests
RATE_WINDOW = 5  # segundo

def check_rate_limit(client_ip: str):
    """Verifica si el cliente ha excedido el límite de requests"""
    now = time.time()
    
    # Limpiar requests antiguos (fuera de la ventana de tiempo)
    request_counts[client_ip] = [
        timestamp for timestamp in request_counts[client_ip]
        if now - timestamp < RATE_WINDOW
    ]
    
    # Verificar si excede el límite
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {RATE_LIMIT} per {RATE_WINDOW} second"
        )
    
    # Registrar este request
    request_counts[client_ip].append(now)

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

@app.get("/")
def bienvenida(request: Request):
    """Endpoint raíz con información del sistema"""
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
            "info": "Use /docs para ver la documentación"
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Servidor de datos no disponible: {str(e)}"
        )

@app.get("/libros/")
def get_filtrar_libros(
    request: Request,
    autor: str = None,
    idioma: str = None,
    pais: str = None,
    anioMin: int = None,
    anioMax: int = None
) -> List[dict]:
    """Filtra libros (proxy a Servidor 2)"""
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
    """Obtiene un libro (proxy a Servidor 2)"""
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

@app.post("/libros/{titulo}")
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
    client_ip = request.client.host
    check_rate_limit(client_ip)  # RATE LIMITING
    
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

@app.delete("/libros/{titulo}")
def eliminar_libro(
    request: Request,
    titulo: str,
    username: str = Depends(verificar_credenciales)  # AUTENTICACIÓN
):
    """Elimina libro (proxy a Servidor 2) - REQUIERE AUTENTICACIÓN"""
    client_ip = request.client.host
    check_rate_limit(client_ip)  # RATE LIMITING
    
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