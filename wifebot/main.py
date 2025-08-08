#!/usr/bin/env python3
"""
Main entry point for running dating platform agents.

This script allows you to run agents for different dating platforms:
- Bumble
- Tinder
- Hinge  
- OkCupid

Usage:
    wifebot <platform> [OPTIONS]
    wifebot --interactive [OPTIONS]
    
Examples:
    wifebot bumble --headless
    wifebot tinder --model gpt-4 --verbose
    wifebot hinge --viewport-width 1920 --viewport-height 1080
    wifebot okcupid --min-wait 2 --max-wait 15
    wifebot all --headless --trace-path /tmp/traces
    wifebot --interactive
    
For full list of options: wifebot --help
"""

import asyncio

from wifebot.factory import PlatformFactory


async def async_main():
    """Async main entry point."""
    factory = PlatformFactory()
    parser = factory.setup_argparse()
    args = parser.parse_args()
    await factory.run_from_args(args)


def main():
    """Synchronous main entry point for CLI."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()