# 🌾 Agri-Market Scraper Engine

Een robuuste, modulaire scraping pipeline voor het verzamelen van agrarische prijsdata uit heterogene bronnen in Europa. Geoptimaliseerd voor schaalbaarheid en verkoopwaarde.

## 📋 Overzicht

De Agri-Market Scraper Engine volgt een **ETL-architectuur** (Extract, Transform, Load) en verzamelt prijsinformatie over aardappelen, uien en andere agrarische producten van diverse Europese marktbronnen.

### Kenmerken

- **Modulair ontwerp**: Strategy Pattern voor verschillende scraper types
- **Anti-bot detectie**: Stealth mode met Playwright
- **Robuustheid**: Automatische retry logic met exponential backoff
- **Type safety**: Pydantic data validatie
- **Parallel processing**: Async/await voor efficiënte scraping
- **Heterogene bronnen**: HTML tables, PDFs, dynamische JavaScript websites

## 🏗️ Architectuur

```
agri-market-scraper/
├── config/
│   ├── sources.json          # Bron configuraties
│   └── __init__.py
├── models/
│   ├── market_price.py       # Pydantic data models
│   └── __init__.py
├── scrapers/
│   ├── base_scraper.py       # Basis scraper met Playwright
│   ├── html_scraper.py       # HTML tabel scraper
│   ├── pdf_scraper.py        # PDF document scraper
│   ├── dynamic_scraper.py    # JavaScript/AJAX scraper
│   ├── scraper_factory.py    # Strategy Pattern factory
│   └── __init__.py
├── utils/
│   ├── config_loader.py      # Configuratie beheer
│   ├── logger.py             # Logging setup
│   └── __init__.py
├── orchestrator.py           # Pipeline coordinator
├── requirements.txt          # Python dependencies
└── README.md
```

## 🚀 Installatie

### Vereisten

- Python 3.10 of hoger
- pip package manager
- PostgreSQL (optioneel, voor database opslag)

### Stap 1: Clone repository

```bash
git clone <repository-url>
cd agri-market-scraper
```

### Stap 2: Installeer dependencies

```bash
pip install -r requirements.txt
```

### Stap 3: Installeer Playwright browsers

```bash
playwright install chromium
```

### Stap 4: Configureer environment variabelen

```bash
cp .env.example .env
# Edit .env met je API keys en database credentials
```

## 📖 Gebruik

### Basis gebruik

Scrape alle actieve bronnen:

```python
import asyncio
from orchestrator import ScraperOrchestrator
from utils import setup_logger

# Setup logging
setup_logger(log_level="INFO")

# Maak orchestrator
orchestrator = ScraperOrchestrator(
    config_path="config/sources.json",
    headless=True,
    timeout=30000,
    max_retries=3
)

# Scrape alles
async def main():
    results = await orchestrator.scrape_all_active_sources()
    orchestrator.export_results_to_json("output/prices.json")
    
    # Toon resultaten
    all_prices = orchestrator.get_all_prices()
    print(f"Totaal verzamelde prijzen: {len(all_prices)}")

asyncio.run(main())
```

### Gebruik vanuit command line

```bash
python orchestrator.py
```

### Scrape specifieke bron

```python
import asyncio
from orchestrator import ScraperOrchestrator

async def scrape_single():
    orchestrator = ScraperOrchestrator()
    result = await orchestrator.scrape_source_by_id("nl_boerderij_aardappel")
    
    if result.success:
        print(f"Succes! {result.records_found} prijzen verzameld")
        for price in result.prices:
            print(f"{price.date} | {price.variety} | €{price.price}/{price.unit.value}")

asyncio.run(scrape_single())
```

### Scrape per land

```python
import asyncio
from orchestrator import ScraperOrchestrator

async def scrape_by_country():
    orchestrator = ScraperOrchestrator()
    results = await orchestrator.scrape_sources_by_country("NL")
    
    print(f"Nederlandse bronnen: {len(results)}")
    for result in results:
        print(f"- {result.source_id}: {result.records_found} records")

asyncio.run(scrape_by_country())
```

## 🔧 Configuratie

### Bron configuratie (sources.json)

Elke bron wordt gedefinieerd in `config/sources.json`:

```json
{
  "id": "nl_boerderij_aardappel",
  "name": "Boerderij.nl - Aardappelprijzen",
  "url": "https://www.boerderij.nl/marktinformatie/aardappelen",
  "country": "NL",
  "type": "html_table",
  "frequency": "daily",
  "active": true,
  "selectors": {
    "table_selector": "table.market-prices",
    "date_column": 0,
    "variety_column": 1,
    "price_column": 2
  }
}
```

#### Bron types

1. **html_table**: Statische HTML tabellen
   - Gebruikt BeautifulSoup en pandas
   - Vereist `table_selector` in configuratie

2. **pdf**: PDF documenten
   - Downloads en extract tabellen met pdfplumber
   - Vereist `pdf_config` met `download_url`

3. **dynamic**: JavaScript-rendered pagina's
   - Gebruikt Playwright met network interception
   - Vereist `wait_for` selector of 'networkidle'

4. **unstructured_text**: Vrije tekst (LLM-ready)
   - Voorbereid voor OpenAI GPT extractie
   - Vereist `llm_config` (toekomstige implementatie)

## 📊 Data Model

### MarketPrice Schema

```python
{
    "date": "2026-02-03",              # YYYY-MM-DD
    "commodity": "Potato",             # Potato, Onion, Carrot
    "variety": "Agria",                # Specifieke variëteit
    "price": 12.50,                    # Decimal
    "currency": "EUR",                 # EUR, PLN, GBP, USD
    "unit": "100kg",                   # kg, 100kg, ton, cwt
    "source_id": "nl_boerderij_aardappel",
    "country": "NL",                   # ISO 3166-1 alpha-2
    "quality_grade": "Class I",        # Optioneel
    "metadata": {}                     # Extra informatie
}
```

### Data validatie

Alle data wordt gevalideerd met Pydantic:

- ✓ Type checking
- ✓ Date niet in de toekomst
- ✓ Price >= 0
- ✓ Country code uppercase 2 letters
- ✓ Enum validatie voor commodity, currency, unit

## 🛡️ Anti-Bot Features

De BaseScraper implementeert diverse stealth technieken:

1. **User-agent rotatie**: Willekeurige realistische user agents
2. **Browser fingerprinting bypass**:
   - `navigator.webdriver` override
   - Plugin/language mocking
   - Chrome object simulatie
3. **Stealth argumenten**: 
   - Disabled automation flags
   - Natural viewport sizes
   - Realistic headers
4. **Human-like gedrag**:
   - Random delays (0.5-2s)
   - Page scrolling voor lazy loading
   - Network idle waiting

## 🔄 Retry Logic

Automatische retry met exponential backoff:

- **Max retries**: 3 (configureerbaar)
- **Retry bij**: 5xx errors, timeouts, connection errors
- **Backoff**: 2s, 4s, 8s
- **Gebruikt**: Tenacity library

## 📈 Extensibiliteit

### Nieuwe scraper types toevoegen

```python
from scrapers import BaseScraper, ScraperFactory
from models import ScraperResult

class CustomScraper(BaseScraper):
    async def scrape(self) -> ScraperResult:
        # Implementeer custom logic
        pass

# Registreer nieuwe type
ScraperFactory.register_scraper_type('custom', CustomScraper)
```

### Nieuwe bronnen toevoegen

Voeg simpelweg een entry toe aan `config/sources.json` met de juiste configuratie.

## 🧪 Testing

```bash
# Valideer alle bronnen
python -c "from utils import ConfigLoader; loader = ConfigLoader(); print(loader.validate_all_sources())"

# Test enkele bron
python -c "
import asyncio
from orchestrator import ScraperOrchestrator
async def test():
    orch = ScraperOrchestrator()
    result = await orch.scrape_source_by_id('nl_boerderij_aardappel')
    print(f'Success: {result.success}, Records: {result.records_found}')
asyncio.run(test())
"
```

## 📝 Logging

Logs worden geschreven naar:
- **Console**: Colored output met timestamps
- **File**: `logs/scraper.log` (rotatie bij 10 MB, 7 dagen retentie)

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`

## 🔮 Toekomstige uitbreidingen

### Module 3: Transform Layer (TODO)
- [ ] Valuta conversie naar EUR
- [ ] Unit normalisatie naar kg
- [ ] Data cleaning en deduplicatie
- [ ] Quality scoring

### Module 4: Load Layer (TODO)
- [ ] PostgreSQL database integratie
- [ ] Bulk insert optimalisatie
- [ ] Data versioning
- [ ] API endpoints

### Module 5: LLM Integration (TODO)
- [ ] OpenAI GPT-4 voor unstructured text
- [ ] Prompt engineering voor markt rapporten
- [ ] Fallback naar local LLM

## 📄 Licentie

Proprietary - Ontwikkeld voor commercieel gebruik

## 🤝 Bijdragen

Voor vragen of suggesties, neem contact op met het ontwikkelteam.

## 🐛 Troubleshooting

### Playwright installation errors

```bash
# Linux: Install dependencies
sudo apt-get install libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2

# Reinstall browsers
playwright install --with-deps chromium
```

### Memory issues bij grote PDFs

Verhoog timeout en gebruik streaming:

```python
orchestrator = ScraperOrchestrator(timeout=60000)
```

### Bot detection blocking

- Gebruik `headless=False` voor debugging
- Verlaag scraping frequency
- Implementeer extra delays in custom scrapers

## 📊 Performance

- **Parallel scraping**: 5-10 bronnen tegelijk
- **Average speed**: 2-5 seconden per HTML bron
- **PDF processing**: 5-15 seconden per document
- **Memory usage**: ~100-300 MB per browser instance

---

**Built with** ❤️ **for the European agricultural market**
