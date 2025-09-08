# 🔌 Configuración de Puertos - Alza API VPS

## 📋 Resumen de Puertos

### **Puertos Externos (VPS Firewall)**
Estos puertos DEBEN estar habilitados en el firewall del VPS:

| Puerto | Protocolo | Servicio | Descripción |
|--------|-----------|----------|-------------|
| **22** | TCP | SSH | Acceso remoto para administración |
| **80** | TCP | HTTP | Nginx - Redirección a HTTPS |
| **443** | TCP | HTTPS | Nginx - Tráfico SSL/TLS |

### **Puertos Internos (Docker Network)**
Estos puertos funcionan internamente y NO necesitan firewall:

| Puerto | Servicio | Descripción |
|--------|----------|-------------|
| **5544** | FastAPI | API REST (interno) |
| **8880** | Django Web | Aplicación web (interno) |
| **6379** | Redis | Cache (interno) |

## 🛡️ Configuración del Firewall

### **Automática (Recomendada)**
El script de despliegue configura automáticamente el firewall:
```bash
bash deploy-all.sh
```

### **Manual con UFW**
```bash
# Instalar UFW
sudo apt-get update
sudo apt-get install -y ufw

# Configurar reglas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Verificar estado
sudo ufw status
```

### **Manual con iptables**
```bash
# Limpiar reglas existentes
sudo iptables -F

# Permitir loopback
sudo iptables -A INPUT -i lo -j ACCEPT

# Permitir conexiones establecidas
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Permitir SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Permitir HTTP
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# Permitir HTTPS
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Denegar todo lo demás
sudo iptables -A INPUT -j DROP

# Guardar reglas (Ubuntu)
sudo iptables-save > /etc/iptables/rules.v4
```

## 🌐 URLs de Acceso

### **Desde Internet (Público)**
- **Web Principal**: `http://34.136.15.241` → Nginx
- **Web SSL**: `https://34.136.15.241` → Nginx SSL
- **API Docs**: `http://34.136.15.241/docs` → FastAPI Docs

### **Desde VPS (Interno)**
- **FastAPI**: `http://localhost:5544`
- **Django**: `http://localhost:8880`
- **Redis**: `redis://localhost:6379`
- **Nginx**: `http://localhost:80`

## 🔍 Verificación de Puertos

### **Verificar puertos abiertos**
```bash
# Ver puertos en uso
sudo netstat -tulpn

# Ver servicios Docker
docker-compose ps

# Verificar UFW
sudo ufw status verbose

# Test conectividad externa
curl -I http://34.136.15.241
curl -I https://34.136.15.241
```

### **Test desde exterior**
```bash
# Desde tu máquina local
curl -I http://34.136.15.241
curl -I http://34.136.15.241:5544  # Esto NO debe funcionar (interno)
curl -I http://34.136.15.241:8880  # Esto NO debe funcionar (interno)
```

## 🚨 Seguridad

### **Puertos que NO deben ser públicos**
- **5544** (FastAPI) - Solo interno via Nginx
- **8880** (Django) - Solo interno via Nginx  
- **6379** (Redis) - Solo interno
- **5666** (PostgreSQL) - Externo pero protegido

### **Configuración segura**
```bash
# Verificar que puertos internos NO son accesibles
nmap -p 5544,8880,6379 34.136.15.241

# Resultado esperado: filtered o closed
```

## 📊 Flujo de Tráfico

```
Internet → VPS:80/443 → Nginx → {
    /api/* → FastAPI:5544
    /admin/* → Django:8880
    /* → Django:8880
}
```

## 🔧 Troubleshooting

### **Puerto bloqueado**
```bash
# Verificar firewall
sudo ufw status
sudo iptables -L

# Verificar servicio
sudo netstat -tulpn | grep :80
docker-compose ps
```

### **Servicio no accesible**
```bash
# Test interno
curl -I http://localhost:5544/health
curl -I http://localhost:8880

# Ver logs
docker-compose logs nginx
docker-compose logs api
docker-compose logs django-web
```

### **SSL no funciona**
```bash
# Verificar certificados
ls -la certbot/conf/live/34.136.15.241/

# Renovar certificados
./init-letsencrypt.sh
```

## ✅ Checklist de Puertos

- [ ] Puerto 22 (SSH) habilitado
- [ ] Puerto 80 (HTTP) habilitado  
- [ ] Puerto 443 (HTTPS) habilitado
- [ ] Puertos internos (5544, 8880, 6379) NO públicos
- [ ] Firewall UFW configurado
- [ ] Nginx funcionando en puerto 80/443
- [ ] FastAPI accesible solo internamente
- [ ] Django accesible solo internamente
- [ ] SSL certificados configurados

## 🎯 Comandos Rápidos

```bash
# Configurar firewall automáticamente
sudo bash setup-firewall.sh

# Ver estado completo
sudo ufw status && docker-compose ps

# Test completo
curl -I http://34.136.15.241 && curl -I http://34.136.15.241/health
```
