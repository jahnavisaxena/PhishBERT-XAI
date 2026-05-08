"""
URL Analyzer — VirusTotal-style heuristic analysis.

Provides multiple independent security checks on a URL,
returning structured results similar to a multi-engine scan.
"""

import re
import math
from urllib.parse import urlparse, parse_qs
from collections import Counter


SUSPICIOUS_TLDS = {
    '.tk', '.ml', '.ga', '.cf', '.gq', '.buzz', '.top', '.xyz',
    '.club', '.work', '.date', '.loan', '.racing', '.win', '.bid',
    '.stream', '.click', '.link', '.gdn', '.science', '.party',
    '.review', '.country', '.cricket', '.accountant', '.faith',
}

URL_SHORTENERS = {
    'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'is.gd', 'cli.gs',
    'ow.ly', 'buff.ly', 'adf.ly', 'bc.vc', 'j.mp', 'rb.gy',
    'cutt.ly', 'shorturl.at', 'v.gd', 'x.co', 'su.pr', 'soo.gd',
}

BRAND_KEYWORDS = [
    'paypal', 'apple', 'google', 'microsoft', 'amazon', 'facebook',
    'netflix', 'instagram', 'linkedin', 'twitter', 'chase', 'bank',
    'wellsfargo', 'citibank', 'hsbc', 'dropbox', 'icloud', 'outlook',
    'office365', 'steam', 'whatsapp', 'telegram', 'discord',
]

PHISHING_KEYWORDS = [
    'login', 'signin', 'sign-in', 'verify', 'secure', 'account',
    'update', 'confirm', 'suspend', 'unlock', 'alert', 'urgent',
    'password', 'credential', 'authenticate', 'billing', 'expire',
    'validate', 'restore', 'recovery', 'webscr', 'cmd=login',
]


def shannon_entropy(s: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not s:
        return 0.0
    freq = Counter(s)
    length = len(s)
    return -sum((c / length) * math.log2(c / length) for c in freq.values())


def analyze_url(raw_url: str) -> dict:
    """
    Run multiple heuristic checks on a URL and return
    structured analysis similar to VirusTotal.
    """
    url = raw_url.strip()

    parse_url = url if '://' in url else f'http://{url}'
    parsed = urlparse(parse_url)

    domain = parsed.hostname or ''
    path = parsed.path or ''
    query = parsed.query or ''
    full = domain + path + ('?' + query if query else '')

    domain_parts = domain.split('.')
    tld = '.' + domain_parts[-1] if domain_parts else ''
    subdomain_count = max(0, len(domain_parts) - 2)

    components = {
        "scheme": parsed.scheme or "none",
        "domain": domain,
        "subdomain_count": subdomain_count,
        "tld": tld,
        "path": path if path != '/' else "none",
        "query_params": len(parse_qs(query)),
        "port": parsed.port,
        "full_length": len(raw_url),
    }

    checks = []

    has_https = raw_url.lower().startswith('https://')
    checks.append({
        "name": "SSL / HTTPS",
        "status": "pass" if has_https else ("info" if '://' not in raw_url else "fail"),
        "detail": "Uses HTTPS encryption" if has_https else "No HTTPS detected",
    })

    url_len = len(raw_url)
    if url_len > 100:
        checks.append({"name": "URL Length", "status": "fail", "detail": f"Suspiciously long ({url_len} chars)"})
    elif url_len > 54:
        checks.append({"name": "URL Length", "status": "warn", "detail": f"Moderately long ({url_len} chars)"})
    else:
        checks.append({"name": "URL Length", "status": "pass", "detail": f"Normal length ({url_len} chars)"})

    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    if ip_pattern.match(domain):
        checks.append({"name": "IP Address", "status": "fail", "detail": "Domain is a raw IP address"})
    else:
        checks.append({"name": "IP Address", "status": "pass", "detail": "Uses a domain name, not raw IP"})

    if tld.lower() in SUSPICIOUS_TLDS:
        checks.append({"name": "TLD Reputation", "status": "warn", "detail": f"TLD '{tld}' is commonly abused"})
    else:
        checks.append({"name": "TLD Reputation", "status": "pass", "detail": f"TLD '{tld}' has normal reputation"})

    if domain.lower() in URL_SHORTENERS:
        checks.append({"name": "URL Shortener", "status": "warn", "detail": f"'{domain}' is a known URL shortener"})
    else:
        checks.append({"name": "URL Shortener", "status": "pass", "detail": "Not a URL shortener"})

    if subdomain_count >= 3:
        checks.append({"name": "Subdomains", "status": "fail", "detail": f"{subdomain_count} subdomains detected"})
    elif subdomain_count >= 2:
        checks.append({"name": "Subdomains", "status": "warn", "detail": f"{subdomain_count} subdomains detected"})
    else:
        checks.append({"name": "Subdomains", "status": "pass", "detail": f"{subdomain_count} subdomain(s)"})

    special_chars = sum(1 for c in domain if c in '-_@!')
    if special_chars >= 3:
        checks.append({"name": "Special Characters", "status": "fail", "detail": f"{special_chars} special chars in domain"})
    elif special_chars >= 1:
        checks.append({"name": "Special Characters", "status": "warn", "detail": f"{special_chars} special char(s) in domain"})
    else:
        checks.append({"name": "Special Characters", "status": "pass", "detail": "No suspicious characters"})

    leetspeak_map = str.maketrans('0134578', 'oieastb')
    normalized_domain = domain.lower().translate(leetspeak_map)
    
    found_brands = [b for b in BRAND_KEYWORDS if b in normalized_domain]
    real_domain = '.'.join(domain_parts[-2:]) if len(domain_parts) >= 2 else domain
    
    spoofed = []
    for b in found_brands:
        if b not in real_domain.lower().replace('.', ''):
            spoofed.append(b)
        elif domain.lower() != normalized_domain:
            spoofed.append(f"{b} (Typosquat)")

    if spoofed:
        checks.append({"name": "Brand Impersonation", "status": "fail", "detail": f"Impersonating: {', '.join(spoofed)}"})
    elif found_brands:
        checks.append({"name": "Brand Impersonation", "status": "pass", "detail": f"Legitimate brand domain"})
    else:
        checks.append({"name": "Brand Impersonation", "status": "pass", "detail": "No brand keywords detected"})

    found_phish = [k for k in PHISHING_KEYWORDS if k in full.lower()]
    if len(found_phish) >= 2:
        checks.append({"name": "Phishing Keywords", "status": "fail", "detail": f"Found: {', '.join(found_phish[:4])}"})
    elif len(found_phish) == 1:
        checks.append({"name": "Phishing Keywords", "status": "warn", "detail": f"Found: {found_phish[0]}"})
    else:
        checks.append({"name": "Phishing Keywords", "status": "pass", "detail": "No phishing keywords"})

    entropy = shannon_entropy(domain)
    if entropy > 4.0:
        checks.append({"name": "Domain Entropy", "status": "warn", "detail": f"High randomness ({entropy:.2f} bits)"})
    else:
        checks.append({"name": "Domain Entropy", "status": "pass", "detail": f"Normal entropy ({entropy:.2f} bits)"})

    has_unicode = any(ord(c) > 127 for c in domain)
    if has_unicode:
        checks.append({"name": "Unicode / IDN", "status": "warn", "detail": "Contains non-ASCII characters (possible homoglyph)"})
    else:
        checks.append({"name": "Unicode / IDN", "status": "pass", "detail": "ASCII-only domain"})

    if '@' in raw_url:
        checks.append({"name": "URL Obfuscation", "status": "fail", "detail": "Contains @ symbol (may hide real destination)"})
    else:
        checks.append({"name": "URL Obfuscation", "status": "pass", "detail": "No URL obfuscation detected"})

    fail_count = sum(1 for c in checks if c['status'] == 'fail')
    warn_count = sum(1 for c in checks if c['status'] == 'warn')
    total = len(checks)
    threat_score = min(100, int(((fail_count * 2 + warn_count) / (total * 2)) * 100))

    if threat_score >= 40:
        risk_level = "High"
    elif threat_score >= 20:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "components": components,
        "checks": checks,
        "summary": {
            "total_checks": total,
            "passed": sum(1 for c in checks if c['status'] == 'pass'),
            "warnings": warn_count,
            "failed": fail_count,
            "threat_score": threat_score,
            "risk_level": risk_level,
        }
    }
