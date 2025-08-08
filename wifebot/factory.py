"""
Platform factory for creating and managing dating platform agents.
"""

import argparse
import sys
from typing import Optional, Dict, Any

from .bumble import BumblePlatform
from .tinder import TinderPlatform
from .hinge import HingePlatform
from .okcupid import OkCupidPlatform
from .config_loader import load_config


class PlatformFactory:
    """Factory class for creating and managing dating platform agents."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the factory with platform registry and configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.platforms = {
            'bumble': BumblePlatform,
            'tinder': TinderPlatform,
            'hinge': HingePlatform,
            'okcupid': OkCupidPlatform,
        }
        self.config = load_config(config_path)
        self.config_path = config_path
    
    def get_available_platforms(self) -> list:
        """Get list of available platform names."""
        return list(self.platforms.keys())
    
    def create_platform(self, platform_name: str, **kwargs):
        """Create a platform instance by name with configuration."""
        if platform_name not in self.platforms:
            raise ValueError(f"Unknown platform: {platform_name}. Available: {self.get_available_platforms()}")
        
        return self.platforms[platform_name](**kwargs)
    
    async def run_single_platform(self, platform_name: str, **kwargs):
        """Run a single dating platform agent."""
        print(f"Starting {platform_name.upper()} dating agent...")
        try:
            platform = self.create_platform(platform_name, **kwargs)
            await platform.run()
            print(f"{platform_name.upper()} agent completed successfully.")
        except Exception as e:
            print(f"Error running {platform_name.upper()} agent: {e}")
            raise
    
    async def run_all_platforms(self, **kwargs):
        """Run agents for all platforms sequentially."""
        platforms = self.get_available_platforms()
        print(f"Running agents for all platforms: {', '.join(platforms)}")
        
        for platform in platforms:
            print(f"\n{'='*50}")
            print(f"Starting {platform.upper()} agent...")
            print('='*50)
            
            try:
                await self.run_single_platform(platform, **kwargs)
            except Exception as e:
                print(f"Error running {platform.upper()} agent: {e}")
            
            print(f"\n{platform.upper()} agent session ended.")
    
    def interactive_mode(self) -> Optional[str]:
        """Interactive mode to choose which platform to run."""
        platforms = self.get_available_platforms()
        
        print("Available dating platforms:")
        for i, platform in enumerate(platforms, 1):
            print(f"  {i}. {platform.capitalize()}")
        print(f"  {len(platforms) + 1}. All platforms")
        print(f"  {len(platforms) + 2}. Exit")
        
        while True:
            try:
                choice = int(input(f"\nSelect platform (1-{len(platforms) + 2}): "))
                
                if choice == len(platforms) + 2:  # Exit
                    print("Goodbye!")
                    return None
                elif choice == len(platforms) + 1:  # All platforms
                    return "all"
                elif 1 <= choice <= len(platforms):
                    return platforms[choice - 1]
                else:
                    print(f"Invalid choice. Please enter 1-{len(platforms) + 2}")
                    
            except ValueError:
                print("Please enter a valid number.")
    
    def setup_argparse(self) -> argparse.ArgumentParser:
        """Set up and return the argument parser."""
        parser = argparse.ArgumentParser(
            description="Run dating platform agents with configurable options.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
    wifebot bumble --headless
    wifebot tinder --model gpt-4 --verbose
    wifebot hinge --viewport-width 1920 --viewport-height 1080
    wifebot all --headless --trace-path /tmp/traces
    wifebot --interactive
            """
        )
        
        # Positional argument for platform (optional when --interactive is used)
        choices = self.get_available_platforms() + ['all']
        parser.add_argument(
            'platform',
            nargs='?',
            choices=choices,
            help='Dating platform to run or "all" for all platforms'
        )
        
        # Configuration file
        parser.add_argument(
            '--config',
            type=str,
            help='Path to configuration JSON file (default: config.json)'
        )
        
        # Browser configuration flags
        parser.add_argument(
            '--headless',
            action='store_true',
            help='Run browser in headless mode'
        )
        
        parser.add_argument(
            '--viewport-width',
            type=int,
            help='Browser viewport width'
        )
        
        parser.add_argument(
            '--viewport-height',
            type=int,
            help='Browser viewport height'
        )
        
        parser.add_argument(
            '--min-wait',
            type=float,
            help='Minimum wait time for page loads in seconds'
        )
        
        parser.add_argument(
            '--max-wait',
            type=float,
            help='Maximum wait time for page loads in seconds'
        )
        
        # Profile and trace configuration
        parser.add_argument(
            '--profile-dir',
            type=str,
            help='Custom browser profile directory'
        )
        
        parser.add_argument(
            '--trace-path',
            type=str,
            help='Custom trace path for logging'
        )
        
        # LLM configuration
        parser.add_argument(
            '--model',
            type=str,
            help='LLM model to use'
        )
        
        # Utility flags
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Enter interactive mode to choose platform'
        )
        
        return parser
    
    def extract_platform_config(self, args) -> Dict[str, Any]:
        """Extract platform configuration from parsed arguments.
        
        Only include arguments that were explicitly provided by the user.
        This allows the Platform constructor to properly implement the
        configuration hierarchy (args > config > defaults).
        """
        config = {}
        
        # Add config path if provided
        if hasattr(args, 'config') and args.config:
            config['config_path'] = args.config
        elif self.config_path:
            config['config_path'] = self.config_path
            
        # Only include arguments that were explicitly provided
        if args.headless:
            config['headless'] = True
            
        if args.viewport_width is not None:
            config['viewport_width'] = args.viewport_width
            
        if args.viewport_height is not None:
            config['viewport_height'] = args.viewport_height
            
        if args.min_wait is not None:
            config['min_wait'] = args.min_wait
            
        if args.max_wait is not None:
            config['max_wait'] = args.max_wait
            
        if args.model is not None:
            config['model'] = args.model
            
        if args.verbose:
            config['verbose'] = True
            
        if args.profile_dir:
            config['profile_dir'] = args.profile_dir
            
        if args.trace_path:
            config['trace_path'] = args.trace_path
        
        return config
    
    async def run_from_args(self, args) -> None:
        """Run the appropriate platform(s) based on parsed arguments."""
        config = self.extract_platform_config(args)
        
        try:
            if args.interactive:
                # Interactive mode - ignore platform argument
                selected_platform = self.interactive_mode()
                if selected_platform is None:
                    return
                elif selected_platform == "all":
                    await self.run_all_platforms(**config)
                else:
                    await self.run_single_platform(selected_platform, **config)
            elif args.platform == "all":
                await self.run_all_platforms(**config)
            elif args.platform in self.platforms:
                await self.run_single_platform(args.platform, **config)
            elif args.platform is None:
                # No platform specified and not interactive - show help
                print("Error: You must specify a platform or use --interactive")
                print(f"Available platforms: {', '.join(self.get_available_platforms())}")
                print("Use 'all' to run all platforms or --interactive for interactive mode")
                sys.exit(1)
            else:
                print(f"Error: Unknown platform '{args.platform}'")
                print(f"Available platforms: {', '.join(self.get_available_platforms())}")
                print("Use 'all' to run all platforms or --interactive for interactive mode")
                sys.exit(1)
        except Exception as e:
            print(f"Fatal error: {e}")
            sys.exit(1)
