"""
Mobile-Friendly Dashboard for Agri-Market Scraper

Flask web application with real-time updates and mobile-optimized UI.
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Data storage
RESULTS_FILE = Path("/workspace/output/prices.json")
STATUS_FILE = Path("/workspace/output/status.json")


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """Get current scraping status"""
    if STATUS_FILE.exists():
        with open(STATUS_FILE, 'r') as f:
            status = json.load(f)
    else:
        status = {
            'running': False,
            'progress': 0,
            'current_source': None,
            'last_update': None
        }
    return jsonify(status)


@app.route('/api/results')
def get_results():
    """Get scraping results"""
    if not RESULTS_FILE.exists():
        return jsonify({
            'success': False,
            'message': 'No data available yet. Run the scraper first.'
        })
    
    try:
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading data: {str(e)}'
        })


@app.route('/api/summary')
def get_summary():
    """Get summary statistics"""
    if not RESULTS_FILE.exists():
        return jsonify({
            'total_sources': 0,
            'successful': 0,
            'failed': 0,
            'total_prices': 0,
            'by_country': {},
            'by_commodity': {},
            'latest_update': None
        })
    
    try:
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
        
        # Calculate statistics
        metadata = data.get('metadata', {})
        results = data.get('results', [])
        
        # Count by country and commodity
        by_country = {}
        by_commodity = {}
        
        for result in results:
            if result.get('success'):
                for price in result.get('prices', []):
                    country = price.get('country', 'Unknown')
                    commodity = price.get('commodity', 'Unknown')
                    
                    by_country[country] = by_country.get(country, 0) + 1
                    by_commodity[commodity] = by_commodity.get(commodity, 0) + 1
        
        return jsonify({
            'total_sources': metadata.get('total_sources', 0),
            'successful': metadata.get('successful_sources', 0),
            'failed': metadata.get('total_sources', 0) - metadata.get('successful_sources', 0),
            'total_prices': metadata.get('total_records', 0),
            'by_country': by_country,
            'by_commodity': by_commodity,
            'latest_update': metadata.get('scraped_at')
        })
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/api/prices')
def get_prices():
    """Get price list with filtering"""
    if not RESULTS_FILE.exists():
        return jsonify([])
    
    try:
        with open(RESULTS_FILE, 'r') as f:
            data = json.load(f)
        
        # Extract all prices
        all_prices = []
        for result in data.get('results', []):
            if result.get('success'):
                for price in result.get('prices', []):
                    all_prices.append(price)
        
        # Filter by query parameters
        country = request.args.get('country')
        commodity = request.args.get('commodity')
        
        if country:
            all_prices = [p for p in all_prices if p.get('country') == country]
        if commodity:
            all_prices = [p for p in all_prices if p.get('commodity') == commodity]
        
        # Sort by date descending
        all_prices.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Limit to 100 results for mobile
        return jsonify(all_prices[:100])
    
    except Exception as e:
        return jsonify([])


if __name__ == '__main__':
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=True)
