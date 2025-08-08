"""
Base Platform class and shared constants for dating platform agents.
"""

from abc import ABC, abstractmethod
from dotenv import load_dotenv
from browser_use import Agent, BrowserSession, BrowserProfile
from browser_use.llm import ChatOpenAI
from .config_loader import (
    load_config, get_default_config_value,
    get_profile_dir, get_trace_path, render_prompt_template
)


class Platform(ABC):
    """Base class for all dating platforms."""
    
    def __init__(self, config_path=None, **kwargs):
        """Initialize platform with configurable options.
        
        Configuration priority (highest to lowest):
        1. Explicit keyword arguments passed to this method
        2. Values from config file
        3. Constructor default values
        
        Args:
            config_path (str, optional): Path to configuration JSON file
            **kwargs: Configuration options that can include:
                - headless (bool): Run browser in headless mode (default: False)
                - viewport_width (int): Browser viewport width (default: 1280)
                - viewport_height (int): Browser viewport height (default: 1100)
                - min_wait (float): Minimum wait time for page loads (default: 1)
                - max_wait (float): Maximum wait time for page loads (default: 10)
                - model (str): LLM model to use (default: 'gpt-4o-mini')
                - verbose (bool): Enable verbose logging (default: False)
                - profile_dir (str, optional): Custom profile directory path
                - trace_path (str, optional): Custom trace path
        """
        load_dotenv()
        
        # Load configuration from file (if it exists)
        try:
            self.config = load_config(config_path)
        except FileNotFoundError:
            self.config = {}
        
        # Load and render base task template with configuration
        self.base_task = render_prompt_template('base_task.tpl', self.config)
        
        # Constructor defaults
        defaults = {
            'headless': False,
            'viewport_width': 1280, 
            'viewport_height': 1100,
            'min_wait': 1,
            'max_wait': 10,
            'model': 'gpt-4o-mini',
            'verbose': False
        }
        
        # Apply configuration hierarchy: kwargs > config file > constructor defaults
        self.headless = self._resolve_config_value('headless', kwargs, 'browser.headless', defaults['headless'])
        self.viewport_width = self._resolve_config_value('viewport_width', kwargs, 'browser.viewport.width', defaults['viewport_width'])
        self.viewport_height = self._resolve_config_value('viewport_height', kwargs, 'browser.viewport.height', defaults['viewport_height'])
        self.min_wait = self._resolve_config_value('min_wait', kwargs, 'browser.minimum_wait_page_load_time', defaults['min_wait'])
        self.max_wait = self._resolve_config_value('max_wait', kwargs, 'browser.maximum_wait_page_load_time', defaults['max_wait'])
        self.model = self._resolve_config_value('model', kwargs, 'llm.model', defaults['model'])
        self.verbose = self._resolve_config_value('verbose', kwargs, 'verbose', defaults['verbose'])
        
        self._custom_profile_dir = kwargs.get('profile_dir')
        self._custom_trace_path = kwargs.get('trace_path')
    
    def _resolve_config_value(self, param_name: str, kwargs: dict, config_key: str, default_value):
        """Resolve configuration value using hierarchy: kwargs > config file > constructor defaults.
        
        Args:
            param_name: Parameter name to look up
            kwargs: Keyword arguments dictionary
            config_key: Dot-separated key to look up in config file
            default_value: Constructor default value if not found elsewhere
            
        Returns:
            Final resolved value following priority hierarchy
        """
        # 1. Explicit kwarg provided - highest priority
        if param_name in kwargs:
            return kwargs[param_name]
        
        # 2. Check config file - medium priority
        config_value = get_default_config_value(self.config, config_key)
        if config_value is not None:
            return config_value
        
        # 3. Fall back to constructor default - lowest priority
        return default_value
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Platform name (e.g., 'tinder', 'bumble')"""
        pass
    
    @property
    @abstractmethod
    def url(self) -> str:
        """Platform URL to navigate to"""
        pass
    
    @property
    @abstractmethod
    def platform_instructions(self) -> str:
        """Platform-specific instructions"""
        pass
    
    @property
    def profile_dir(self) -> str:
        """Browser profile directory for this platform"""
        return get_profile_dir(self.config, self.name, self._custom_profile_dir)
    
    @property
    def trace_path(self) -> str:
        """Trace path for this platform"""
        return get_trace_path(self.config, self.name, self._custom_trace_path)
    
    @property
    def browser_config(self) -> dict:
        """Dynamic browser configuration based on constructor parameters and config file"""
        return {
            'headless': self.headless,
            'minimum_wait_page_load_time': self.min_wait,
            'maximum_wait_page_load_time': self.max_wait,
            'viewport': {'width': self.viewport_width, 'height': self.viewport_height},
        }
    
    @property
    def llm_config(self) -> dict:
        """Dynamic LLM configuration based on constructor parameters and config file"""
        return {'model': self.model}
    
    @property
    def task(self) -> str:
        """Complete task string with base task + platform-specific instructions"""
        return self.base_task + "\n\n" + self.platform_instructions
    
    async def run(self):
        """Run the dating agent for this platform."""
        if self.verbose:
            print(f"Configuration: {self.browser_config}")
            print(f"LLM: {self.llm_config}")
            print(f"Profile dir: {self.profile_dir}")
            print(f"Trace path: {self.trace_path}")
            
        # Initialize the BrowserSession with dynamic configuration
        browser_session = BrowserSession(
            browser_profile=BrowserProfile(
                **self.browser_config,
                user_data_dir=self.profile_dir,
                trace_path=self.trace_path,
            )
        )

        # Start the browser session
        await browser_session.start()

        try:
            # Navigate to the platform
            await browser_session.navigate(self.url)

            # Initialize and run the Agent with dynamic configuration
            agent = Agent(
                task=self.task,
                llm=ChatOpenAI(**self.llm_config),
                browser_session=browser_session,
                available_file_paths=[self.trace_path],
                file_system_path=self.trace_path,
                save_conversation_path=f"{self.trace_path}/conversation.json",
            )
            await agent.run()
        
        finally:
            # Always close the browser session
            await browser_session.stop()
