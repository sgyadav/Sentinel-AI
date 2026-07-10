from threat_intelligence.abuseipdb import check_ip as abuse_check
from threat_intelligence.virustotal import check_ip as vt_check
from threat_intelligence.otx import check_ip as otx_check


def check_reputation(ip_address: str):

    return {

        "ip": ip_address,

        "abuseipdb": abuse_check(ip_address),

        "virustotal": vt_check(ip_address),

        "alienvault": otx_check(ip_address)

    }