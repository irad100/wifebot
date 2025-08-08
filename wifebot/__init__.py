"""
WifeBot - Dating platform automation package.
"""

from .platform import Platform
from .bumble import BumblePlatform
from .tinder import TinderPlatform
from .hinge import HingePlatform
from .okcupid import OkCupidPlatform
from .factory import PlatformFactory

__all__ = [
    'Platform',
    'BumblePlatform', 
    'TinderPlatform',
    'HingePlatform',
    'OkCupidPlatform',
    'PlatformFactory',
]

