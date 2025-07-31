import re
import requests
from urllib.parse import urlparse



class UtilService: 
    @staticmethod 
    def is_contain_link(self, text: str):
        """
        Returns True if the text contains a URL, False otherwise.
        Supports HTTP, HTTPS, and common domain patterns.
        """
        url_pattern = re.compile(
            r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
            r'(?:/[-\w._~:/?#[\]@!$&\'()*+,;=]*)?'
            r'|(?:www\.)[-\w.]+\.[a-z]{2,}(?:/[-\w._~:/?#[\]@!$&\'()*+,;=]*)?',
            re.IGNORECASE
        )

        return bool(url_pattern.search(text))

    @staticmethod
    def is_link_accessible(self, text:str):
        """
        Returns True if the text contains an accessible URL, False otherwise.
        Handles common exceptions and follows redirects.
        """
        if not self.is_contain_link(text):
            return False
            
        try:
            # Extract first URL found in text
            url_match = re.search(
                r'(https?://\S+|www\.\S+)', 
                text, 
                re.IGNORECASE
            )
            
            if not url_match:
                return False
                
            url = url_match.group(0)
            
            # Add https:// if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Validate domain structure
            parsed = urlparse(url)
            if not parsed.netloc:
                return False
                
            # Make HEAD request (faster than GET)
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            return response.status_code < 400
            
        except (requests.RequestException, ValueError):
            return False
