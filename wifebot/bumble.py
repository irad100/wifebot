"""
Bumble dating platform implementation.
"""

from .platform import Platform
from .loader import load_prompt


class BumblePlatform(Platform):
    """Bumble dating platform implementation."""
    
    def __init__(self, **kwargs):
        """Initialize Bumble platform with configuration options."""
        super().__init__(**kwargs)
    
    @property
    def name(self) -> str:
        return 'bumble'
    
    @property
    def url(self) -> str:
        return 'https://bumble.com/app'
    
    @property
    def platform_instructions(self) -> str:
        return load_prompt('bumble_instructions')
