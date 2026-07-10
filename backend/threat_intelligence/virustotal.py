"""VirusTotal threat intelligence integration"""

import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
URL = "https://www.virustotal.com/api/v3/ip_addresses"
TIMEOUT = 10


def check_ip(ip_address: str) -> Dict[str, Any]:
    """
    Check IP reputation on VirusTotal
    
    Args:
        ip_address: IPv4 address to check
        
    Returns:
        Dictionary with reputation data or error
    """
    if not API_KEY:
        return {
            "provider": "VirusTotal",
            "configured": False,
            "ip": ip_address,
            "message": "API key not configured"
        }

    try:
        headers = {"x-apikey": API_KEY}
        endpoint = f"{URL}/{ip_address}"

        response = requests.get(
            endpoint,
            headers=headers,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"VirusTotal check completed for {ip_address}")
        return result

    except requests.exceptions.Timeout:
        logger.error(f"VirusTotal timeout for {ip_address}")
        return {
            "provider": "VirusTotal",
            "error": "Request timeout",
            "ip": ip_address
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"VirusTotal error for {ip_address}: {str(e)}")
        return {
            "provider": "VirusTotal",
            "error": str(e),
            "ip": ip_address
        }
    except Exception as e:
        logger.error(f"VirusTotal unexpected error: {str(e)}")
        return {
            "provider": "VirusTotal",
            "error": "Unexpected error",
            "ip": ip_address
        }
