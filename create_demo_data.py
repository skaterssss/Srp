"""Create demo data for dashboard testing"""

import json
from datetime import date, timedelta
import random
from pathlib import Path

# Create output directory
Path("output").mkdir(exist_ok=True)

# Generate demo prices
varieties = {
    'Potato': ['Agria', 'Fontane', 'Lady Claire', 'Markies', 'Victoria'],
    'Onion': ['Red Baron', 'Sturon', 'Yellow Globe', 'White Pearl'],
    'Carrot': ['Nantes', 'Chantenay', 'Imperator']
}

countries = ['NL', 'DE', 'BE', 'PL', 'GB']
currencies = {'NL': 'EUR', 'DE': 'EUR', 'BE': 'EUR', 'PL': 'PLN', 'GB': 'GBP'}
units = ['100kg', 'kg', 'ton']

demo_results = []

for country in countries:
    prices = []
    for commodity, vars in varieties.items():
        for variety in random.sample(vars, min(3, len(vars))):
            base_price = random.uniform(10, 50)
            for i in range(3):  # 3 price points per variety
                price_date = (date.today() - timedelta(days=i*7)).isoformat()
                prices.append({
                    'date': price_date,
                    'commodity': commodity,
                    'variety': variety,
                    'price': round(base_price + random.uniform(-5, 5), 2),
                    'currency': currencies[country],
                    'unit': random.choice(units),
                    'source_id': f'{country.lower()}_demo',
                    'country': country,
                    'quality_grade': random.choice(['Class I', 'Class II', None])
                })
    
    demo_results.append({
        'source_id': f'{country.lower()}_demo',
        'success': True,
        'records_found': len(prices),
        'error': None,
        'prices': prices
    })

# Add one failed source for realism
demo_results.append({
    'source_id': 'fr_demo',
    'success': False,
    'records_found': 0,
    'error': 'Connection timeout',
    'prices': []
})

total_records = sum(r['records_found'] for r in demo_results)
successful = sum(1 for r in demo_results if r['success'])

output_data = {
    'metadata': {
        'scraped_at': date.today().isoformat() + 'T12:00:00',
        'total_sources': len(demo_results),
        'successful_sources': successful,
        'total_records': total_records
    },
    'results': demo_results
}

# Save to file
with open('output/prices.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"✅ Demo data created!")
print(f"   - {len(demo_results)} sources")
print(f"   - {successful} successful")
print(f"   - {total_records} price records")
print(f"   - Saved to output/prices.json")
