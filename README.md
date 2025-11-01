# Gestor de Finanzas Personales

Una aplicación web completa para gestionar finanzas personales desarrollada con Django 5. Permite a los usuarios registrar ingresos y gastos, crear categorías personalizadas, establecer presupuestos mensuales y visualizar estadísticas con gráficos interactivos.

## 🚀 Características

### ✅ Funcionalidades Implementadas

- **Autenticación de Usuarios**
  - Registro de nuevos usuarios
  - Inicio y cierre de sesión
  - Gestión de perfiles
  - Cambio de contraseñas

- **Gestión de Transacciones**
  - CRUD completo para ingresos y gastos
  - Categorías personalizables con colores e iconos
  - Filtros avanzados por tipo, categoría, fecha y búsqueda
  - Exportación a CSV
  - Paginación de resultados

- **Dashboard Interactivo**
  - Estadísticas en tiempo real
  - Gráficos con Chart.js:
    - Línea temporal de ingresos vs gastos
    - Gráfico de torta por categorías
    - Gráfico de barras para presupuestos
  - Transacciones recientes
  - Presupuestos del mes actual
  - Categorías más utilizadas

- **Sistema de Presupuestos**
  - Creación de presupuestos mensuales por categoría
  - Seguimiento del progreso en tiempo real
  - Alertas cuando se excede el presupuesto
  - Visualización del porcentaje utilizado

- **Reportes y Exportación**
  - Reportes mensuales detallados
  - Exportación de transacciones a CSV
  - Filtros aplicables a la exportación

- **Interfaz Moderna**
  - Diseño responsive con Bootstrap 5
  - Iconos de Font Awesome
  - Animaciones CSS
  - Modo oscuro (opcional)
  - Interfaz intuitiva y fácil de usar

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.0
- **Frontend**: Bootstrap 5, Chart.js, Font Awesome
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Autenticación**: Sistema nativo de Django
- **Gráficos**: Chart.js
- **Exportación**: django-import-export, pandas

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

## 🔧 Instalación

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd Django-Finanzas
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear Superusuario (Opcional)

```bash
python manage.py createsuperuser
```

### 6. Ejecutar el Servidor

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/`

## 📁 Estructura del Proyecto

```
Django-Finanzas/
├── finance/                 # Configuración principal del proyecto
│   ├── settings.py         # Configuraciones de Django
│   ├── urls.py             # URLs principales
│   └── wsgi.py             # Configuración WSGI
├── accounts/               # Aplicación de autenticación
│   ├── views.py           # Vistas de registro y perfil
│   ├── urls.py            # URLs de autenticación
│   └── templates/         # Templates de autenticación
├── transactions/          # Aplicación de transacciones
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas CRUD
│   ├── forms.py           # Formularios
│   ├── admin.py           # Configuración del admin
│   └── templates/         # Templates de transacciones
├── dashboard/             # Aplicación del dashboard
│   ├── views.py           # Vistas del dashboard
│   ├── urls.py            # URLs del dashboard
│   └── templates/         # Templates del dashboard
├── templates/             # Templates base
│   └── base/              # Template base principal
├── static/                # Archivos estáticos
│   ├── css/               # Estilos CSS
│   ├── js/                # JavaScript
│   └── images/            # Imágenes
├── requirements.txt       # Dependencias del proyecto
├── manage.py             # Script de gestión de Django
└── README.md             # Este archivo
```

## 🎯 Uso de la Aplicación

### 1. Registro e Inicio de Sesión

1. Accede a `http://127.0.0.1:8000/`
2. Haz clic en "Registrarse" para crear una nueva cuenta
3. Completa el formulario de registro
4. Inicia sesión con tus credenciales

### 2. Configuración Inicial

Al registrarte, se crearán automáticamente categorías por defecto:
- **Ingresos**: Salario, Freelance, Inversiones, Otros Ingresos
- **Gastos**: Alimentación, Transporte, Vivienda, Servicios, Entretenimiento, Salud, Educación, Ropa, Otros Gastos

### 3. Gestión de Transacciones

1. **Agregar Transacción**:
   - Ve a "Transacciones" → "Nueva Transacción"
   - Selecciona el tipo (Ingreso/Gasto)
   - Ingresa el monto
   - Selecciona una categoría
   - Agrega fecha y descripción
   - Guarda la transacción

2. **Filtrar Transacciones**:
   - Usa los filtros en la página de transacciones
   - Filtra por tipo, categoría, fecha o búsqueda
   - Los filtros se aplican automáticamente

3. **Exportar Datos**:
   - Haz clic en "Exportar CSV" en la página de transacciones
   - Los filtros aplicados se incluyen en la exportación

### 4. Gestión de Categorías

1. **Ver Categorías**: Ve a "Categorías" en el menú
2. **Crear Categoría**: Haz clic en "Nueva Categoría"
3. **Personalizar**: Asigna nombre, color e icono
4. **Editar/Eliminar**: Usa los botones de acción

### 5. Sistema de Presupuestos

1. **Crear Presupuesto**:
   - Ve a "Presupuestos" → "Nuevo Presupuesto"
   - Selecciona categoría y mes
   - Define el monto del presupuesto

2. **Seguimiento**:
   - El dashboard muestra el progreso en tiempo real
   - Las alertas aparecen cuando se excede el presupuesto
   - Los porcentajes se actualizan automáticamente

### 6. Dashboard y Reportes

1. **Dashboard Principal**:
   - Estadísticas generales y del mes actual
   - Gráficos interactivos
   - Transacciones recientes
   - Presupuestos del mes

2. **Reportes Mensuales**:
   - Ve a "Reportes" en el menú
   - Selecciona el mes deseado
   - Visualiza estadísticas detalladas por categoría

## 🔧 Configuración Avanzada

### Cambiar Base de Datos (Producción)

Para usar PostgreSQL en producción, modifica `finance/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tu_base_de_datos',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Configuración de Archivos Estáticos

Para producción, ejecuta:

```bash
python manage.py collectstatic
```

### Variables de Entorno

Crea un archivo `.env` para configuraciones sensibles:

```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
```

## 🐛 Solución de Problemas

### Error de Migraciones

Si encuentras errores con las migraciones:

```bash
python manage.py makemigrations --empty transactions
python manage.py makemigrations
python manage.py migrate
```

### Problemas con Archivos Estáticos

```bash
python manage.py collectstatic --clear
python manage.py collectstatic
```

### Reiniciar Base de Datos

```bash
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 📈 Próximas Mejoras

- [ ] Notificaciones por email
- [ ] API REST completa
- [ ] Aplicación móvil
- [ ] Integración con bancos
- [ ] Análisis predictivo de gastos
- [ ] Múltiples monedas
- [ ] Backup automático
- [ ] Modo offline

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado como proyecto de gestión de finanzas personales con Django.

## 📞 Soporte

Si tienes alguna pregunta o problema, por favor:

1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

¡Gracias por usar el Gestor de Finanzas Personales! 🎉
