"""
OkCupid dating platform implementation.
"""

from .platform import Platform
from .loader import load_prompt


class OkCupidPlatform(Platform):
    """OkCupid dating platform implementation."""
    
    def __init__(self, **kwargs):
        """Initialize OkCupid platform with configuration options."""
        super().__init__(**kwargs)
    
    @property
    def name(self) -> str:
        return 'okcupid'
    
    @property
    def url(self) -> str:
        return 'https://www.okcupid.com/discover'
    
    @property
    def platform_instructions(self) -> str:
        return load_prompt('okcupid_instructions')

