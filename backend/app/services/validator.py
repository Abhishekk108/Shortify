import ipaddress
import socket
from urllib.parse import urlparse


def validate_url(url: str) -> str:
    """
    Validate and clean a URL string.

    - Strips leading/trailing whitespace.
    - Requires scheme to be 'http' or 'https'.
    - Requires a non-empty host (netloc).

    Returns the cleaned URL string if valid.
    Raises ValueError with a descriptive message if invalid.
    """
    cleaned = url.strip()

    if not cleaned:
        raise ValueError("URL must not be empty.")

    parsed = urlparse(cleaned)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            f"Invalid URL scheme '{parsed.scheme}'. Only 'http' and 'https' are allowed."
        )

    if not parsed.netloc:
        raise ValueError("URL must include a valid host (e.g., example.com).")

    return cleaned


def is_safe_url(url: str) -> bool:
    """
    Check whether the URL's host resolves to a public (non-private) IP address.

    Returns False if the host resolves to a private or loopback address (SSRF protection).
    Returns True if the host appears to be a public address.
    Returns True on socket errors (fail open — don't block unresolvable hosts).

    Private ranges checked:
        - 127.x.x.x   (loopback IPv4)
        - 10.x.x.x    (private class A)
        - 172.16-31.x (private class B)
        - 192.168.x.x (private class C)
        - ::1          (loopback IPv6)
    """
    try:
        parsed = urlparse(url.strip())
        hostname = parsed.hostname  # strips port if present

        if not hostname:
            return True  # can't determine host, fail open

        # Resolve all addresses for the hostname
        addr_infos = socket.getaddrinfo(hostname, None)

        for addr_info in addr_infos:
            # addr_info is (family, type, proto, canonname, sockaddr)
            # sockaddr is (address, port) for IPv4 or (address, port, flow, scope) for IPv6
            raw_addr = addr_info[4][0]
            try:
                ip = ipaddress.ip_address(raw_addr)
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return False
            except ValueError:
                continue  # skip addresses we can't parse

    except socket.error:
        # DNS resolution failed or other socket error — fail open
        return True

    return True
