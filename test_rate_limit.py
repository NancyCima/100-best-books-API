"""
Prueba de rate limit
"""
import requests
import time
import threading
from datetime import datetime

def print_timestamped(msg):
    """Imprime mensaje con timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {msg}")

def test_rate_limit_rapido(url="http://localhost:8000/"):
    """
    Prueba el rate limit con requests simultáneos
    usando threads para evitar que el tiempo de respuesta afecte
    """
    print("TEST 1: Requests simultáneos para probar rate limit")
    print("="*60)
    
    results = []
    threads = []
    
    def make_request(i):
        """Hace un request y guarda el resultado"""
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start
            
            results.append({
                'num': i,
                'status': response.status_code,
                'elapsed': elapsed,
                'time': time.time()
            })
            
            if response.status_code == 200:
                print_timestamped(f"✅ Request {i}: 200 OK (took {elapsed:.3f}s)")
            elif response.status_code == 429:
                print_timestamped(f"🚫 Request {i}: 429 RATE LIMITED!")
                try:
                    detail = response.json().get('detail', '')
                    print(f"   └─ {detail}")
                except:
                    pass
            else:
                print_timestamped(f"⚠️  Request {i}: {response.status_code}")
                
        except Exception as e:
            print_timestamped(f"❌ Request {i}: ERROR - {e}")
            results.append({
                'num': i,
                'status': 'ERROR',
                'elapsed': 0,
                'error': str(e)
            })
    
    print(" Lanzando 15 requests casi simultáneos...\n")
    start_time = time.time()
    
    for i in range(1, 6):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()
        time.sleep(0.01)  # Delay mínimo entre threads
    
    # Esperar a que todos terminen
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    
    # Análisis de resultados
    print("\n" + "="*60)
    print(" ANÁLISIS:")
    success = sum(1 for r in results if r['status'] == 200)
    limited = sum(1 for r in results if r['status'] == 429)
    
    print(f"   ✅ Exitosos (200): {success}")
    print(f"   🚫 Rate Limited (429): {limited}")
    print(f"   Tiempo total: {total_time:.2f}s")
    
    if limited >= 3:
        print("\n✅ RATE LIMIT FUNCIONANDO CORRECTAMENTE")
    else:
        print("\n❌ RATE LIMIT NO ESTÁ FUNCIONANDO")
        print("   (Se esperaban al menos 3 requests con 429)")
    
    return results

def test_rate_limit_secuencial(url="http://localhost:8000/"):
    """
    Prueba básica secuencial - útil para debug
    """
    print("\n\n TEST 2: Requests secuenciales rápidos")
    print("="*60)
    
    for i in range(1, 6):
        try:
            start = time.time()
            print_timestamped(f"Enviando request {i}...")
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start
            
            if response.status_code == 200:
                print_timestamped(f"  ✅ 200 OK (took {elapsed:.3f}s)")
            elif response.status_code == 429:
                print_timestamped(f"  🚫 429 RATE LIMITED")
                try:
                    detail = response.json().get('detail', '')
                    print(f"{detail}")
                except:
                    pass
            else:
                print_timestamped(f"⚠️  {response.status_code}")
                
        except Exception as e:
            print_timestamped(f"❌ ERROR: {e}")
        
        # Pequeño delay entre requests
        if i < 5:
            time.sleep(0.2)

def test_rate_limit_reset(url="http://localhost:8000/"):
    """
    Verifica que el rate limit se resetee después de 15 segundos
    """
    print("\n\nTEST 3: Verificar reset después de 15 segundos")
    print("="*60)
    
    print("Fase 1: Hacer 3 requests rápidos")
    count_429 = 0
    for i in range(1, 4):
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"  Request {i}: ✅ 200 OK")
        else:
            print(f"  Request {i}: 🚫 429 RATE LIMITED")
            count_429 += 1
        time.sleep(0.1)
    
    if count_429 > 0:
        print(f"\n✅ Rate limit activado ({count_429} requests bloqueados)")
    else:
        print("\n⚠️  Ningún request fue bloqueado en la fase 1")
    
    print("\nEsperando 16 segundos para reset...")
    time.sleep(16)
    
    print("\nFase 2: Hacer 2 requests después del reset")
    success_after_reset = 0
    for i in range(1, 3):
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"  Request {i}: ✅ 200 OK")
            success_after_reset += 1
        else:
            print(f"  Request {i}: 🚫 429 RATE LIMITED")
        time.sleep(0.1)
    
    if success_after_reset == 2:
        print("\n✅ RESET FUNCIONA CORRECTAMENTE")
    else:
        print("\n❌ RESET NO FUNCIONÓ COMO ESPERADO")

def check_server(url="http://localhost:8000/"):
    """Verifica que el servidor esté respondiendo rápido"""
    print("Verificando servidor...")
    print("="*60)
    
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start
        
        print(f"✅ Servidor responde en {elapsed:.3f}s")
        
        if elapsed > 1.0:
            print("⚠️  ADVERTENCIA: El servidor está tardando mucho (>1s)")
            print("   Esto puede afectar las pruebas de rate limit.")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: No se puede conectar al servidor")
        print(f"   {e}")
        return False

if __name__ == "__main__":
    # Verificar servidor primero
    if not check_server():
        print("\n⚠️  Considera iniciar el Servidor 2 antes de continuar")
        print("   O las pruebas pueden dar falsos positivos debido a timeouts")
        print()
    
    # Test principal con threads
    test_rate_limit_rapido()
    
    # Esperar un poco entre tests
    print("\nEsperando 16 segundos antes del siguiente test...")
    time.sleep(16)
    
    # Test secuencial
    test_rate_limit_secuencial()
    
    # Esperar antes del último test
    print("\nEsperando 16 segundos antes del test final...")
    time.sleep(16)
    
    # Test de reset
    test_rate_limit_reset()
    
    print("\n" + "="*60)
    print("PRUEBAS COMPLETADAS")
    print("="*60)