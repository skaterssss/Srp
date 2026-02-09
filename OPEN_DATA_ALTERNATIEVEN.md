# Open Data Alternatieven voor Groenteprijzen

## Overzicht

Als LNCN publicatie niet toestaat, zijn er verschillende open data bronnen beschikbaar voor groenteprijzen. Dit document geeft een overzicht van beschikbare bronnen, specifiek voor **uien**, **aardappelen** en **peen/wortels**.

---

## 🇪🇺 EU DG AGRI - Agriculture and Rural Development

### Agricultural Markets Observatory (AMO)

**Website**: https://agriculture.ec.europa.eu/data-and-analysis/markets/price-data_en

**Licentie**: ✅ **OPEN DATA** - Vrij te gebruiken en publiceren

### Beschikbare Data per Groentesoort

#### 🧅 Uien (Onions)

**Beschikbaarheid**: ✅ **JA** - DG AGRI heeft uitgebreide ui data

**Data Types**:
- **Marktprijzen (Market Prices)**
  - Producer prices (producentenprijzen)
  - Wholesale prices (groothandelsprijzen)
  - Import/export prices
  
- **Geografische Coverage**:
  - EU-brede data
  - Per lidstaat (inclusief Nederland)
  - Belangrijke productie regio's
  
- **Frequentie**: 
  - Weekly (wekelijks)
  - Monthly (maandelijks)
  - Annual statistics (jaarlijkse statistieken)

- **Historische Data**:
  - Meestal vanaf 2010-2015
  - Sommige datasets terug tot vroegere jaren

- **Formats**:
  - Excel (XLSX)
  - CSV
  - PDF rapporten
  - Interactive dashboards

**Specifieke Data Velden**:
```
- Datum/Periode
- Land/Regio
- Prijs (EUR per 100kg of per ton)
- Prijs type (producer/wholesale/retail)
- Kwaliteitsklasse (indien beschikbaar)
- Volume data (productie, import, export)
- Voorraden (stocks)
```

**AMO Sectie**: Fruit and Vegetables > Onions

---

#### 🥔 Aardappelen (Potatoes)

**Beschikbaarheid**: ✅ **JA** - Zeer uitgebreide aardappel data

**Data Types**:
- **Marktprijzen**
  - Producer prices (boerderijprijzen)
  - Wholesale prices
  - Consumer prices (consumenten prijzen)
  - Processing potato prices (industrie aardappelen)
  - Seed potato prices (pootaardappelen)
  
- **Product Categorieën**:
  - Consumption potatoes (consumptie aardappelen)
  - Seed potatoes (pootaardappelen)
  - Starch potatoes (zetmeel aardappelen)
  - Per variëteit (bijvoorbeeld Bintje, Charlotte, etc.)

- **Geografische Coverage**:
  - Alle EU lidstaten
  - Nederland zeer gedetailleerd (belangrijke producent)
  - UK data (pre/post Brexit)
  
- **Frequentie**: 
  - Weekly prices (zeer actueel)
  - Monthly aggregates
  - Annual production statistics

- **Historische Data**:
  - Uitgebreide historische series
  - Vaak vanaf 2000 of eerder

- **Formats**:
  - Excel/CSV
  - Interactive price dashboards
  - Time series data
  - Comparative analyses

**Specifieke Data Velden**:
```
- Datum/Periode
- Land/Regio
- Prijs (EUR per 100kg)
- Aardappel type (consumptie/poot/zetmeel)
- Variëteit (indien gespecificeerd)
- Kwaliteit
- Productie volumes
- Import/Export volumes en prijzen
- Storage levels (opslag)
- Processing volumes
```

**AMO Sectie**: Arable Crops > Potatoes

**Extra Bron**: 
- **NEPG (North-Western European Potato Growers)** data is vaak geïntegreerd
- **Eurostat** heeft aanvullende productie statistieken

---

#### 🥕 Peen/Wortels (Carrots)

**Beschikbaarheid**: ⚠️ **BEPERKT** - Minder uitgebreid dan uien/aardappelen

**Data Types**:
- **Marktprijzen**
  - Wholesale prices (beschikbaar maar beperkt)
  - Minder gedetailleerd dan uien/aardappelen
  
- **Geografische Coverage**:
  - EU-breed
  - Focus op belangrijkste producenten (NL, FR, DE, PL)
  
- **Frequentie**: 
  - Monthly (maandelijks)
  - Niet altijd weekly beschikbaar

- **Historische Data**:
  - Beperkter dan andere producten
  - Vaak vanaf 2015

- **Formats**:
  - Excel/CSV
  - Onderdeel van "Fresh Vegetables" categorie

**Specifieke Data Velden**:
```
- Datum/Periode  
- Land/Regio
- Prijs (EUR per 100kg)
- Productie volumes (jaarlijks)
- Import/Export data
- Beperkte kwaliteitsclassificatie
```

**AMO Sectie**: Fruit and Vegetables > Fresh Vegetables (Carrots als subcategorie)

**Let op**: Voor peen/wortels is de data minder granulair dan voor uien en aardappelen. Mogelijk zijn nationale bronnen (zoals CBS Nederland) completer.

---

## Vergelijking: DG AGRI vs LNCN

| Aspect | DG AGRI | LNCN |
|--------|---------|------|
| **Licentie** | ✅ Open Data (vrij te gebruiken) | ❌ Betaald abonnement, restricted |
| **Coverage Aardappelen** | ✅ Uitstekend | ? |
| **Coverage Uien** | ✅ Goed | ? |
| **Coverage Peen** | ⚠️ Beperkt | ? |
| **Frequentie** | Weekly/Monthly | ? (waarschijnlijk daily/weekly) |
| **Granulariteit** | EU/National level | ? (mogelijk meer lokaal) |
| **Historische Data** | Uitstekend (10+ jaar) | ? |
| **Kwaliteitsklassen** | Beperkt | ? (mogelijk gedetailleerder) |
| **Nederlandse Focus** | EU-breed, NL data beschikbaar | ? (mogelijk meer NL focus) |
| **Actualiteit** | 1-2 weken vertraging | ? (mogelijk actueler) |
| **Variëteiten** | Beperkt | ? (mogelijk gedetailleerder) |

**Conclusie**: 
- DG AGRI is **excellent voor aardappelen**
- DG AGRI is **goed voor uien**
- DG AGRI is **beperkt voor peen** (aanvullende bronnen aanbevolen)
- Voor zeer gedetailleerde, actuele Nederlandse data kan LNCN meer bieden (maar vereist toestemming)

---

## Hoe Toegang te Krijgen tot DG AGRI Data

### Methode 1: Web Interface (Simpel)

1. **Bezoek**: https://agriculture.ec.europa.eu/data-and-analysis/markets/price-data_en
2. **Navigate naar**: 
   - Arable Crops > Potatoes
   - Fruit and Vegetables > Onions
   - Fruit and Vegetables > Fresh Vegetables
3. **Download**: Excel of CSV bestanden
4. **Gebruik**: Geen registratie vereist, open data

### Methode 2: Data Portal (Bulk Download)

1. **Bezoek**: https://agridata.ec.europa.eu/
2. **Explore**: Agricultural Markets datasets
3. **Download**: Bulk data exports
4. **API**: Mogelijk API toegang (check documentatie)

### Methode 3: Eurostat (Aanvullend)

1. **Website**: https://ec.europa.eu/eurostat/data/database
2. **Section**: Agriculture > Agricultural production > Crops products
3. **Data**: 
   - Production volumes
   - Producer prices
   - Less frequent than AMO, but good for annual statistics

---

## Andere Open Data Bronnen

### 🇳🇱 CBS (Centraal Bureau voor de Statistiek)

**Website**: https://opendata.cbs.nl/

**Relevante Datasets**:
- **Aardappelen**: Uitgebreide Nederlandse data
  - StatLine table: "Landbouw; gewassen, dieren, grondgebruik, naar regio"
  - Prijzen, productie, areaal
  
- **Groenten (algemeen)**: 
  - Productie statistieken
  - Prijsindices (geaggregeerd)
  - Minder gedetailleerd dan DG AGRI voor individuele groenten

**Frequentie**: Meestal quarterly of annual

**Voordeel**: Nederlandse focus, betrouwbaar

**Nadeel**: Minder frequent dan DG AGRI market data

**Licentie**: ✅ Open Data

---

### 🌍 FAO (Food and Agriculture Organization - UN)

**Website**: https://www.fao.org/faostat/en/

**FAOSTAT Database**:

**Beschikbaar voor Uien, Aardappelen, Peen**:
- Producer prices (global)
- Production volumes
- Trade data (import/export)
- Per country data

**Frequentie**: Annual (niet voor real-time prices)

**Coverage**: Wereldwijd (180+ countries)

**Voordeel**: 
- Globale context
- Lange historische series (decades)
- Zeer betrouwbaar

**Nadeel**: 
- Niet real-time
- Less granular than EU data voor Europa

**Licentie**: ✅ Open Data (CC BY-NC-SA 3.0 IGO)

---

### 🇪🇺 Eurostat

**Website**: https://ec.europa.eu/eurostat/data/database

**Relevante Data**:
- Agricultural production statistics
- Producer price indices
- Annual production volumes
- Trade data

**Voor Uien/Aardappelen/Peen**: Ja, beschikbaar

**Frequentie**: Monthly to Annual (depends on dataset)

**Voordeel**: 
- Officiële EU statistieken
- Zeer betrouwbaar
- Geharmoniseerde methodologie

**Nadeel**: 
- Minder frequent dan AMO
- Meer statistische aggregaties dan markt prijzen

**Licentie**: ✅ Open Data

---

### 🇳🇱 RVO (Rijksdienst voor Ondernemend Nederland)

**Website**: https://www.rvo.nl/

**Data**: 
- Landbouw gerelateerde data
- Mogelijk subsidie gerelateerde statistieken
- Minder focus op prijzen

**Status**: Check voor actuele datasets

**Licentie**: Overheidsdata, meestal open

---

### 🥔 NEPG (North-Western European Potato Growers)

**Website**: http://www.nepg.org/

**Specifiek voor Aardappelen**:
- Market reports
- Price data voor NW Europa (NL, BE, DE, FR, UK)
- Weekly market commentaries

**Data Beschikbaarheid**:
- Sommige data vrij toegankelijk
- Gedetailleerde rapporten mogelijk voor leden
- Check licentie voorwaarden per dataset

**Focus**: Specifiek aardappelen in NW Europa

---

## Data Vergelijking Tabel

| Bron | Uien | Aardappelen | Peen | Frequentie | Licentie | Nederlandse Focus |
|------|------|-------------|------|------------|----------|-------------------|
| **DG AGRI AMO** | ✅ Uitstekend | ✅ Uitstekend | ⚠️ Beperkt | Weekly/Monthly | ✅ Open | ✅ Ja |
| **CBS** | ⚠️ Beperkt | ✅ Goed | ⚠️ Beperkt | Quarterly/Annual | ✅ Open | ✅✅ Excellent |
| **FAO** | ✅ Goed | ✅ Goed | ✅ Goed | Annual | ✅ Open | ⚠️ Globaal |
| **Eurostat** | ✅ Goed | ✅ Goed | ✅ Goed | Monthly/Annual | ✅ Open | ⚠️ EU-breed |
| **NEPG** | ❌ Nee | ✅ Excellent | ❌ Nee | Weekly | ⚠️ Check | ✅ Ja (NW EU) |
| **LNCN** | ? | ? | ? | ? | ❌ Restricted | ✅ Waarschijnlijk |

---

## Aanbevelingen per Groentesoort

### 🥔 Voor Aardappelen

**Primaire Bron**: DG AGRI AMO
- Uitstekende dekking
- Weekly updates
- Historische data
- Gratis en open

**Aanvullend**: 
- NEPG voor NW Europese focus
- CBS voor Nederlandse productie statistieken
- Eurostat voor EU-brede context

**Conclusie**: ✅ **Uitstekende open data beschikbaar - LNCN niet noodzakelijk**

---

### 🧅 Voor Uien

**Primaire Bron**: DG AGRI AMO
- Goede dekking
- Weekly/Monthly data
- EU-breed inclusief Nederland
- Gratis en open

**Aanvullend**: 
- CBS voor Nederlandse specifieke data
- FAO voor globale context

**Conclusie**: ✅ **Goede open data beschikbaar - LNCN toestemming mogelijk niet nodig**

---

### 🥕 Voor Peen/Wortels

**Primaire Bron**: Combinatie nodig

**Aanbevolen Aanpak**:
1. **DG AGRI AMO** - Basisdata (beperkt)
2. **CBS** - Nederlandse productie en prijsindices
3. **Eurostat** - EU context
4. **FAO** - Globale data en historische series

**Probleem**: Geen enkele open bron is echt uitgebreid voor peen

**Conclusie**: ⚠️ **Open data beperkt - LNCN zou toegevoegde waarde kunnen hebben**

**Alternatief**: 
- Focus op aardappelen en uien (excellent open data)
- Peen alleen als LNCN toestemming geeft
- Of: gebruik beperktere CBS/Eurostat data voor peen

---

## Praktische Implementatie

### Optie 1: Pure Open Data Benadering

**Strategy**: Gebruik alleen open data bronnen

**Implementatie**:
```
Data Pipeline:
1. Ingest DG AGRI data (automated weekly)
   - Aardappelen: Excellent coverage
   - Uien: Good coverage
   - Peen: Supplemented with CBS/Eurostat

2. Enrich with CBS data (quarterly)
   - Nederlandse context
   - Productie statistieken

3. Add FAO data (annually)
   - Historische series
   - Globale vergelijking

4. Publish freely (no license restrictions)
```

**Voordelen**:
- ✅ Geen juridische risico's
- ✅ Volledig vrij te publiceren
- ✅ Betrouwbare bronnen
- ✅ Geen abonnementskosten

**Nadelen**:
- ❌ Mogelijk minder gedetailleerd dan LNCN
- ❌ Mogelijk minder actueel (1-2 weken vertraging)
- ❌ Peen data beperkt

---

### Optie 2: Hybride Benadering (met LNCN toestemming)

**Strategy**: Open data als basis, LNCN voor toegevoegde waarde

**Implementatie**:
```
Base Layer: Open Data
- DG AGRI voor EU context
- CBS voor Nederlandse baselines

Enhanced Layer: LNCN (if permitted)
- Meer gedetailleerde Nederlandse prijzen
- Dagelijkse updates
- Meer kwaliteitsklassen
- Meer variëteiten
```

**Vereist**: Toestemming van LNCN voor enhanced layer

---

### Optie 3: Focus Strategie

**Strategy**: Focus op producten met beste open data

**Implementatie**:
```
Phase 1: Launch met Aardappelen + Uien
- Excellent open data beschikbaar
- Geen juridische blokkades
- Snelle time-to-market

Phase 2: Add Peen later
- Zodra betere data beschikbaar
- Of: na LNCN toestemming
```

**Voordelen**:
- ✅ Geen vertraging
- ✅ Focus op beste data
- ✅ Iteratieve approach

---

## Data Kwaliteit Beoordeling

### DG AGRI AMO Kwaliteit

**Sterke Punten**:
- ✅ Officiële EU bron - zeer betrouwbaar
- ✅ Gestandaardiseerde methodologie
- ✅ Regelmatige updates
- ✅ Lange historische series
- ✅ Goed gedocumenteerd
- ✅ Multiple formats beschikbaar

**Beperkingen**:
- ⚠️ 1-2 weken vertraging vs real-time
- ⚠️ EU/nationale level (niet lokaal)
- ⚠️ Beperkte variëteit details
- ⚠️ Peen minder uitgebreid

**Metadata Beschikbaarheid**: Uitstekend
- Methodologie gedocumenteerd
- Data sources transparant
- Update frequentie duidelijk

---

## Attributie en Gebruik

### DG AGRI Data

**Licentie**: European Commission - Open Data

**Vereiste Attributie**:
```
Data Source: European Commission, 
DG Agriculture and Rural Development
Agricultural Markets Observatory (AMO)
https://agriculture.ec.europa.eu/data-and-analysis/markets/price-data_en

Last updated: [DATE]
License: Open Data - free to use and share
```

**Toegestaan Gebruik**:
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ No permission needed
- ✅ Can be combined with other data

**Restrictions**: 
- Minimal (basic attribution required)
- No misrepresentation

---

## Technische Toegang

### DG AGRI API/Bulk Access

**Status**: Check current API availability

**Opties**:
1. **Manual Download**: Excel/CSV from website
2. **Automated Scraping**: Mogelijk but check robots.txt
3. **API Access**: Check agridata.ec.europa.eu for API docs
4. **Bulk Download**: Request from DG AGRI if available

**Contact voor Bulk Access**:
- AGRI-MARKETS@ec.europa.eu
- Voor automated access permissions

---

## Volgende Stappen

### Immediate Actions

1. **[HIGH]** Verken DG AGRI AMO website:
   - Check actuele data beschikbaarheid voor uien/aardappelen/peen
   - Download sample datasets
   - Assess data kwaliteit

2. **[HIGH]** Evaluate of open data voldoende is voor je use case:
   - Vergelijk met je requirements
   - Beslis of LNCN echt nodig is

3. **[MEDIUM]** Als open data voldoende is:
   - Skip LNCN toestemming proces
   - Begin direct met implementatie
   - Gebruik pure open data approach

4. **[MEDIUM]** Als LNCN toegevoegde waarde heeft:
   - Contacteer LNCN zoals gedocumenteerd
   - Gebruik open data als fallback
   - Hybrid approach

---

## Conclusie

### Direct Antwoord op Uw Vraag

> "Heeft europa dg agri relevant data voor uien aardappel en peen?"

**Antwoord**: 

**Aardappelen**: ✅ **JA** - Uitstekende data beschikbaar
- Weekly prices
- Multiple categories (consumption/seed/starch)
- Extensive historical data
- EU + national level
- **Aanbeveling**: DG AGRI is excellent voor aardappelen

**Uien**: ✅ **JA** - Goede data beschikbaar  
- Weekly/monthly prices
- EU + national level
- Good historical coverage
- **Aanbeveling**: DG AGRI is goed voor uien

**Peen**: ⚠️ **BEPERKT** - Data beschikbaar maar minder uitgebreid
- Monthly prices (not always weekly)
- Less granular than potatoes/onions
- Limited variety information
- **Aanbeveling**: Combineer DG AGRI + CBS + Eurostat voor peen

### Overall Conclusie

Voor een project met **aardappelen** en **uien** is DG AGRI AMO een **excellent open data alternatief** en je hebt mogelijk **geen LNCN toestemming nodig**.

Voor **peen** is de open data situatie **complexer** - mogelijk biedt LNCN hier meer toegevoegde waarde.

---

**Laatste Update**: 9 februari 2026  
**Status**: Initial assessment - verify actuele data beschikbaarheid  
**Next**: Hands-on exploration van DG AGRI datasets
