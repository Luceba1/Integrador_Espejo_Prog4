# Checklist final TPI v6 / ERD v7

## Prioridades marcadas por el profesor

- [x] Cloudinary: upload de imágenes.
- [x] Cloudinary: destroy por `public_id`.
- [x] Cloudinary: validación MIME y límite de tamaño.
- [x] Cloudinary: `imagenes_url[]` en Producto e `imagen_url` en Categoría.
- [x] WebSocket: WSManager con pool de conexiones.
- [x] WebSocket: canales admin, usuario y pedido puntual.
- [x] WebSocket: autenticación por cookie HttpOnly o `?token=`.
- [x] WebSocket: reconexión frontend e invalidación de queries.
- [x] Ngrok: `NGROK_URL` para back_urls HTTPS.
- [x] Ngrok: `MP_WEBHOOK_URL` para webhooks locales.
- [x] Tests: suite pytest por capas.
- [x] Tests: core, db, models, repositories, routers, schemas, services y uow.
- [x] MercadoPago: Checkout Pro.
- [x] MercadoPago: creación de preferencia.
- [x] MercadoPago: webhook `topic/type=payment`.
- [x] MercadoPago: redirect success/failure/pending.
- [x] MercadoPago: confirmación y actualización de pedido.
- [x] MercadoPago: `idempotency_key`, `transaction_amount`, `mp_status_detail`.

## Backend

- [x] FastAPI + SQLModel + PostgreSQL.
- [x] Arquitectura por capas: core, db, models, repositories, routers, schemas, services, uow.
- [x] Flujo Router → Service → UoW → Repository → Model.
- [x] CORS con credenciales.
- [x] JWT access token 30 minutos.
- [x] Refresh token 7 días, hasheado y revocable.
- [x] Rate limiting 5 intentos fallidos / 15 minutos.
- [x] RBAC ADMIN/STOCK/PEDIDOS/CLIENT.
- [x] Seed obligatorio: roles, estados, formas de pago, unidades y admin.
- [x] Categorías jerárquicas.
- [x] Productos con imágenes Cloudinary, unidad de venta y receta.
- [x] Ingredientes con stock, unidad y alérgenos.
- [x] Pedido con snapshot, total, subtotal, descuento y costo de envío.
- [x] Historial append-only.
- [x] FSM de 5 estados sin EN_CAMINO.
- [x] Soft delete y reactivación.
- [x] Exportación Excel.
- [x] Handlers de error con `detail`, `code`, `field`.
- [x] Headers `X-Request-ID` y `X-Process-Time`.
- [x] Swagger `/docs` y ReDoc `/redoc`.

## Frontend

- [x] React + TypeScript + Vite.
- [x] Tailwind CSS.
- [x] Axios centralizado con interceptors.
- [x] TanStack Query para fetch/mutations.
- [x] Zustand + localStorage para carrito.
- [x] Zustand para estado WebSocket.
- [x] Store pública, carrito, checkout y mis pedidos.
- [x] Panel admin para usuarios, categorías, ingredientes, unidades, productos y pedidos.
- [x] Botón sutil de carrito con contador.
- [x] Eliminados visualmente apagados.
- [x] Cancelación admin con popup para decidir recuperación de ingredientes.

## Validación recomendada

- [ ] `python -m compileall -q app tests`
- [ ] `pytest`
- [ ] `npm install`
- [ ] `npm run build`
- [ ] Demo completa con Cloudinary + MercadoPago + Ngrok + WebSocket.

## Corrección final contra TPI v6

- [x] Se agregó `.gitignore` raíz para evitar subir `.env`, `.venv`, `node_modules`, `dist`, cachés y archivos compilados.
- [x] Se mejoró el dashboard administrativo con KPIs, tendencia semanal, pedidos por estado, ventas por forma de pago, top productos y alertas de stock bajo.
- [x] Se amplió el endpoint `GET /api/v1/admin/dashboard` para alimentar gráficos comerciales, operativos, pagos y stock.
- [x] Se agregó alias TPI `GET /api/v1/productos/{id}/ingredientes`.
- [x] Se agregó alias TPI `POST /api/v1/productos/{id}/ingredientes`.
- [x] Se agregó alias TPI `PATCH /api/v1/productos/{id}/imagenes`.
- [x] Se agregó alias TPI `GET /api/v1/pagos/{pedido_id}`.
- [x] Se agregó alias TPI `DELETE /api/v1/pedidos/{id}` para cancelación propia.

## Corrección ampliada final contra TPI v6

- [x] Módulo estadísticas ADMIN con 5 endpoints TPI: resumen, ventas, productos-top, pedidos-por-estado e ingresos.
- [x] Dashboard frontend con Recharts: AreaChart, BarChart y PieChart.
- [x] `recharts` agregado a `package.json` y `package-lock.json`.
- [x] Eventos WebSocket normalizados al contrato TPI: `estado_nuevo`, `estado_anterior`, `motivo` y `timestamp`.
- [x] Invalidación TanStack Query corregida para refrescar dashboard tras eventos WS.
- [x] Stores Zustand separados: carrito, sesión, pagos, WebSocket y UI.
- [x] `pytest.ini` ajustado para evitar warning de pytest-asyncio.
- [x] `npm run build` validado correctamente.
- [x] `pytest -q` validado correctamente: 56 tests passing.
