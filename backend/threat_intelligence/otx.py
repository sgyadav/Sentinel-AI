"""AlienVault OTX threat intelligence integration"""

import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

API_KEY = os.getenv("ALIENVAULT_OTX_API_KEY", "")
URL = "https://otx.alienvault.com/api/v1/indicators/IPv4"
TIMEOUT = 10


def check_ip(ip_address: str) -> Dict[str, Any]:
    """
    Check IP reputation on AlienVault OTX
    
    Args:
        ip_address: IPv4 address to check
        
    Returns:
        Dictionary with threat data or error
    """
    if not API_KEY:
        return {
            "provider": "AlienVault OTX",
            "configured": False,
            "ip": ip_address,
            "message": "API key not configured"
        }

    try:
        headers = {"X-OTX-API-KEY": API_KEY}
        endpoint = f"{URL}/{ip_address}/general"

        response = requests.get(
            endpoint,
            headers=headers,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"AlienVault OTX check completed for {ip_address}")
        return result

    except requests.exceptions.Timeout:
        logger.error(f"AlienVault OTX timeout for {ip_address}")
        return {
            "provider": "AlienVault OTX",
            "error": "Request timeout",
            "ip": ip_address
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"AlienVault OTX error for {ip_address}: {str(e)}")
        return {
            "provider": "AlienVault OTX",
            "error": str(e),
            "ip": ip_address
        }
    except Exception as e:
        logger.error(f"AlienVault OTX unexpected error: {str(e)}")
        return {
            "provider": "AlienVault OTX",
            "error": "Unexpected error",
            "ip": ip_address
        }
