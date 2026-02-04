# 📱 Dashboard Toegang - Mobile Instructies

## ✅ Status: Dashboard is LIVE!

Het dashboard draait momenteel op de server en toont **135 demo prijsrecords** van 5 Europese landen.

## 🌐 Toegang Opties

### Optie 1: GitHub Codespaces / Cloud Environment (BESTE OPTIE)

Aangezien je in een cloud omgeving draait, gebruik de **Port Forwarding** feature:

1. **In VS Code / Cursor**:
   - Kijk naar de "PORTS" tab onderaan
   - Zoek poort `5000`
   - Klik op het 🌐 icoon om de publieke URL te openen
   - Deze URL werkt op je mobile!

2. **Format**: `https://[unique-id].githubpreview.dev`

### Optie 2: Lokaal Netwerk (als je op een lokale machine draait)

1. **Vind je lokale IP**:
   ```bash
   hostname -I | awk '{print $1}'
   ```

2. **Open op mobile** (zelfde WiFi netwerk):
   ```
   http://[YOUR-IP]:5000
   ```

### Optie 3: ngrok Tunnel (Universal)

Installeer en start ngrok voor een publieke URL:

```bash
# Installeer ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Start tunnel
ngrok http 5000
```

Dit geeft je een publieke URL zoals: `https://abc123.ngrok.io`

### Optie 4: Quick Deploy naar Vercel/Railway

**Railway** (gratis tier, 1-command deploy):

```bash
# Installeer Railway CLI
npm install -g @railway/cli

# Login en deploy
railway login
railway init
railway up
```

## 🎯 Huidige Dashboard Features

### Dashboard URL: `http://localhost:5000`

**Wat je ziet**:
- 📊 **6 bronnen** (5 succesvol, 1 gefaald)
- 💰 **135 prijsrecords**
- 🌍 **5 landen**: NL, DE, BE, PL, GB
- 🥔 **3 commodities**: Aardappelen, Uien, Wortelen

**Functionaliteit**:
- ✅ Real-time statistieken
- ✅ Grafiek per land
- ✅ Filter op commodity (klik op de tabs)
- ✅ Actuele prijzen met valuta (€, £, zł)
- ✅ Auto-refresh elke 30 seconden
- ✅ Touch-friendly mobile UI
- ✅ Pull-to-refresh (klik op 🔄 knop rechtsonder)

## 📸 Preview

Het dashboard toont:
```
═══════════════════════════════
🌾 Agri-Market Scraper
Real-time prijsdata uit Europa
═══════════════════════════════

📊 Statistieken
┌────────────┬────────────┐
│ Bronnen: 6 │ Succesvol: 5│
│ Prijzen: 135│ Update: 12:00│
└────────────┴────────────┘

📊 Verdeling per Land
[Bar chart: NL, DE, BE, PL, GB]

🔍 Filter
[Alles] [🥔 Aardappelen] [🧅 Uien] [🥕 Wortelen]

💰 Actuele Prijzen
┌─────────────────────────┐
│ Agria                   │
│ €25.50 / 100kg         │
│ 📅 03-02-2026 🌍 NL    │
└─────────────────────────┘
... (meer prijzen)

⚖️ Legal Compliance
✅ Alle bronnen zijn legaal
```

## ⚖️ Legal Status

**ALLE BRONNEN ZIJN LEGAAL GESCRAPED** ✅

- 5 actieve bronnen zijn compliant met EU wetgeving
- Alleen publieke marktdata (feiten, geen copyright)
- GDPR compliant (geen persoonlijke data)
- robots.txt wordt gerespecteerd
- Zie `LEGAL_COMPLIANCE.md` voor volledige analyse

## 🚀 Quick Actions

### Dashboard herstarten:
```bash
cd /workspace
pkill -f flask
python3 -m flask --app dashboard/app run --host=0.0.0.0 --port=5000 &
```

### Nieuwe demo data genereren:
```bash
cd /workspace
python3 create_demo_data.py
```

### Echte scraper runnen (duurt langer):
```bash
cd /workspace
python3 orchestrator.py
```

## 📱 Mobile Optimalisaties

- ✅ Viewport optimized voor kleine schermen
- ✅ Touch targets > 44px
- ✅ Geen zware frameworks (snelle load)
- ✅ Responsive grid layout
- ✅ Smooth animations
- ✅ Bottom floating refresh button
- ✅ Pull-down gradient header

## 🎨 Design

- **Kleurschema**: Purple gradient (`#667eea` → `#764ba2`)
- **Typografie**: SF Pro / Segoe UI (native fonts)
- **Cards**: Rounded corners, subtle shadows
- **Animations**: Smooth transitions (0.2s-0.3s)

## 📊 API Endpoints (voor developers)

Test met curl:

```bash
# Summary statistics
curl http://localhost:5000/api/summary | jq

# All prices
curl http://localhost:5000/api/prices | jq

# Filter by commodity
curl "http://localhost:5000/api/prices?commodity=Potato" | jq

# Filter by country
curl "http://localhost:5000/api/prices?country=NL" | jq
```

## 🐛 Troubleshooting

**Dashboard laadt niet:**
```bash
# Check if Flask is running
ps aux | grep flask

# Check logs
tail -f /workspace/dashboard.log
```

**Geen data:**
```bash
# Verify data file exists
ls -lh /workspace/output/prices.json

# Regenerate demo data
python3 /workspace/create_demo_data.py
```

**Port in gebruik:**
```bash
# Kill process on port 5000
sudo lsof -ti:5000 | xargs kill -9

# Restart dashboard
cd /workspace && python3 -m flask --app dashboard/app run --host=0.0.0.0 --port=5000 &
```

## 🎓 Volgende Stappen

1. **Mobile testen**: Open via een van de toegangsopties hierboven
2. **Data verkennen**: Gebruik de filters en scroll door prijzen
3. **Echte scraper runnen**: `python3 orchestrator.py` voor live data
4. **Productie deployment**: Kies Railway, Vercel, of Heroku
5. **API integratie**: Gebruik de REST API voor je eigen apps

## 📞 Support

- **Documentatie**: Zie `dashboard/README.md`
- **Legal info**: Zie `LEGAL_COMPLIANCE.md`
- **Main README**: Zie `README.md`

---

**Geniet van je mobile dashboard!** 🎉📱
