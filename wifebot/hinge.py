"""
Hinge dating platform implementation.
"""

from .platform import Platform
from .config_loader import load_prompt


class HingePlatform(Platform):
    """Hinge dating platform implementation."""
    
    def __init__(self, **kwargs):
        """Initialize Hinge platform with configuration options."""
        super().__init__(**kwargs)
    
    @property
    def name(self) -> str:
        return 'hinge'
    
    @property
    def url(self) -> str:
        return 'https://hinge.co/discover'
    
    @property
    def platform_instructions(self) -> str:
        return load_prompt('hinge_instructions')

