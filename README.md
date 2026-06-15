# Food Store — Sistema de Gestión de Pedidos de Comida

Trabajo Práctico Integrador — Programación 4
Tecnicatura Universitaria en Programación

## Descripción

Food Store es una aplicación web full-stack para la gestión integral de pedidos de comida.

Permite que los clientes naveguen un catálogo, agreguen productos al carrito, realicen pedidos, paguen mediante MercadoPago y sigan el estado del pedido en tiempo real mediante WebSocket.

El administrador puede gestionar productos, categorías, ingredientes, unidades de medida, imágenes, usuarios, pedidos, stock y exportaciones desde un panel centralizado.

## Tecnologías utilizadas

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Axios
* Zustand
* TanStack Query
* React Router
* Recharts

### Backend

* FastAPI
* SQLModel
* PostgreSQL
* JWT
* Passlib / bcrypt
* Unit of Work
* Repository Pattern
* WebSocket
* Cloudinary SDK
* MercadoPago SDK
* Pytest

### Integraciones

* Cloudinary para imágenes de productos y categorías.
* MercadoPago Checkout Pro para pagos.
* Ngrok para recibir webhooks de MercadoPago en entorno local.
* WebSocket para actualización en tiempo real de pedidos.

## Funcionalidades principales

### Autenticación y autorización

* Registro de usuarios.
* Login con JWT.
* Access token.
* Refresh token de 7 días.
* Logout con revocación de refresh token.
* Roles:

  * ADMIN
  * STOCK
  * PEDIDOS
  * CLIENT
* Rate limiting en login/register: 5 intentos fallidos por IP en 15 minutos.

### Catálogo

* CRUD de productos.
* Productos con múltiples imágenes.
* Categorías jerárquicas.
* Ingredientes con stock.
* Ingredientes marcados como alérgenos.
* Unidades de medida.
* Receta por producto.
* Baja lógica y reactivación.
* Exportación a Excel.

### Cloudinary

* Upload de imágenes.
* Validación de tipo MIME.
* Validación de tamaño.
* Eliminación por public_id.
* Almacenamiento de URL segura en productos y categorías.

### Carrito

* Carrito implementado con Zustand.
* Persistencia con localStorage.
* Ícono de carrito con contador.
* Vista completa para modificar cantidades y confirmar pedido.

### Pedidos

* Creación de pedidos desde carrito.
* Estados del pedido:

  * PENDIENTE
  * CONFIRMADO
  * EN_PREP
  * ENTREGADO
  * CANCELADO
* Historial de estados append-only.
* Snapshot de precio y nombre al crear el pedido.
* Descuento de stock por ingredientes.
* Cancelación con opción de recuperar ingredientes al stock desde admin.

### MercadoPago

* Creación de preferencia de pago.
* Checkout Pro.
* Webhook de confirmación.
* Redirect de éxito.
* Confirmación automática del pedido.
* Registro de estado del pago.
* Idempotency key.
* Integración con Ngrok para pruebas locales.

### WebSocket

* Canal para cliente.
* Canal para administrador.
* Canal por pedido.
* Broadcast de cambios de estado.
* Actualización en tiempo real sin polling.
* Reconexión automática desde frontend.
* Payload compatible con TPI: `event`, `pedido_id`, `estado_anterior`, `estado_nuevo`, `usuario_id`, `motivo` y `timestamp`.


### Estadísticas y dashboard

* Módulo `/api/v1/estadisticas` protegido por rol ADMIN.
* Endpoints:

  * `GET /api/v1/estadisticas/resumen`
  * `GET /api/v1/estadisticas/ventas`
  * `GET /api/v1/estadisticas/productos-top`
  * `GET /api/v1/estadisticas/pedidos-por-estado`
  * `GET /api/v1/estadisticas/ingresos`
* Dashboard administrativo con KPIs y gráficos Recharts:

  * Ventas de los últimos 7 días.
  * Pedidos por estado.
  * Ventas por forma de pago.
  * Top productos vendidos.
  * Alertas de stock bajo.

### Testing

Tests automatizados por capas y por módulos funcionales:

* core
* db
* models
* repositories
* routers
* schemas
* services
* uow
* functional/auth
* functional/pedidos
* functional/pagos
* functional/estadisticas
* functional/uploads
* functional/websocket

Ejemplo de ejecución:

```bash
pytest -v
```

Resultado esperado:

```txt
62 passed
```

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
  .env.example

frontend/
  src/
    api/
    components/
    hooks/
    pages/
    services/
    stores/
    types/
  package.json
  .env.example
```

## Requisitos previos

Tener instalado:

* Python 3.10+
* Node.js
* PostgreSQL
* Git
* Cuenta de Cloudinary
* Cuenta de MercadoPago Developers
* Ngrok

## Configuración del backend

Entrar a la carpeta backend:

```bash
cd backend
```

Crear entorno virtual:

```bash
python -m venv .venv
```

Activar entorno virtual en Windows:

```bash
.\.venv\Scripts\activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Crear archivo `.env` desde el ejemplo:

```bash
copy .env.example .env
```

Completar variables:

```env
DATABASE_URL=postgresql+psycopg://postgres:TU_PASSWORD@localhost:5432/parcial_catalogo

SECRET_KEY=clave_super_secreta
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

COOKIE_SECURE=false
COOKIE_SAMESITE=lax

BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
VITE_FRONTEND_URL=http://127.0.0.1:5173

CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
CLOUDINARY_FOLDER=food_store

MP_ACCESS_TOKEN=TEST-tu-access-token
MP_PUBLIC_KEY=TEST-tu-public-key
NGROK_URL=https://tu-url-ngrok.ngrok-free.app
MP_WEBHOOK_URL=https://tu-url-ngrok.ngrok-free.app/api/v1/pagos/webhook
```

Ejecutar seed:

```bash
python -m app.db.seed
```

Levantar backend:

```bash
uvicorn app.main:app --reload
```

Swagger:

```txt
http://127.0.0.1:8000/docs
```

Redoc:

```txt
http://127.0.0.1:8000/redoc
```

## Configuración del frontend

Entrar a la carpeta frontend:

```bash
cd frontend
```

Instalar dependencias:

```bash
npm install
```

Crear `.env` desde `.env.example`:

```bash
copy .env.example .env
```

Configurar:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Validar build:

```bash
npm run build
```

Levantar frontend:

```bash
npm run dev -- --host 127.0.0.1
```

Abrir:

```txt
http://127.0.0.1:5173
```

## Configuración de Ngrok para MercadoPago

Levantar backend local:

```bash
uvicorn app.main:app --reload
```

En otra terminal:

```bash
ngrok http http://127.0.0.1:8000
```

Copiar la URL HTTPS de Ngrok y configurar en backend `.env`:

```env
NGROK_URL=https://tu-url-ngrok.ngrok-free.app
MP_WEBHOOK_URL=https://tu-url-ngrok.ngrok-free.app/api/v1/pagos/webhook
```

Reiniciar backend.

Crear un pedido nuevo con MercadoPago y pagar con cuenta compradora de prueba.

Resultado esperado:

* MercadoPago aprueba pago.
* Webhook llega al backend.
* Pedido pasa a CONFIRMADO.
* Se descuenta stock de ingredientes.

## Credenciales iniciales

Usuario administrador:

```txt
Email: admin@parcial.com
Password: Admin1234
```

## Tests

Ejecutar desde backend:

```bash
pytest -v
```

También se puede validar sintaxis:

```bash
python -m compileall -q app tests
```

## Flujo de prueba recomendado

1. Levantar backend.
2. Levantar frontend.
3. Iniciar sesión como admin.
4. Crear categoría.
5. Crear unidad de medida.
6. Crear ingrediente con stock.
7. Crear producto con imagen Cloudinary.
8. Asociar receta al producto.
9. Iniciar sesión como cliente.
10. Agregar producto al carrito.
11. Crear pedido en efectivo.
12. Cambiar estado desde admin.
13. Ver actualización por WebSocket.
14. Crear pedido con MercadoPago.
15. Pagar con cuenta de prueba.
16. Confirmar que el pedido pasa a CONFIRMADO.
17. Confirmar descuento de stock.
18. Cancelar pedido y probar recuperación de ingredientes.
19. Ejecutar exportación a Excel.
20. Ejecutar tests.

## Notas de entrega

No subir archivos sensibles:

* `.env`
* `.venv`
* `node_modules`
* `dist`
* `__pycache__`
* archivos `.pyc`

Subir solamente `.env.example`.

## Correcciones finales de compatibilidad TPI v6

Esta versión suma endpoints y pantallas para quedar más alineada con la especificación técnica v6:

- Dashboard administrativo avanzado con KPIs, gráfico de tendencia de 7 días, pedidos por estado, ventas por forma de pago, top productos e ingredientes con stock crítico.
- `GET /api/v1/admin/dashboard` para alimentar el panel con métricas comerciales, operativas, pagos y stock.
- `GET /api/v1/productos/{id}/ingredientes` para listar receta/ingredientes de un producto.
- `POST /api/v1/productos/{id}/ingredientes` para asociar o actualizar un ingrediente de la receta.
- `PATCH /api/v1/productos/{id}/imagenes` para reemplazar la lista de imágenes Cloudinary del producto.
- `GET /api/v1/pagos/{pedido_id}` para consultar el pago asociado a un pedido.
- `DELETE /api/v1/pedidos/{id}` como alias de cancelación propia compatible con la especificación.

El código mantiene también los endpoints ya usados por el frontend para no romper compatibilidad.


## Correcciones finales de calidad

- Unit of Work: las operaciones que notifican por WebSocket ahora abren un bloque `with SQLModelUnitOfWork()`. El commit/rollback queda centralizado en el UoW y el broadcast se ejecuta recién después del commit exitoso.
- MercadoPago: la preferencia de pago se crea enviando la `idempotency_key` como header `x-idempotency-key` mediante `RequestOptions` del SDK, y esa misma clave queda guardada en la tabla `Pago`.
- Frontend: `package-lock.json` queda sincronizado con `package.json`, incluyendo `recharts` para el dashboard administrativo.
