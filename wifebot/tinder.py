"""
Tinder dating platform implementation.
"""

from .platform import Platform
from .loader import load_prompt


class TinderPlatform(Platform):
    """Tinder dating platform implementation."""
    
    def __init__(self, **kwargs):
        """Initialize Tinder platform with configuration options."""
        super().__init__(**kwargs)
    
    @property
    def name(self) -> str:
        return 'tinder'
    
    @property
    def url(self) -> str:
        return 'https://tinder.com/app/recs'
    
    @property
    def platform_instructions(self) -> str:
        return load_prompt('tinder_instructions')
