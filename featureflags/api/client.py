import logging
import ssl
from typing import Dict

import attr


@attr.s(auto_attribs=True)
class Client:
    """A class for keeping track of data related to the API"""

    base_url: str
    events_url: str
    params: Dict[str, str] = attr.ib(factory=dict, kw_only=True)
    cookies: Dict[str, str] = attr.ib(factory=dict, kw_only=True)
    headers: Dict[str, str] = attr.ib(factory=dict, kw_only=True)
    timeout: float = attr.ib(30.0, kw_only=True)
    max_auth_retries: int
    # Used for on-prem
    ssl_context: ssl.SSLContext = attr.ib(factory=ssl.SSLContext, kw_only=True)

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in all endpoints"""
        return {**self.headers}

    def with_headers(self, headers: Dict[str, str]) -> "Client":
        """Get a new client matching this one with additional headers"""
        return attr.evolve(self, headers={**self.headers, **headers})

    def get_params(self) -> Dict[str, str]:
        return {**self.params}

    def get_cookies(self) -> Dict[str, str]:
        return {**self.cookies}

    def with_cookies(self, cookies: Dict[str, str]) -> "Client":
        """Get a new client matching this one with additional cookies"""
        return attr.evolve(self, cookies={**self.cookies, **cookies})

    def with_ssl_context(self, ca_file: str) -> "Client":
        """Get a new client matching this one with custom CA certifications"""
        # Create an SSL context
        context = ssl.create_default_context()

        # Add custom root CA certificates
        context.load_verify_locations(cafile=ca_file)

        # Return a new client with the modified SSL context
        return attr.evolve(self, ssl_context=context)

    def get_timeout(self) -> float:
        return self.timeout

    def get_ssl_context(self) -> ssl.SSLContext:
        return self.ssl_context

    def get_max_auth_retries(self) -> int:
        return self.max_auth_retries

    def with_timeout(self, timeout: float) -> "Client":
        """
        Get a new client matching this one with a new timeout (in seconds)
        """
        return attr.evolve(self, timeout=timeout)


@attr.s(auto_attribs=True)
class AuthenticatedClient(Client):
    """A Client which has been authenticated for use on secured endpoints"""

    token: str

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in authenticated endpoints"""
        return {"Authorization": f"Bearer {self.token}", **self.headers}
