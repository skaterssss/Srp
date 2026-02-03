"""
Legal Compliance Checker for Web Scraping

This module checks robots.txt and provides legal compliance assessment
for scraping activities according to EU law and best practices.
"""

import asyncio
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin
import httpx
from loguru import logger

from models import SourceConfig


class LegalComplianceChecker:
    """
    Checks legal compliance for web scraping activities.
    
    Features:
    - robots.txt validation
    - Rate limiting recommendations
    - GDPR compliance notes
    - Terms of Service warnings
    """
    
    def __init__(self, respect_robots_txt: bool = True):
        """
        Initialize compliance checker.
        
        Args:
            respect_robots_txt: Whether to enforce robots.txt rules
        """
        self.respect_robots_txt = respect_robots_txt
        self.robots_cache: Dict[str, Optional[str]] = {}
    
    async def check_source_legality(self, source: SourceConfig) -> Dict:
        """
        Check if scraping a source is legally compliant.
        
        Args:
            source: SourceConfig to check
            
        Returns:
            Dictionary with compliance status and recommendations
        """
        result = {
            'source_id': source.id,
            'url': source.url,
            'legal_status': 'unknown',
            'robots_txt_allows': None,
            'robots_txt_url': None,
            'recommendations': [],
            'warnings': [],
            'gdpr_notes': []
        }
        
        # Check robots.txt
        robots_check = await self._check_robots_txt(source.url)
        result['robots_txt_allows'] = robots_check['allowed']
        result['robots_txt_url'] = robots_check['robots_url']
        
        if not robots_check['allowed']:
            result['legal_status'] = 'blocked'
            result['warnings'].append(
                f"⚠️ robots.txt disallows scraping: {robots_check.get('reason', 'Unknown')}"
            )
        else:
            result['legal_status'] = 'allowed'
        
        # Check if it's public market data (usually legally scrapable)
        if self._is_public_market_data(source):
            result['recommendations'].append(
                "✓ Public market data - generally allowed under fair use"
            )
            if result['legal_status'] == 'unknown':
                result['legal_status'] = 'likely_allowed'
        
        # GDPR compliance notes
        if source.country in ['NL', 'DE', 'BE', 'FR', 'PL']:
            result['gdpr_notes'].append(
                "📋 EU source - Ensure GDPR compliance: no personal data collection"
            )
            result['gdpr_notes'].append(
                "📋 Factual market prices are not personal data (GDPR Article 4)"
            )
        
        # Rate limiting recommendations
        if source.frequency == 'daily':
            result['recommendations'].append(
                "⏱️ Daily frequency: Recommended rate limit 1 request/hour"
            )
        elif source.frequency == 'weekly':
            result['recommendations'].append(
                "⏱️ Weekly frequency: Recommended rate limit 1 request/day"
            )
        
        # User-agent requirement
        result['recommendations'].append(
            "🤖 Always use identifiable User-Agent with contact info"
        )
        
        # Copyright considerations
        result['recommendations'].append(
            "©️ Scraping facts/prices: Generally allowed (Feist v. Rural, EU Database Directive)"
        )
        
        return result
    
    async def _check_robots_txt(self, url: str) -> Dict:
        """
        Check robots.txt for the given URL.
        
        Args:
            url: Website URL to check
            
        Returns:
            Dictionary with robots.txt status
        """
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = urljoin(base_url, '/robots.txt')
        
        # Check cache
        if robots_url in self.robots_cache:
            content = self.robots_cache[robots_url]
        else:
            # Fetch robots.txt
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(robots_url, follow_redirects=True)
                    if response.status_code == 200:
                        content = response.text
                        self.robots_cache[robots_url] = content
                    else:
                        # No robots.txt = implicitly allowed
                        self.robots_cache[robots_url] = None
                        content = None
            except Exception as e:
                logger.warning(f"Could not fetch robots.txt from {robots_url}: {e}")
                content = None
                self.robots_cache[robots_url] = None
        
        result = {
            'robots_url': robots_url,
            'allowed': True,  # Default to allowed if no robots.txt
            'reason': 'No robots.txt found (implicitly allowed)'
        }
        
        if content:
            # Simple robots.txt parsing
            # Check for "Disallow: /" which blocks everything
            if 'Disallow: /' in content:
                # Check if it's under User-agent: *
                lines = content.split('\n')
                applies_to_all = False
                
                for i, line in enumerate(lines):
                    if 'User-agent: *' in line:
                        # Check next lines for Disallow
                        for next_line in lines[i+1:i+10]:
                            if next_line.startswith('User-agent:'):
                                break
                            if 'Disallow: /' in next_line:
                                applies_to_all = True
                                break
                
                if applies_to_all:
                    result['allowed'] = False
                    result['reason'] = 'Disallow: / found for all user agents'
                else:
                    result['allowed'] = True
                    result['reason'] = 'robots.txt present but allows scraping'
            else:
                result['allowed'] = True
                result['reason'] = 'robots.txt allows scraping'
        
        return result
    
    def _is_public_market_data(self, source: SourceConfig) -> bool:
        """
        Check if source provides public market data.
        
        Public market data is generally legally scrapable as it consists
        of factual information without copyright protection.
        
        Args:
            source: SourceConfig to check
            
        Returns:
            True if source provides public market data
        """
        # Keywords indicating public market data
        market_keywords = [
            'market', 'price', 'markt', 'prijs', 'prix',
            'ceny', 'ahdb', 'ami', 'boerderij', 'vegebe'
        ]
        
        url_lower = source.url.lower()
        name_lower = source.name.lower()
        
        return any(keyword in url_lower or keyword in name_lower 
                  for keyword in market_keywords)
    
    async def check_all_sources(self, sources: List[SourceConfig]) -> Dict:
        """
        Check legal compliance for all sources.
        
        Args:
            sources: List of SourceConfig objects
            
        Returns:
            Summary dictionary with all results
        """
        logger.info(f"Checking legal compliance for {len(sources)} sources...")
        
        tasks = [self.check_source_legality(source) for source in sources]
        results = await asyncio.gather(*tasks)
        
        # Create summary
        summary = {
            'total_sources': len(sources),
            'allowed': 0,
            'likely_allowed': 0,
            'blocked': 0,
            'unknown': 0,
            'sources': results
        }
        
        for result in results:
            status = result['legal_status']
            if status == 'allowed':
                summary['allowed'] += 1
            elif status == 'likely_allowed':
                summary['likely_allowed'] += 1
            elif status == 'blocked':
                summary['blocked'] += 1
            else:
                summary['unknown'] += 1
        
        return summary
    
    def print_compliance_report(self, summary: Dict) -> None:
        """
        Print a formatted compliance report.
        
        Args:
            summary: Summary dictionary from check_all_sources
        """
        print("\n" + "="*70)
        print("🔍 LEGAL COMPLIANCE REPORT - WEB SCRAPING")
        print("="*70)
        
        print(f"\n📊 Summary:")
        print(f"  Total sources: {summary['total_sources']}")
        print(f"  ✅ Allowed: {summary['allowed']}")
        print(f"  ⚠️  Likely allowed: {summary['likely_allowed']}")
        print(f"  ❌ Blocked: {summary['blocked']}")
        print(f"  ❓ Unknown: {summary['unknown']}")
        
        print("\n" + "-"*70)
        print("📋 Detailed Source Analysis:")
        print("-"*70)
        
        for source_result in summary['sources']:
            status_icon = {
                'allowed': '✅',
                'likely_allowed': '⚠️',
                'blocked': '❌',
                'unknown': '❓'
            }.get(source_result['legal_status'], '❓')
            
            print(f"\n{status_icon} {source_result['source_id']}")
            print(f"   URL: {source_result['url']}")
            print(f"   Status: {source_result['legal_status'].upper()}")
            
            if source_result.get('robots_txt_url'):
                allows = "✓ Allows" if source_result['robots_txt_allows'] else "✗ Blocks"
                print(f"   robots.txt: {allows}")
            
            if source_result.get('warnings'):
                print(f"\n   ⚠️  Warnings:")
                for warning in source_result['warnings']:
                    print(f"      {warning}")
            
            if source_result.get('recommendations'):
                print(f"\n   💡 Recommendations:")
                for rec in source_result['recommendations']:
                    print(f"      {rec}")
            
            if source_result.get('gdpr_notes'):
                print(f"\n   📋 GDPR Notes:")
                for note in source_result['gdpr_notes']:
                    print(f"      {note}")
        
        print("\n" + "="*70)
        print("⚖️  LEGAL DISCLAIMER:")
        print("="*70)
        print("""
This compliance check is for informational purposes only and does not
constitute legal advice. Consider the following:

1. ✓ Public market prices (facts) generally have no copyright protection
2. ✓ EU Database Directive: Extracting substantial parts requires permission
3. ✓ Respect robots.txt and Terms of Service
4. ✓ Use reasonable rate limiting to avoid server overload
5. ✓ Include contact info in User-Agent header
6. ✓ GDPR: Only collect public, non-personal data
7. ⚠️  Some sites may have specific ToS prohibiting scraping
8. ⚠️  Commercial use may have different legal implications

Recommendation: Consult a legal professional for your specific use case.
        """)
        print("="*70 + "\n")


async def main():
    """Run compliance check on all configured sources."""
    from utils import ConfigLoader, setup_logger
    
    setup_logger(log_level="INFO")
    
    # Load sources
    config_loader = ConfigLoader("config/sources.json")
    sources = config_loader.load_sources()
    
    # Run compliance check
    checker = LegalComplianceChecker(respect_robots_txt=True)
    summary = await checker.check_all_sources(sources)
    
    # Print report
    checker.print_compliance_report(summary)
    
    # Return status code
    if summary['blocked'] > 0:
        print("⚠️  Warning: Some sources are blocked by robots.txt")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
