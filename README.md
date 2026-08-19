# Sistema de Citas Médicas

Proyecto full-stack simple para gestionar citas médicas con tres roles: paciente, médico y administrador.

## Funciones

### Paciente
- Registro e inicio de sesión.
- Buscar médicos por especialidad.
- Ver horarios disponibles.
- Reservar una cita.
- Ver historial de citas.
- Cancelar citas pendientes.

### Médico
- Iniciar sesión.
- Crear y consultar sus horarios disponibles.
- Ver sus citas.
- Marcar una cita como completada o cancelada.

### Administrador
- Iniciar sesión.
- Ver y activar/desactivar usuarios.
- Crear y modificar especialidades.
- Crear y modificar médicos.

## Tecnologías

- Frontend: React + TypeScript + Vite.
- Backend: FastAPI + SQLAlchemy.
- Base de datos: PostgreSQL.
- Migraciones: Alembic.
- Autenticación: JWT y contraseñas con hash Argon2.
- Contenedores: Docker + Docker Compose.
- CI: GitHub Actions.

## Forma más simple de iniciar todo

1. Copia `.env.example` como `.env` si quieres cambiar las variables. Para una prueba local también funcionan los valores por defecto del `docker-compose.yml`.
2. Desde la raíz ejecuta:

```bash
docker compose up --build
```

3. Abre:

- Aplicación: http://localhost:3000
- Swagger / API: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Docker levanta PostgreSQL, aplica las migraciones, carga datos demo, inicia FastAPI y sirve el frontend.

## Cuentas demo

Si `SEED_DEMO_DATA=true`:

- Admin: `admin@example.com` / `Admin1234!`
- Médico: `doctor@example.com` / `Doctor123!`
- Paciente: `patient@example.com` / `Patient123!`

También se crean tres especialidades y horarios futuros para la cuenta de médico demo.

Estas contraseñas son solo para desarrollo local. En un despliegue real deben cambiarse.

## Inicio manual para desarrollo

### Base de datos

```bash
docker compose up -d db
```

### Backend

```bash
cd backend
pip install -r requirements-dev.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

### Frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Estructura principal

```text
backend/
  app/
    models/       modelos de base de datos
    routers/      endpoints
    main.py       aplicación FastAPI
    security.py   hashes y JWT
    schemas.py    datos de entrada y salida
    seed.py       datos de prueba
  migrations/     migraciones Alembic
  tests/          pruebas básicas

frontend/
  src/
    App.tsx       interfaz simple para los tres roles

.github/workflows/
  ci.yml          pruebas y build automáticos
```

## Evitar reservas duplicadas

Cada cita utiliza un `slot_id` único en la tabla `appointments`. Además, al reservar se bloquea temporalmente la fila del horario antes de guardar. Así la base de datos impide que dos pacientes terminen reservando el mismo horario incluso si las peticiones llegan casi al mismo tiempo.

## API principal

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /specialties`
- `GET /doctors`
- `GET /doctors/{doctor_id}/availability`
- `POST /appointments`
- `GET /appointments/me`
- `POST /appointments/{id}/cancel`
- `GET/POST /doctor/slots`
- `GET /doctor/appointments`
- `PATCH /doctor/appointments/{id}`
- `/admin/*` para usuarios, especialidades y médicos

## CI

GitHub Actions comprueba en cada push o pull request:

- que el backend compila;
- las pruebas básicas de autenticación y health check;
- que el frontend TypeScript puede construirse correctamente.
