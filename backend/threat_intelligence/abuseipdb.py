"""AbuseIPDB threat intelligence integration"""

import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

API_KEY = os.getenv("ABUSEIPDB_API_KEY", "")
URL = "https://api.abuseipdb.com/api/v2/check"
TIMEOUT = 10


def check_ip(ip_address: str) -> Dict[str, Any]:
    """
    Check IP reputation on AbuseIPDB
    
    Args:
        ip_address: IPv4 address to check
        
    Returns:
        Dictionary with reputation data or error
    """
    if not API_KEY:
        return {
            "provider": "AbuseIPDB",
            "configured": False,
            "ip": ip_address,
            "message": "API key not configured"
        }

    try:
        headers = {
            "Key": API_KEY,
            "Accept": "application/json"
        }

        params = {
            "ipAddress": ip_address,
            "maxAgeInDays": 90
        }

        response = requests.get(
            URL,
            headers=headers,
            params=params,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"AbuseIPDB check completed for {ip_address}")
        return result

    except requests.exceptions.Timeout:
        logger.error(f"AbuseIPDB timeout for {ip_address}")
        return {
            "provider": "AbuseIPDB",
            "error": "Request timeout",
            "ip": ip_address
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"AbuseIPDB error for {ip_address}: {str(e)}")
        return {
            "provider": "AbuseIPDB",
            "error": str(e),
            "ip": ip_address
        }
    except Exception as e:
        logger.error(f"AbuseIPDB unexpected error: {str(e)}")
        return {
            "provider": "AbuseIPDB",
            "error": "Unexpected error",
            "ip": ip_address
        }
