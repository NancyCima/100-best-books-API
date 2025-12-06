# Proyecto Final - Redes de Datos
## Arquitectura Cliente-Servidor1-Servidor2

### 📋 Descripción
Sistema de biblioteca online con arquitectura de tres capas:
- **Cliente**: Interfaz CLI para gestionar libros
- **Servidor 1 (Gateway)**: Autenticación, rate limiting y proxy
- **Servidor 2 (Datos)**: Almacenamiento y gestión del JSON

---

### 🏗️ Arquitectura

```
┌──────────┐         ┌────────────┐         ┌────────────┐
│ CLIENTE  │ ◄─────► │ SERVIDOR 1 │ ◄─────► │ SERVIDOR 2 │
│   CLI    │  :8000  │  Gateway   │  :9000  │   Datos    │
└──────────┘         └────────────┘         └────────────┘
```

---

### 🚀 Inicio Rápido

#### 1. Servidor 2 (Datos)
```bash
cd servidor2
pip install -r requirements.txt
uvicorn main:app --port 9000
```

#### 2. Servidor 1 (Gateway)
```bash
cd servidor1
pip install -r requirements.txt
uvicorn main:app --port 8000
```

#### 3. Cliente
```bash
cd cliente
pip install requests
python main.py
```

---

### 🔒 Seguridad

**Autenticación Basic HTTP** (solo POST y DELETE):
- Usuario: `admin`
- Contraseña: `redes2025`

**Rate Limiting**:
- GET: 10-20 solicitudes/segundo
- POST/DELETE: 5 solicitudes/segundo

---

### 📁 Archivos

```
proyecto/
├── servidor1/
│   ├── main.py              # Gateway con seguridad
│   └── requirements.txt
├── servidor2/
│   ├── main.py              # Gestión de datos
│   ├── requirements.txt
│   └── data/
│       └── copybooks.json   # Base de datos
└── cliente/
    ├── main.py              # Interfaz usuario
    └── requirements.txt
```