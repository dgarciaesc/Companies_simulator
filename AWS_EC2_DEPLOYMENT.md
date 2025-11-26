# AWS EC2 Deployment Guide (Free Tier)

## Prerrequisitos

1. **Cuenta AWS**: Crear cuenta gratuita en https://aws.amazon.com/free
2. **Tarjeta de crédito**: Requerida para verificación (no se cobrará en free tier)
3. **Repositorio GitHub**: Tu código debe estar en GitHub

## Paso 1: Crear Instancia EC2 (Free Tier)

### 1.1. Acceder a AWS Console
1. Ir a [AWS Console](https://console.aws.amazon.com)
2. Buscar "EC2" en la barra de búsqueda
3. Hacer clic en **Launch Instance**

### 1.2. Configurar Instancia
```
Nombre: companies-simulator

Imágenes de aplicaciones y sistemas operativos:
- Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
- Arquitectura: 64-bit (x86)
- ✅ Free tier eligible

Tipo de instancia:
- t2.micro (1 vCPU, 1 GB RAM) - ✅ FREE TIER
- O t3.micro si está disponible

Par de claves (Key pair):
- Crear nuevo par de claves
- Nombre: companies-simulator-key
- Tipo: RSA
- Formato: .pem (para Mac/Linux) o .ppk (para Windows/PuTTY)
- 💾 DESCARGAR Y GUARDAR LA CLAVE (no se puede recuperar después)

Configuración de red:
- ✅ Permitir tráfico SSH desde 0.0.0.0/0 (o tu IP)
- ✅ Permitir tráfico HTTP desde Internet
- ✅ Permitir tráfico HTTPS desde Internet

Configurar almacenamiento:
- 30 GB gp3 (free tier incluye hasta 30 GB)
- Tipo de volumen: General Purpose SSD (gp3)
```

### 1.3. Lanzar Instancia
- Revisar configuración
- Hacer clic en **Launch Instance**
- Esperar a que el estado sea "Running" (2-3 minutos)

## Paso 2: Configurar Grupo de Seguridad

1. En EC2 Dashboard → **Security Groups**
2. Seleccionar el grupo de seguridad de tu instancia
3. **Inbound Rules** → **Edit inbound rules**
4. Asegurar estas reglas:

```
Type         Protocol   Port Range   Source
SSH          TCP        22           0.0.0.0/0  (o tu IP)
HTTP         TCP        80           0.0.0.0/0
HTTPS        TCP        443          0.0.0.0/0
PostgreSQL   TCP        5432         127.0.0.1/32  (solo localhost)
Custom TCP   TCP        8000         127.0.0.1/32  (solo localhost)
```

## Paso 3: Conectar a la Instancia EC2

### Opción A: Desde Windows (PowerShell)
```powershell
# Mover la clave descargada a una ubicación segura
Move-Item .\companies-simulator-key.pem $HOME\.ssh\

# Conectar a EC2
ssh -i $HOME\.ssh\companies-simulator-key.pem ubuntu@<EC2-PUBLIC-IP>
```

### Opción B: Desde AWS Console (EC2 Instance Connect)
1. Seleccionar tu instancia
2. Clic en **Connect**
3. Seleccionar **EC2 Instance Connect**
4. Clic en **Connect**

### Opción C: Desde Mac/Linux
```bash
# Establecer permisos correctos
chmod 400 companies-simulator-key.pem

# Conectar
ssh -i companies-simulator-key.pem ubuntu@<EC2-PUBLIC-IP>
```

## Paso 4: Setup Inicial en EC2

Una vez conectado por SSH:

```bash
# Establecer contraseña de base de datos
export DB_PASSWORD="tu-contraseña-segura-aqui"

# Descargar script de setup
curl -O https://raw.githubusercontent.com/dgarciaesc/Companies_simulator/main/setup-aws-ec2.sh

# Dar permisos de ejecución
chmod +x setup-aws-ec2.sh

# Ejecutar setup
./setup-aws-ec2.sh
```

El script instalará:
- ✅ Python 3.12
- ✅ PostgreSQL
- ✅ Node.js 18
- ✅ Nginx
- ✅ Tu aplicación completa
- ✅ Servicios systemd configurados

## Paso 5: Crear Usuario IAM para GitHub Actions

### 5.1. Crear Usuario IAM
1. En AWS Console → **IAM**
2. **Users** → **Add users**
3. Nombre: `github-actions-deploy`
4. Tipo de acceso: **Programmatic access**
5. Permisos: **AmazonEC2FullAccess** (o crear política personalizada)
6. **Create user**
7. **💾 GUARDAR Access Key ID y Secret Access Key**

### 5.2. Política IAM Mínima (Opcional, más segura)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus"
      ],
      "Resource": "*"
    }
  ]
}
```

## Paso 6: Configurar GitHub Secrets

1. Ir a tu repositorio GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** para cada uno:

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID
Valor: <tu-access-key-id>

AWS_SECRET_ACCESS_KEY
Valor: <tu-secret-access-key>

AWS_REGION
Valor: us-east-1  (o tu región)

# EC2 Connection
EC2_HOST
Valor: <tu-ec2-public-ip>

EC2_USER
Valor: ubuntu

EC2_SSH_KEY
Valor: <contenido-completo-del-archivo-.pem>

# Database
DB_PASSWORD
Valor: <tu-contraseña-de-bd>
```

### Para obtener el contenido de la clave SSH:
```powershell
# Windows
Get-Content $HOME\.ssh\companies-simulator-key.pem | Out-String
```

```bash
# Mac/Linux
cat companies-simulator-key.pem
```

## Paso 7: Habilitar GitHub Actions

El archivo `.github/workflows/deploy-aws.yml` ya está configurado.

Para deployar:
```bash
git add .
git commit -m "Deploy to AWS EC2"
git push origin main
```

Monitorear el deployment:
- GitHub → **Actions** tab
- Ver el workflow en ejecución

## Paso 8: Acceder a la Aplicación

### Obtener IP Pública
```bash
# Desde AWS Console
EC2 → Instances → Seleccionar instancia → Ver "Public IPv4 address"

# Desde la instancia EC2
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

### Acceder
```
URL: http://<EC2-PUBLIC-IP>

Credenciales de prueba:
Email: user1@test.com
Password: password1
```

## Monitoreo y Gestión

### Verificar Estado de Servicios
```bash
# API
sudo systemctl status companies-api

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql
```

### Ver Logs
```bash
# API logs (en tiempo real)
sudo journalctl -u companies-api -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Últimos 100 logs de API
sudo journalctl -u companies-api -n 100
```

### Reiniciar Servicios
```bash
# Reiniciar API
sudo systemctl restart companies-api

# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### Deployment Manual
```bash
cd ~/companies_simulator
git pull origin main
./deploy-aws.sh
```

## Gestión de Costos (Free Tier)

### ✅ Recursos Gratuitos (12 meses)
- 750 horas/mes de instancia t2.micro o t3.micro
- 30 GB de almacenamiento EBS General Purpose (SSD)
- 15 GB de transferencia de datos saliente
- 1 GB de transferencia de datos entrante

### ⚠️ Monitorear Uso
1. AWS Console → **Billing Dashboard**
2. **Free Tier** → Ver uso actual
3. Configurar **Billing Alerts**:
   - CloudWatch → Alarmas
   - Crear alarma cuando el coste estimado > $1

### 💡 Consejos para Mantenerse en Free Tier
- Usar solo 1 instancia t2.micro
- Detener instancia cuando no se use (no terminar)
- Mantener almacenamiento bajo 30 GB
- Monitorear transferencia de datos

## Mejoras de Seguridad

### 1. Restringir Acceso SSH
```bash
# Editar grupo de seguridad
# Cambiar SSH source de 0.0.0.0/0 a tu IP específica
```

### 2. Configurar SSL/HTTPS (con dominio)
```bash
# Instalar Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado (necesitas un dominio)
sudo certbot --nginx -d tudominio.com

# Auto-renovación
sudo certbot renew --dry-run
```

### 3. Configurar Firewall UFW
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 4. Actualizar Sistema Regularmente
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get autoremove -y
```

## Troubleshooting

### Problema: No puedo conectarme por SSH
```bash
# Verificar:
1. IP pública correcta
2. Grupo de seguridad permite puerto 22
3. Permisos de clave: chmod 400 clave.pem
4. Usuario correcto: ubuntu (no ec2-user)
```

### Problema: Aplicación no accesible
```bash
# Verificar servicios
sudo systemctl status companies-api
sudo systemctl status nginx

# Verificar puertos
sudo netstat -tulpn | grep -E '(80|8000)'

# Ver logs
sudo journalctl -u companies-api --since "5 minutes ago"
```

### Problema: Error de base de datos
```bash
# Verificar PostgreSQL
sudo systemctl status postgresql

# Probar conexión
psql -U companies_user -d companies_db -h localhost

# Recrear base de datos
sudo -u postgres psql
DROP DATABASE companies_db;
CREATE DATABASE companies_db OWNER companies_user;
\q

# Reejecutar setup
cd ~/companies_simulator
./setup-aws-ec2.sh
```

### Problema: Sin memoria
```bash
# Verificar uso de memoria
free -h

# Crear swap (1GB)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Backup y Recuperación

### Backup de Base de Datos
```bash
# Crear backup
cd ~
sudo -u postgres pg_dump companies_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
sudo -u postgres psql companies_db < backup_20231126_123000.sql
```

### Snapshot de Instancia EC2
1. EC2 Console → Instances
2. Seleccionar instancia → **Actions** → **Image and templates** → **Create image**
3. Nombre: `companies-simulator-backup-2023-11-26`
4. Crear imagen

### Restaurar desde Snapshot
1. EC2 Console → AMIs
2. Seleccionar imagen → **Launch instance from AMI**

## Actualizar la Aplicación

### Automático (via GitHub Actions)
```bash
# Hacer cambios en código
git add .
git commit -m "Nueva funcionalidad"
git push origin main
# GitHub Actions deployará automáticamente
```

### Manual
```bash
# Conectar a EC2
ssh -i clave.pem ubuntu@<EC2-IP>

# Actualizar
cd ~/companies_simulator
git pull origin main
./deploy-aws.sh
```

## Detener/Iniciar Instancia (Ahorrar costos)

### Detener Instancia
```bash
# Desde AWS Console
EC2 → Instances → Seleccionar → Instance state → Stop

# O desde AWS CLI
aws ec2 stop-instances --instance-ids i-1234567890abcdef0
```

### Iniciar Instancia
```bash
# Desde AWS Console
EC2 → Instances → Seleccionar → Instance state → Start

# O desde AWS CLI
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

⚠️ **Nota**: La IP pública cambiará al reiniciar (usar Elastic IP para IP fija)

## Elastic IP (IP Fija - Opcional)

```bash
# Asignar Elastic IP
1. EC2 → Elastic IPs → Allocate Elastic IP address
2. Asociar con tu instancia

⚠️ Elastic IP es GRATIS cuando está asociada a instancia running
💰 Cobra $0.005/hora cuando NO está asociada o instancia stopped
```

## Soporte

- **GitHub Issues**: https://github.com/dgarciaesc/Companies_simulator/issues
- **AWS Documentation**: https://docs.aws.amazon.com/ec2
- **AWS Free Tier**: https://aws.amazon.com/free
- **GitHub Actions**: https://docs.github.com/en/actions

## Comandos Rápidos de Referencia

```bash
# Conectar a EC2
ssh -i clave.pem ubuntu@<IP>

# Ver estado servicios
sudo systemctl status companies-api nginx

# Ver logs en tiempo real
sudo journalctl -u companies-api -f

# Reiniciar todo
sudo systemctl restart companies-api nginx

# Deploy manual
cd ~/companies_simulator && ./deploy-aws.sh

# Backup BD
sudo -u postgres pg_dump companies_db > backup.sql

# Ver IP pública
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Ver uso de recursos
htop  # (instalar: sudo apt install htop)
df -h  # espacio en disco
free -h  # memoria
```
