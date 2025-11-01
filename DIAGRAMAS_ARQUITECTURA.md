# Diagramas de Arquitectura - Gestor de Finanzas Personales

## Diagrama de Clases

```
┌─────────────────────────────────────────────────────────────────┐
│                          User (Django)                          │
│  + username                                                     │
│  + email                                                        │
│  + password                                                     │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ 1
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                       UserProfile                               │
│  + user (ForeignKey -> User)                                    │
│  + is_admin                                                     │
│  + created_at                                                   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ 1
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
        │ *             │ *             │ *             │ *
        │               │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│ Transaction  │ │   Category   │ │     Tag     │ │   Budget    │
├──────────────┤ ├──────────────┤ ├─────────────┤ ├─────────────┤
│ + user       │ │ + user       │ │ + user      │ │ + user      │
│ + amount     │ │ + name       │ │ + name      │ │ + category  │
│ + description│ │ + type       │ │ + color     │ │ + amount    │
│ + date       │ │ + color      │ │             │ │ + month     │
│ + type       │ │ + icon       │ │             │ └─────────────┘
│ + category   │ └──────────────┘ └─────────────┘
│ + tags       │
│ + created_at │
└──────┬───────┘
       │
       │ *
       │
┌──────▼──────────────┐
│ RecurringTransaction│
├─────────────────────┤
│ + user              │
│ + name              │
│ + amount            │
│ + frequency         │
│ + next_occurrence   │
│ + is_active         │
└─────────────────────┘

┌──────────────────────┐
│   SavingsGoal        │
├──────────────────────┤
│ + user               │
│ + name               │
│ + target_amount      │
│ + current_amount     │
│ + target_date        │
│ + is_achieved        │
└──────────────────────┘
```

## Diagrama de Arquitectura (Capas)

```
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE PRESENTACIÓN                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Templates   │  │   Static     │  │   JavaScript │         │
│  │  (HTML)      │  │   (CSS/JS)   │  │   (Chart.js) │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP Request/Response
                            │
┌─────────────────────────────────────────────────────────────────┐
│                       CAPA DE CONTROL                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Views      │  │  Forms       │  │  API Views   │         │
│  │  (MVC)       │  │  (Validación)│  │  (REST API)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  - TransactionListView, CreateView, UpdateView, DeleteView     │
│  - CategoryListView, CreateView, UpdateView, DeleteView        │
│  - BudgetListView, CreateView, UpdateView, DeleteView          │
│  - DashboardView                                               │
│  - TransactionViewSet, CategoryViewSet, BudgetViewSet          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Business Logic
                            │
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE SERVICIOS                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Report       │  │  External    │  │  Exchange    │         │
│  │ Generators   │  │  Service     │  │  Rate        │         │
│  │ (DI Pattern) │  │  Consumer    │  │  Service     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  - ReportGenerator (Interface)                                 │
│    ├── PDFReportGenerator                                      │
│    └── ExcelReportGenerator                                    │
│  - ExternalServiceConsumer                                     │
│  - ExchangeRateService                                         │
│  - FreeWeatherService                                          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Data Access
                            │
┌─────────────────────────────────────────────────────────────────┐
│                      CAPA DE DATOS                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Models     │  │  Serializers │  │  Managers    │         │
│  │  (ORM)       │  │  (REST API)  │  │  (Queries)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  - Transaction, Category, Tag, Budget                           │
│  - SavingsGoal, RecurringTransaction                           │
│  - UserProfile                                                 │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ SQL Queries
                            │
┌─────────────────────────────────────────────────────────────────┐
│                      BASE DE DATOS                              │
│  ┌──────────────┐  ┌──────────────┐                           │
│  │   SQLite     │  │  PostgreSQL  │                           │
│  │ (Desarrollo) │  │ (Producción) │                           │
│  └──────────────┘  └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## Comunicación con Aplicaciones Externas

```
┌─────────────────────────────────────────────────────────────────┐
│                    APLICACIÓN PRINCIPAL                         │
│                  (Gestor de Finanzas)                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Servicios Externos (Consumo)                        │      │
│  │  - ExchangeRateService → exchangerate-api.com        │      │
│  │  - FreeWeatherService → wttr.in                      │      │
│  │  - ExternalServiceConsumer → Equipo Precedente       │      │
│  └──────────────────────────────────────────────────────┘      │
│                            │                                    │
│                            │ HTTP/HTTPS                         │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  API REST (Provisión)                                │      │
│  │  - /api/transactions/                                │      │
│  │  - /api/categories/                                  │      │
│  │  - /api/budgets/                                     │      │
│  │  - /api/savings-goals/                               │      │
│  │                                                      │      │
│  │  Formato: JSON                                       │      │
│  │  Autenticación: SessionAuthentication                │      │
│  └──────────────────────────────────────────────────────┘      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS (JSON)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Equipo       │   │ Aplicaciones │   │ Aplicaciones │
│ Siguiente    │   │ de Terceros  │   │ de Usuario   │
│ (Consume     │   │ (APIs        │   │ (Frontend,   │
│  nuestra API)│   │  Públicas)   │   │  Mobile)     │
└──────────────┘   └──────────────┘   └──────────────┘
```

## Patrón de Inversión de Dependencias (DI)

```
┌─────────────────────────────────────────────────────────────────┐
│                      ReportGenerator                            │
│                    (Interface - ABC)                            │
│                                                                 │
│  + generate(queryset, filename) -> HttpResponse                 │
│  + get_content_type() -> str                                    │
└───────────────┬─────────────────────────────────────────────────┘
                │
                │ implements
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
┌─────────────────┐  ┌─────────────────┐
│ PDFReport       │  │ ExcelReport     │
│ Generator       │  │ Generator       │
├─────────────────┤  ├─────────────────┤
│ + generate()    │  │ + generate()    │
│ + get_content_  │  │ + get_content_  │
│   type()        │  │   type()        │
└─────────────────┘  └─────────────────┘
        │                │
        │                │
        └───────┬────────┘
                │
                │ uses
                │
┌───────────────▼─────────────────────────────────────────────────┐
│              ReportGeneratorFactory                             │
│                                                                 │
│  + get_generator(format_type) -> ReportGenerator               │
│                                                                 │
│  - Factory Pattern para crear instancias                       │
└─────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos Completo

```
┌──────────────┐
│   Usuario    │
└──────┬───────┘
       │
       │ 1. Navegación / Acción
       ▼
┌──────────────────────────────────────┐
│         URL Router                   │
│    (finance/urls.py)                 │
└──────┬───────────────────────────────┘
       │
       │ 2. Routing
       ▼
┌──────────────────────────────────────┐
│         View (Controller)            │
│    - Processa request                │
│    - Valida con Forms                │
│    - Llama a servicios               │
└──────┬───────────────────────────────┘
       │
       │ 3. Business Logic
       ▼
┌──────────────────────────────────────┐
│         Services / Models            │
│    - ReportGenerator (DI)            │
│    - ExternalServiceConsumer         │
│    - Model methods                   │
└──────┬───────────────────────────────┘
       │
       │ 4. Data Access
       ▼
┌──────────────────────────────────────┐
│         Database (ORM)               │
│    - QuerySet operations             │
│    - Transactions, Categories, etc.  │
└──────┬───────────────────────────────┘
       │
       │ 5. Response Data
       ▼
┌──────────────────────────────────────┐
│         Template Rendering           │
│    - HTML + Context                  │
│    - Static files (CSS/JS)           │
└──────┬───────────────────────────────┘
       │
       │ 6. HTML Response
       ▼
┌──────────────┐
│   Usuario    │
└──────────────┘
```

## Estructura de Archivos y Responsabilidades

```
finance/
├── settings.py              # Configuración global
│   ├── INSTALLED_APPS
│   ├── MIDDLEWARE
│   ├── DATABASES
│   └── EXTERNAL_SERVICE_BASE_URL
│
├── urls.py                  # Routing principal
│   ├── /api/ → API REST
│   ├── /accounts/ → Autenticación
│   ├── /transactions/ → Transacciones
│   └── / → Dashboard
│
accounts/
├── models.py                # UserProfile
├── views.py                 # Auth, Profile, Admin
├── urls.py                  # Auth URLs
└── context_processors.py    # Language context
│
transactions/
├── models.py                # Transaction, Category, Tag, Budget, SavingsGoal, RecurringTransaction
├── views.py                 # CRUD Views
├── forms.py                 # Formularios de validación
├── serializers.py           # REST API Serializers
├── api_views.py             # REST API ViewSets
├── api_urls.py              # REST API URLs
├── services.py              # Servicios externos (clima, tipo de cambio)
├── external_service_consumer.py  # Consumo de servicios de otros equipos
├── external_views.py        # Vista para mostrar datos externos
├── report_generators.py     # DI Pattern para reportes
└── urls.py                  # Transaction URLs
│
dashboard/
├── views.py                 # DashboardView, stats API
└── urls.py                  # Dashboard URLs
```

## Notas sobre el Diagrama de Arquitectura

1. **Arquitectura MVC**: Django implementa un patrón similar a MVC donde:
   - Models = Capa de Datos (models.py)
   - Views = Controladores (views.py)
   - Templates = Vista (templates/)

2. **Servicios Externos**: La aplicación consume tres tipos de servicios:
   - APIs públicas (tipo de cambio, clima)
   - Servicios de equipos precedentes (cadena de entregables)
   - Proporciona servicios a equipos siguientes

3. **Inversión de Dependencias**: Implementada en `report_generators.py`:
   - Interfaz: `ReportGenerator`
   - Implementaciones: `PDFReportGenerator`, `ExcelReportGenerator`
   - Factory: `ReportGeneratorFactory`

4. **REST API**: Disponible en `/api/` para consumo externo:
   - Serializers para convertir Models a JSON
   - ViewSets para operaciones CRUD
   - Autenticación requerida

5. **Deployment**: Docker + GCP:
   - Dockerfile para contenedorización
   - docker-compose.yml para orquestación
   - PostgreSQL para producción

