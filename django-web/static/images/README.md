# 📸 **GUÍA DE IMÁGENES - APG PACKING**

## 📁 **Estructura de Directorios**

```
static/images/
├── 🔐 login/          # Imágenes para la página de login
│   ├── background.jpg  # Imagen de fondo del login (recomendado)
│   ├── hero.jpg       # Imagen del panel izquierdo
│   └── pattern.png    # Patrones decorativos
│
├── 🏢 logo/           # Logos corporativos
│   ├── logo.png       # Logo principal
│   ├── logo-white.png # Logo blanco para fondos oscuros
│   ├── favicon.ico    # Favicon del sitio
│   └── logo-small.png # Logo pequeño para header
│
├── 📊 dashboard/      # Imágenes para el dashboard
│   ├── charts/        # Gráficos e iconos
│   └── illustrations/ # Ilustraciones corporativas
│
└── 🎨 general/        # Imágenes generales
    ├── placeholders/  # Imágenes de placeholder
    └── icons/         # Iconos personalizados
```

---

## 🖼️ **Cómo Agregar Imágenes al Login**

### **1. Para el Panel Izquierdo (Hero Section):**

Coloca tu imagen en: `static/images/login/hero.jpg`

Luego actualiza el template de login:

```html
<!-- En templates/auth/login.html -->
<div class="login-bg-image" style="background-image: url('{% static "images/login/hero.jpg" %}');">
    <!-- Contenido existente -->
</div>
```

### **2. Para Fondo Completo:**

Coloca tu imagen en: `static/images/login/background.jpg`

Y agrega esta clase CSS:

```css
.login-background {
    background-image: url('/static/images/login/background.jpg');
    background-size: cover;
    background-position: center;
}
```

### **3. Para Logo Corporativo:**

Coloca tu logo en: `static/images/logo/logo.png`

Actualiza el template:

```html
<img src="{% static 'images/logo/logo.png' %}" alt="APG PACKING" class="corporate-logo">
```

---

## 📐 **Especificaciones Recomendadas**

### **Imágenes de Login:**
- **Resolución**: 1920x1080px mínimo
- **Formato**: JPG o PNG
- **Tamaño**: Máximo 2MB
- **Orientación**: Landscape para hero, cualquiera para fondo

### **Logos:**
- **Formato**: PNG con transparencia
- **Tamaños**:
  - Logo principal: 200x200px
  - Logo header: 60x60px
  - Favicon: 32x32px
- **Fondo**: Transparente preferible

### **Iconos y Elementos:**
- **Formato**: SVG o PNG
- **Tamaño**: 24x24px, 48x48px, 96x96px
- **Estilo**: Consistente con el diseño corporativo

---

## 🎨 **Paleta de Colores APG PACKING**

Para que tus imágenes mantengan consistencia:

```css
Primario:    #2563eb (Azul corporativo)
Secundario:  #1e293b (Gris oscuro)
Acento:      #3b82f6 (Azul claro)
Éxito:       #22c55e (Verde)
Advertencia: #f59e0b (Amarillo)
Peligro:     #ef4444 (Rojo)
```

---

## 🚀 **Implementación Rápida**

### **Paso 1: Agregar tus imágenes**
```bash
# Copia tus imágenes a los directorios correspondientes
cp tu-logo.png static/images/logo/logo.png
cp tu-background.jpg static/images/login/background.jpg
```

### **Paso 2: Actualizar templates**
```html
{% load static %}

<!-- Para usar en templates -->
<img src="{% static 'images/logo/logo.png' %}" alt="Logo">
<div style="background-image: url('{% static "images/login/background.jpg" %}');"></div>
```

### **Paso 3: Recopilar archivos estáticos**
```bash
cd django-web
python manage.py collectstatic --noinput
```

---

## 🔧 **Configuración Avanzada**

### **Para Imágenes Responsivas:**

```html
<picture>
    <source media="(max-width: 768px)" srcset="{% static 'images/login/hero-mobile.jpg' %}">
    <source media="(max-width: 1024px)" srcset="{% static 'images/login/hero-tablet.jpg' %}">
    <img src="{% static 'images/login/hero-desktop.jpg' %}" alt="APG PACKING">
</picture>
```

### **Para Lazy Loading:**

```html
<img data-src="{% static 'images/dashboard/chart.png' %}" 
     class="opacity-0 transition-opacity duration-300" 
     alt="Gráfico">
```

### **Para Optimización:**

```html
<!-- WebP con fallback -->
<picture>
    <source srcset="{% static 'images/logo/logo.webp' %}" type="image/webp">
    <img src="{% static 'images/logo/logo.png' %}" alt="Logo">
</picture>
```

---

## 📱 **Consideraciones Móviles**

- Usa imágenes optimizadas para móviles (más pequeñas)
- Considera diferentes orientaciones
- Prueba la legibilidad en pantallas pequeñas
- Usa formatos modernos (WebP) cuando sea posible

---

## 🛠️ **Herramientas Recomendadas**

### **Para Optimización:**
- **TinyPNG**: Compresión PNG/JPG
- **Squoosh**: Conversión y optimización
- **ImageOptim**: Optimización automática

### **Para Edición:**
- **Figma**: Diseño de interfaces
- **Photoshop**: Edición avanzada
- **Canva**: Diseño rápido

---

## 📋 **Checklist de Implementación**

- [ ] ✅ Logo principal agregado (`logo/logo.png`)
- [ ] ✅ Logo blanco para header (`logo/logo-white.png`)
- [ ] ✅ Favicon configurado (`logo/favicon.ico`)
- [ ] ✅ Imagen de fondo login (`login/background.jpg`)
- [ ] ✅ Imagen hero del login (`login/hero.jpg`)
- [ ] ✅ Templates actualizados con `{% static %}`
- [ ] ✅ Archivos estáticos recopilados
- [ ] ✅ Pruebas en diferentes dispositivos
- [ ] ✅ Optimización de tamaños completada

---

## 🎯 **Ejemplo Completo de Uso**

```html
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <link rel="icon" href="{% static 'images/logo/favicon.ico' %}">
    <link rel="stylesheet" href="{% static 'css/corporate.css' %}">
</head>
<body>
    <!-- Header con logo -->
    <header>
        <img src="{% static 'images/logo/logo.png' %}" 
             alt="APG PACKING" 
             class="corporate-logo">
    </header>
    
    <!-- Login con fondo -->
    <div class="login-bg-image" 
         style="background-image: url('{% static 'images/login/background.jpg' %}');">
        <div class="login-card">
            <!-- Contenido del login -->
        </div>
    </div>
    
    <script src="{% static 'js/corporate.js' %}"></script>
</body>
</html>
```

---

**¡Ahora puedes agregar todas tus imágenes corporativas y personalizar completamente el diseño de APG PACKING!** 🎨✨
