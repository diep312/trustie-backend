import requests
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup
import tldextract
import warnings
from fake_useragent import UserAgent
import os
import json
from pathlib import Path


# Suppress SSL warnings (not recommended for production)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

class SafeScraper:
    def __init__(self, keywords_file="sus_keyword.json"):
        self.user_agent = UserAgent()
        self.keywords_file = keywords_file
        self.suspicious_keywords = self.load_keywords()
    
    def load_keywords(self):
        """
        Load suspicious keywords from a text file
        Supports both .txt (one per line) and .json formats
        Creates default file if none exists
        """
        # Default keywords if file doesn't exist
        default_keywords = [
            'login', 'password', 'bank', 'paypal', 'verify',
            'account', 'secure', 'update', 'phishing', 'scam',
            'credential', 'social security', 'ssn', 'password',
            'username', 'click here', 'limited time', 'offer',
            'prize', 'winner', 'urgent', 'suspended', 'locked'
        ]
        
        try:
            # Create directory if needed
            Path(self.keywords_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Create default file if it doesn't exist
            if not os.path.exists(self.keywords_file):
                with open(self.keywords_file, 'w') as f:
                    f.write("\n".join(default_keywords))
                return default_keywords
            
            # Check file extension for appropriate parsing
            if self.keywords_file.endswith('.json'):
                with open(self.keywords_file, 'r') as f:
                    return json.load(f)
            else:  # Assume text file
                with open(self.keywords_file, 'r') as f:
                    return [line.strip() for line in f if line.strip()]
                    
        except Exception as e:
            print(f"Warning: Couldn't load keywords file ({e}). Using defaults.")
            return default_keywords
    
    def reload_keywords(self):
        """Hot-reload keywords without restarting"""
        self.suspicious_keywords = self.load_keywords()



    def contains_link(self, text):
        """Improved URL detection with common scam patterns"""
        url_pattern = re.compile(
            r'(https?://[^\s]+|www\.[^\s]+|bit\.ly/[^\s]+|tinyurl\.com/[^\s]+)',
            re.IGNORECASE
        )
        return bool(url_pattern.search(text))
    
    def is_suspicious_domain(self, domain):
        """Check for known suspicious domain patterns"""
        extracted = tldextract.extract(domain)
        return any(
            kw in extracted.domain.lower() or kw in extracted.subdomain.lower()
            for kw in self.suspicious_keywords
        )
    
    def get_website_content(self, text):
        """
        Safely scrape website content with multiple security checks
        Returns: {
            'contains_link': bool,
            'is_accessible': bool,
            'is_suspicious': bool,
            'content': str,
            'error': str,
            'security_checks': dict
        }
        """
        if not self.contains_link(text):
            return {'contains_link': False}
        
        try:
            # Extract URL from text
            url_match = re.search(r'(https?://\S+|www\.\S+)', text, re.IGNORECASE)
            raw_url = url_match.group(0)
            
            # Normalize URL
            if not raw_url.startswith(('http://', 'https://')):
                url = 'https://' + raw_url
            else:
                url = raw_url
            
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Security checks
            security_checks = {
                'is_https': parsed.scheme == 'https',
                'is_suspicious_domain': self.is_suspicious_domain(domain),
                'has_redirects': False,
                'final_url': url
            }
            
            # First make a HEAD request to check safety
            with requests.Session() as session:
                # Configure session with security parameters
                session.max_redirects = 3
                session.timeout = 8
                
                # First request (HEAD) to check redirects
                headers = {'User-Agent': self.user_agent.random}
                response = session.head(
                    url,
                    headers=headers,
                    allow_redirects=True,
                    verify=True  # SSL verification
                )
                
                security_checks.update({
                    'has_redirects': response.url != url,
                    'final_url': response.url,
                    'status_code': response.status_code
                })
                
                # If suspicious domain or too many redirects, abort
                if (security_checks['is_suspicious_domain'] or 
                    response.status_code >= 400):
                    return {
                        'contains_link': True,
                        'is_accessible': False,
                        'is_suspicious': True,
                        'security_checks': security_checks,
                        'error': 'Suspicious domain or inaccessible'
                    }
                
                # Now make the actual GET request with sandboxed parameters
                response = session.get(
                    response.url,  # Follow final URL
                    headers=headers,
                    timeout=10,
                    verify=True,
                    stream=True  # Don't download immediately
                )
                
                # Check content type for safety
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('text/html'):
                    return {
                        'contains_link': True,
                        'is_accessible': True,
                        'is_suspicious': True,
                        'security_checks': security_checks,
                        'error': f'Non-HTML content: {content_type}'
                    }
                
                # Safe parsing with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser', 
                                   from_encoding=response.encoding)
                
                # Remove potentially dangerous elements
                for script in soup(["script", "style", "iframe", "object", "embed"]):
                    script.decompose()
                
                # Get clean text content
                text_content = soup.get_text(separator=' ', strip=True)
                
                return {
                    'contains_link': True,
                    'is_accessible': True,
                    'is_suspicious': security_checks['is_suspicious_domain'],
                    'content': text_content[:5000],  # Limit content size
                    'security_checks': security_checks
                }
        
        except requests.exceptions.SSLError:
            return {
                'contains_link': True,
                'is_accessible': False,
                'is_suspicious': True,
                'error': 'SSL verification failed - potential security risk'
            }
        except Exception as e:
            return {
                'contains_link': True,
                'is_accessible': False,
                'error': str(e)
            }

# # Usage Example
# scraper = SafeScraper()
# sample_text = "Check this site: https://example.com"
# result = scraper.get_website_content(sample_text)

# if result['contains_link'] and result['is_accessible']:
#     print("Scraped content:", result['content'])
#     if result['is_suspicious']:
#         print("⚠️ Warning: Suspicious website detected")