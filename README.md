# Food Store — Sistema de Gestión de Pedidos de Comida

Trabajo Práctico Integrador — Programación 4  
Tecnicatura Universitaria en Programación

---

## Integrantes

> Completar los datos faltantes antes de entregar.

| Integrante | GitHub |
|---|---:|---|---|
| Lucas Pujada | https://github.com/Luceba1 |
| Gianfranco Canciani |
| Julio Leiva |
| Bruno Rivera |

---

## Videos de entrega

| Instancia | Link de YouTube | Observaciones |
|---|---|---|
| Video Parcial 1 | Pegar link acá | Completar |
| Video Parcial 2 | Pegar link acá | Completar |
| Video Final TPI | Pegar link acá | Completar |

---

## Descripción del proyecto

Food Store es una aplicación web full-stack para la gestión integral de pedidos de comida.

Permite que los clientes naveguen un catálogo, agreguen productos al carrito, creen pedidos, paguen mediante MercadoPago y sigan el estado del pedido en tiempo real mediante WebSocket.

Desde el panel administrador se puede gestionar productos, categorías, ingredientes, unidades de medida, imágenes, usuarios, pedidos, stock, estadísticas, dashboard y exportaciones.

---

## Tecnologías utilizadas

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Axios
- Zustand
- TanStack Query
- React Router
- Recharts

### Backend

- FastAPI
- SQLModel
- PostgreSQL
- JWT
- Passlib / bcrypt
- Unit of Work
- Repository Pattern
- WebSocket
- Cloudinary SDK
- MercadoPago SDK
- Pytest

### Integraciones externas

- Cloudinary para imágenes de productos y categorías.
- MercadoPago Checkout Pro para pagos.
- Ngrok para recibir webhooks de MercadoPago en entorno local.
- WebSocket para actualizaciones de pedidos en tiempo real.

---

## Funcionalidades principales

### Autenticación y autorización

- Registro de usuarios.
- Login con JWT.
- Access token.
- Refresh token de 7 días.
- Logout con revocación de refresh token.
- Roles:
  - ADMIN
  - STOCK
  - PEDIDOS
  - CLIENT
- Rate limiting en login/register: 5 intentos fallidos por IP en 15 minutos.

### Catálogo y stock

- CRUD de productos.
- Productos con múltiples imágenes.
- Categorías jerárquicas.
- Ingredientes con stock.
- Ingredientes marcados como alérgenos.
- Unidades de medida.
- Receta por producto.
- Stock calculado/descontado por ingredientes.
- Baja lógica y reactivación.
- Exportación a Excel.

### Cloudinary

- Upload de imágenes.
- Validación de tipo MIME.
- Validación de tamaño.
- Eliminación por `public_id`.
- Almacenamiento de URL segura en productos y categorías.

### Carrito

- Carrito implementado con Zustand.
- Persistencia con localStorage.
- Ícono de carrito con contador.
- Vista para modificar cantidades y confirmar pedido.

### Pedidos

Estados del pedido:

- PENDIENTE
- CONFIRMADO
- EN_PREP
- ENTREGADO
- CANCELADO

Funciones principales:

- Creación de pedidos desde carrito.
- Historial de estados append-only.
- Snapshot de nombre, precio y subtotal al crear el pedido.
- Descuento de stock por ingredientes.
- Cancelación con recuperación de ingredientes al stock cuando corresponde.
- Notificación por WebSocket después del commit exitoso.

### MercadoPago

- Creación de preferencia de pago.
- Checkout Pro.
- Webhook de confirmación.
- Redirect de éxito, fallo y pendiente.
- Confirmación automática del pedido.
- Registro de estado del pago.
- Idempotency key enviada a MercadoPago mediante header `x-idempotency-key`.
- Integración con Ngrok para pruebas locales.

### WebSocket

- Canal para cliente.
- Canal para administrador.
- Canal por pedido.
- Broadcast de cambios de estado.
- Actualización en tiempo real sin polling.
- Reconexión automática desde frontend.
- Payload con `event`, `pedido_id`, `estado_anterior`, `estado_nuevo`, `usuario_id`, `motivo` y `timestamp`.

### Estadísticas y dashboard

- Dashboard administrativo con KPIs y gráficos Recharts.
- Endpoints protegidos por rol ADMIN.
- Gráficos y métricas:
  - Ventas de los últimos días.
  - Pedidos por estado.
  - Ventas por forma de pago.
  - Top productos vendidos.
  - Alertas de stock bajo.
  - Ticket promedio.
  - Pagos aprobados/rechazados.

---

## Estructura del proyecto

```txt
backend/
  app/
    core/
    db/
    models/
    repositories/
    routers/
    schemas/
    services/
    uow/
  tests/
  requirements.txt
  pytest.ini
  .env.example

frontend/
  src/
    components/
    hooks/
    pages/
    services/
    stores/
    types/
  package.json
  package-lock.json
  .env.example
```

---

## Requisitos previos

Antes de ejecutar el proyecto, instalar:

- Python 3.10 o superior.
- Node.js 20 LTS o superior.
- PostgreSQL 15 o superior.
- Git.
- Ngrok, si se va a probar MercadoPago con webhook local.
- Cuenta de Cloudinary, si se va a probar subida de imágenes.
- Cuenta de MercadoPago Developers, si se va a probar pago real/sandbox.

Verificar versiones en CMD:

```cmd
python --version
node --version
npm --version
psql --version
```

Si `python` no funciona en Windows, probar:

```cmd
py --version
```

---

# Ejecución del proyecto en Windows

Las instrucciones siguientes están pensadas para ejecutarse desde CMD o terminal de VS Code.

## 1. Clonar o abrir el proyecto

Si se trabaja desde GitHub:

```cmd
git clone https://github.com/Luceba1/Integrador_Espejo_Prog4.git
cd Integrador_Espejo_Prog4
```

Si ya se descargó el ZIP, descomprimirlo y entrar a la carpeta raíz del proyecto.

---

## 2. Crear la base de datos PostgreSQL

El backend necesita una base de datos PostgreSQL creada antes de ejecutar el seed.

Nombre recomendado:

```txt
parcial_catalogo
```

Opción A — Crear desde pgAdmin:

1. Abrir pgAdmin.
2. Conectarse al servidor local.
3. Click derecho en `Databases`.
4. Seleccionar `Create > Database`.
5. Nombre: `parcial_catalogo`.
6. Guardar.

Opción B — Crear desde CMD si `psql` está configurado:

```cmd
psql -U postgres -c "CREATE DATABASE parcial_catalogo;"
```

Si ya existe, PostgreSQL puede mostrar un error indicando que la base ya está creada. En ese caso se puede continuar.

---

## 3. Configurar y ejecutar backend

Entrar a backend:

```cmd
cd backend
```

Crear entorno virtual:

```cmd
python -m venv .venv
```

Si el comando anterior falla, probar:

```cmd
py -3.10 -m venv .venv
```

Activar entorno virtual:

```cmd
.\.venv\Scripts\activate
```

Instalar dependencias:

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Crear archivo `.env`:

```cmd
copy /Y .env.example .env
```

Abrir el `.env`:

```cmd
notepad .env
```

Configurar como mínimo estas variables:

```env
DATABASE_URL=postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/parcial_catalogo
APP_NAME=Parcial Integrador Sistema de Pedidos
SECRET_KEY=CAMBIAR_POR_UNA_CLAVE_SEGURA
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
AUTH_RATE_LIMIT_MAX_ATTEMPTS=5
AUTH_RATE_LIMIT_WINDOW_MINUTES=15
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SQL_ECHO=false
VITE_FRONTEND_URL=http://127.0.0.1:5173
VITE_API_URL=http://127.0.0.1:8000
```

Cambiar `TU_PASSWORD` por la contraseña real del usuario `postgres`.

Para generar una `SECRET_KEY` segura:

```cmd
python -c "import secrets; print(secrets.token_hex(32))"
```

Copiar el valor generado y pegarlo en `SECRET_KEY`.

Variables para Cloudinary:

```env
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
CLOUDINARY_FOLDER=food_store
```

Variables para MercadoPago:

```env
MP_ACCESS_TOKEN=TEST-tu-access-token-de-mercadopago
MP_PUBLIC_KEY=TEST-tu-public-key-de-mercadopago
NGROK_URL=https://tu-subdominio.ngrok-free.app
MP_WEBHOOK_URL=https://tu-subdominio.ngrok-free.app/api/v1/pagos/webhook
MP_WEBHOOK_SECRET=
```

Si todavía no se va a probar MercadoPago ni Cloudinary, se pueden dejar valores de prueba. Para probar pagos e imágenes de verdad, estas variables deben ser reales.

Ejecutar seed inicial:

```cmd
python -m app.db.seed
```

Este comando carga datos iniciales como roles, estados de pedido, formas de pago, unidades de medida y usuario administrador.

Levantar backend:

```cmd
uvicorn app.main:app --reload
```

Backend disponible en:

```txt
http://127.0.0.1:8000
```

Swagger:

```txt
http://127.0.0.1:8000/docs
```

Redoc:

```txt
http://127.0.0.1:8000/redoc
```

---

## 4. Configurar y ejecutar frontend

Abrir otra terminal desde la raíz del proyecto y entrar a frontend:

```cmd
cd frontend
```

Instalar dependencias usando el lockfile:

```cmd
npm ci
```

Si `npm ci` fallara por diferencias de versión de Node/npm, usar:

```cmd
npm install
```

Crear archivo `.env`:

```cmd
copy /Y .env.example .env
```

Abrir el `.env`:

```cmd
notepad .env
```

Configurar:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Validar build de frontend:

```cmd
npm run build
```

Levantar frontend:

```cmd
npm run dev -- --host 127.0.0.1
```

Frontend disponible en:

```txt
http://127.0.0.1:5173
```

---

## 5. Credenciales iniciales

Usuario administrador creado por seed:

```txt
Email: admin@parcial.com
Password: Admin1234
```

Con este usuario se puede entrar al panel administrador.

---

# Configuración de Ngrok para MercadoPago

MercadoPago necesita una URL pública para enviar el webhook al backend local.

Primero levantar backend:

```cmd
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

En otra terminal:

```cmd
ngrok http http://127.0.0.1:8000
```

Ngrok mostrará una URL parecida a:

```txt
https://abc123.ngrok-free.app
```

Copiar esa URL y configurar en `backend/.env`:

```env
NGROK_URL=https://abc123.ngrok-free.app
MP_WEBHOOK_URL=https://abc123.ngrok-free.app/api/v1/pagos/webhook
```

Después de cambiar `.env`, reiniciar backend.

En MercadoPago Developers, configurar también el webhook apuntando a:

```txt
https://abc123.ngrok-free.app/api/v1/pagos/webhook
```

Resultado esperado al pagar:

1. El cliente crea un pedido.
2. El backend crea una preferencia de MercadoPago.
3. El cliente paga en Checkout Pro.
4. MercadoPago llama al webhook del backend mediante Ngrok.
5. El pago se registra.
6. El pedido pasa a CONFIRMADO.
7. Se descuenta stock de ingredientes.
8. Se emite evento WebSocket.

---

# Tests

Los tests se ejecutan desde la carpeta backend.

```cmd
cd backend
.\.venv\Scripts\activate
pytest -q
```

Resultado esperado:

```txt
62 passed
```

También se puede ejecutar con más detalle:

```cmd
pytest -v
```

Validar sintaxis de backend:

```cmd
python -m compileall -q app tests
```

Tests incluidos:

- core
- db
- models
- repositories
- routers
- schemas
- services
- uow
- functional/auth
- functional/pedidos
- functional/pagos
- functional/estadisticas
- functional/uploads
- functional/websocket

---

# Flujo de prueba recomendado

Para verificar la aplicación completa:

1. Crear base de datos PostgreSQL.
2. Configurar `backend/.env`.
3. Ejecutar `python -m app.db.seed`.
4. Levantar backend.
5. Configurar `frontend/.env`.
6. Levantar frontend.
7. Iniciar sesión como admin.
8. Crear categoría.
9. Crear unidad de medida.
10. Crear ingrediente con stock.
11. Crear producto con imagen Cloudinary.
12. Asociar receta/ingredientes al producto.
13. Crear usuario cliente o registrarse desde frontend.
14. Iniciar sesión como cliente.
15. Agregar producto al carrito.
16. Crear pedido en efectivo.
17. Cambiar estado desde admin.
18. Ver actualización por WebSocket.
19. Crear pedido con MercadoPago.
20. Pagar con cuenta de prueba.
21. Confirmar que el pedido pasa a CONFIRMADO.
22. Confirmar descuento de stock.
23. Probar dashboard y estadísticas.
24. Probar exportación a Excel.
25. Ejecutar `pytest -q`.

---

# Solución de errores comunes

## Error: DATABASE_URL y SECRET_KEY faltantes

Mensaje posible:

```txt
ValidationError: DATABASE_URL Field required
ValidationError: SECRET_KEY Field required
```

Solución:

```cmd
cd backend
copy /Y .env.example .env
notepad .env
```

Completar `DATABASE_URL` y `SECRET_KEY`.

---

## Error: la base de datos no existe

Mensaje posible:

```txt
database "parcial_catalogo" does not exist
```

Solución: crear la base desde pgAdmin o ejecutar:

```cmd
psql -U postgres -c "CREATE DATABASE parcial_catalogo;"
```

---

## Error: contraseña incorrecta de PostgreSQL

Mensaje posible:

```txt
password authentication failed for user "postgres"
```

Solución: revisar la contraseña en `DATABASE_URL`:

```env
DATABASE_URL=postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/parcial_catalogo
```

---

## Error de CORS o sesión que se pierde

Usar siempre:

```txt
http://127.0.0.1:5173
http://127.0.0.1:8000
```

No mezclar `localhost` y `127.0.0.1` si se están usando cookies.

Verificar en `backend/.env`:

```env
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
VITE_FRONTEND_URL=http://127.0.0.1:5173
```

Verificar en `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

---

## Error: Docker Desktop / PostgreSQL no iniciado

Si PostgreSQL está instalado localmente, asegurarse de que el servicio esté iniciado.

Si PostgreSQL corre con Docker, abrir Docker Desktop antes de levantar la base.

---

## Error: MercadoPago no confirma el pedido

Revisar:

1. Backend levantado en `http://127.0.0.1:8000`.
2. Ngrok apuntando a `http://127.0.0.1:8000`.
3. `NGROK_URL` actualizado en `.env`.
4. `MP_WEBHOOK_URL` actualizado en `.env`.
5. Backend reiniciado después de cambiar `.env`.
6. Webhook configurado en MercadoPago Developers.
7. Usar cuentas de prueba de MercadoPago.

---

## Error: Cloudinary no sube imágenes

Revisar estas variables en `backend/.env`:

```env
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
CLOUDINARY_FOLDER=food_store
```

También verificar que el archivo sea imagen válida y no supere el tamaño permitido.

---

## Error: npm ci falla

Probar:

```cmd
npm install
```

Luego validar:

```cmd
npm run build
```

---

# Notas para entrega

No subir archivos sensibles o generados:

- `.env`
- `.venv`
- `node_modules`
- `dist`
- `__pycache__`
- archivos `.pyc`
- `.pytest_cache`

Sí subir:

- `.env.example`
- `requirements.txt`
- `package.json`
- `package-lock.json`
- `README.md`
- código fuente
- tests

---

# Comandos rápidos

Backend:

```cmd
cd backend
.\.venv\Scripts\activate
python -m app.db.seed
uvicorn app.main:app --reload
```

Frontend:

```cmd
cd frontend
npm run dev -- --host 127.0.0.1
```

Tests:

```cmd
cd backend
.\.venv\Scripts\activate
pytest -q
```

Build frontend:

```cmd
cd frontend
npm run build
```

---

# Estado final esperado

Backend funcionando:

```txt
http://127.0.0.1:8000
```

Swagger funcionando:

```txt
http://127.0.0.1:8000/docs
```

Frontend funcionando:

```txt
http://127.0.0.1:5173
```

Tests correctos:

```txt
62 passed
```
