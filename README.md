# Survey Validator - Render Deployment

## 🚀 Mission Overview
Stateless Survey Validator deployed to Render.com with external GitHub Actions Master Scheduler for 11-day autonomous operation.

## 📋 Architecture

### External Heartbeat (GitHub Actions)
- **Schedule**: Every 60 minutes via cron (`0 * * * *`)
- **Trigger**: Render Deploy Hook via curl POST
- **Stealth**: No self-ping - Render spins down after burst
- **Monitoring**: Heartbeat log tracking

### Stateless Burst Execution
- **Pattern**: 2:1 ratio (2 Form 1 submissions, 1 Form 2 submission)
- **Pacing**: Random 5-10 minute delays between submissions
- **Validation**: Full-Form Audit before each submission
- **Proxy Resilience**: Fresh proxy pool per burst

## 🔧 Configuration

### Environment Variables
```
FORM_1_URL=https://docs.google.com/forms/d/e/1FAIpQLSfNd-UEvuk2LyHMsTjflIo-wXjk6DVkD-wj1DPNc8rAsSMHBg/viewform
FORM_2_URL=https://docs.google.com/forms/d/e/1FAIpQLSd_a_DS8qoevwm-anVAn5Iv2J6uKDc6N5RjomS0h21Gd3Dmag/viewform?usp=dialog
RENDER_DEPLOY_HOOK_URL=your-render-deploy-hook-url
```

### GitHub Secrets
- `RENDER_DEPLOY_HOOK_URL`: Your Render service deploy hook URL

## 📁 Repository Structure
```
.github/workflows/pulse_deploy.yml  # GitHub Actions scheduler
main.py                          # Core survey logic (stateless)
app.py                           # Flask entry point
build.sh                          # Render build script
render.yaml                       # Render service config
requirements.txt                  # Python dependencies
```

## 🎯 Execution Flow

1. **GitHub Actions** triggers every hour
2. **Render Deploy Hook** spins up service
3. **Flask App** receives request and triggers burst
4. **Survey Validator** executes 2:1 pattern
5. **Service** shuts down (stealth mode)
6. **Ready** for next hourly trigger

## 🛡️ Stealth Features

### Headless Configuration
- `--headless --no-sandbox --disable-dev-shm-usage --disable-gpu`
- Undetected ChromeDriver
- CDP stealth commands masking navigator.webdriver

### User-Agent Rotation
- 5 different realistic User-Agents
- Random selection per execution

### Proxy Management
- Fresh proxy scraping each burst
- Multiple proxy sources
- Automatic failover

## 📊 Monitoring

### Render Dashboard
- All logs piped to stdout
- Real-time execution monitoring
- Error tracking and alerts

### GitHub Actions
- Heartbeat log artifacts
- Deploy success/failure tracking
- 30-day retention

## 🚀 Deployment Instructions

1. **Push to GitHub** with all files
2. **Set GitHub Secrets**: `RENDER_DEPLOY_HOOK_URL`
3. **Create Render Service** using `render.yaml`
4. **Configure Environment Variables** in Render dashboard
5. **Test** manual trigger via GitHub Actions

Mission ready for 11-day autonomous operation! 🎯
