# Checklist: Publicatie van LNCN Groenteprijzen Data

## Vraag
Mogen we groenteprijzen data van LNCN (verkregen via jaarlijks abonnement) openbaar publiceren?

## Kritische Vragen die Beantwoord Moeten Worden

### 1. Juridische Aspecten

#### a) Abonnementsvoorwaarden
- [ ] Bekijk de **Terms of Service** van LNCN
- [ ] Controleer het **abonnementscontract** of de licentieovereenkomst
- [ ] Zoek naar clausules over:
  - Databezit en eigendomsrechten
  - Publicatie en redistributie
  - Commercieel vs. niet-commercieel gebruik
  - Toegestane gebruiksdoeleinden

#### b) Intellectueel Eigendom
- [ ] Heeft LNCN copyright of database rechten op deze data?
- [ ] Is de data beschermd onder EU Database Directive?
- [ ] Zijn er sui generis database rechten van toepassing?

#### c) Contact met LNCN
- [ ] **AANBEVELING**: Neem schriftelijk contact op met LNCN
- [ ] Vraag expliciet toestemming voor publicatie
- [ ] Vraag om schriftelijke bevestiging
- [ ] Bespreek de scope: welke data, in welk formaat, voor welk doel

### 2. Technische Overwegingen

#### a) Data Aggregatie/Transformatie
- [ ] Overweeg of je ruwe data of geaggregeerde data publiceert
- [ ] Transformatie kan juridische status veranderen
- [ ] Statistieken of afgeleide werken kunnen andere rechten hebben

#### b) Attributie
- [ ] Plan om LNCN correct te crediteren als bron
- [ ] Vermeld abonnementsvereisten indien relevant
- [ ] Link naar LNCN's officiële bronnen

### 3. Alternatieve Opties

Als directe publicatie niet toegestaan is:

- [ ] Publiceer alleen afgeleide statistieken of analyses
- [ ] Gebruik data intern zonder externe publicatie
- [ ] Vraag LNCN om een speciale licentie voor open data publicatie
- [ ] Zoek naar alternatieve open data bronnen voor groenteprijzen

## Aanbevolen Acties

### STAP 1: Documentatie Review (URGENT)
1. Zoek en lees alle documenten van LNCN:
   - Abonnementsovereenkomst
   - Terms of Service
   - Privacy Policy
   - Data Usage Policy
   - API documentatie (indien van toepassing)

### STAP 2: Schriftelijke Aanvraag
2. Stuur een formele email naar LNCN:

```
Onderwerp: Verzoek tot publicatie van groenteprijzen data

Beste [LNCN contactpersoon],

Wij hebben een abonnement op uw groenteprijzen database en willen graag
de volgende data publiceren: [specificeer welke data].

Het doel is: [leg uit waarom - onderzoek, transparantie, etc.]

De data zou gepubliceerd worden op: [platform/website]
In het formaat: [CSV, API, etc.]
Voor het volgende publiek: [wie krijgt toegang]

Kunnen wij uw schriftelijke toestemming verkrijgen voor deze publicatie?
Zijn er voorwaarden of beperkingen waar we rekening mee moeten houden?

Met vriendelijke groet,
[Uw naam/organisatie]
```

### STAP 3: Wacht op Antwoord
3. **Publiceer NIET** voordat je schriftelijke toestemming hebt

### STAP 4: Documenteer Toestemming
4. Bewaar alle communicatie en toestemmingen in dit project

## Juridisch Risico's bij Ongeautoriseerde Publicatie

⚠️ **WAARSCHUWING**: Publicatie zonder toestemming kan leiden tot:

- Contractbreuk (breach of contract)
- Schending van database rechten
- Juridische claims voor schadevergoeding
- Beëindiging van uw abonnement
- Reputatieschade

## Resultaat van Deze Checklist

Status: ⏳ **IN AFWACHTING VAN VERIFICATIE**

- [ ] Alle relevante documenten zijn gelezen
- [ ] LNCN is gecontacteerd
- [ ] Schriftelijke toestemming is verkregen
- [ ] Voorwaarden zijn begrepen en gedocumenteerd

**CONCLUSIE**: Tot deze stappen zijn voltooid, adviseren we om de data NIET te publiceren.

## Volgende Stappen voor dit Project

Als toestemming wordt verleend:
1. Documenteer de toestemming in `LICENSE.md` of `DATA_LICENSE.md`
2. Implementeer correcte attributie in alle publicaties
3. Volg eventuele voorwaarden van LNCN
4. Stel monitoring in om naleving te waarborgen

Als toestemming wordt geweigerd:
1. Heroverweeg het projectdoel
2. Zoek alternatieve data bronnen
3. Overweeg alleen analyses/statistieken te publiceren
4. Vraag naar een aangepaste licentie
