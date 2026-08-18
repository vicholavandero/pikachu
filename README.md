# 🎴 Hunter Card TCG — Monitor de Preventas

Corre gratis en GitHub Actions y te avisa al celular cuando aparece una nueva preventa.

---

## Configuración (10 minutos)

### 1. Crear el repositorio en GitHub

1. Ve a [github.com/new](https://github.com/new)
2. Ponle cualquier nombre (ej: `hunter-monitor`)
3. Puede ser **privado** (tienes 500 min/mes gratis) o **público** (minutos ilimitados)
4. Crea el repo y sube estos archivos:

```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/TU_USUARIO/hunter-monitor.git
git push -u origin main
```

---

### 2. Elegir método de notificación

#### Opción A: ntfy.sh (más simple, recomendada)

1. Instala la app **ntfy** en tu celular (Android/iOS — es gratis)
2. Inventa un nombre de tema único, ej: `hunter-tcg-alertas-xyz123`
   - Abre la app → suscríbete a ese tema
3. En GitHub → tu repo → **Settings → Secrets and variables → Actions → New repository secret**:
   - Nombre: `NTFY_TOPIC`
   - Valor: el nombre de tema que elegiste

#### Opción B: Telegram

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram → `/newbot` → guarda el token
2. Habla con [@userinfobot](https://t.me/userinfobot) → guarda tu Chat ID
3. En GitHub → Secrets → agrega dos secrets:
   - `TELEGRAM_TOKEN` → el token del bot
   - `TELEGRAM_CHAT_ID` → tu chat ID

Puedes configurar **ambas opciones** a la vez si quieres.

---

### 3. Activar y probar

1. Ve a **Actions** en tu repo
2. Haz clic en el workflow `Monitor Hunter Card TCG Preventas`
3. Clic en **Run workflow** para probarlo manualmente
4. Revisa los logs — deberías ver los productos actuales encontrados

A partir de ahí corre automáticamente cada 30 minutos.

---

## Cómo funciona

```
GitHub Actions (cada 30 min)
       │
       ▼
monitor.py → scraping de huntercardtcg.com/preventas
       │
       ├── compara con products.json (estado anterior)
       │
       ├── si hay productos nuevos → notificación push
       │
       └── guarda nuevo estado en products.json (commit automático)
```

## Personalizar el intervalo

Edita `.github/workflows/monitor.yml`, línea `cron`:

```yaml
- cron: "*/30 * * * *"   # cada 30 min (por defecto)
- cron: "*/15 * * * *"   # cada 15 min
- cron: "0 * * * *"      # cada hora
```

> GitHub no garantiza ejecuciones más frecuentes que cada 5 minutos.
> Con repos privados, 500 min/mes ÷ 30 min = ~1,000 ejecuciones/mes, más que suficiente.
