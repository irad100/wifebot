"""
Configuration and prompt loading utilities for wifebot.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Template, Environment, FileSystemLoader


def get_project_root() -> Path:
    """Get the project root directory."""
    # This file is in wifebot/, so go up one level to get project root
    return Path(__file__).parent.parent


def get_xdg_config_home() -> Path:
    """Get XDG_CONFIG_HOME directory, defaulting to ~/.config if not set."""
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_config_home:
        return Path(xdg_config_home)
    else:
        return Path.home() / '.config'


def get_default_config_path() -> Path:
    """Get the default configuration file path following XDG specification."""
    return get_xdg_config_home() / 'wifebot' / 'config.json'


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Optional path to config file. If None, uses XDG_CONFIG_HOME/wifebot/config.json
        
    Returns:
        Dictionary containing configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    if config_path is None:
        config_path = get_default_config_path()
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config


def load_prompt(prompt_name: str, prompts_dir: Optional[str] = None) -> str:
    """
    Load a prompt from a text file.
    
    Args:
        prompt_name: Name of the prompt file (without .txt extension)
        prompts_dir: Optional directory containing prompts. If None, uses project_root/prompts/
        
    Returns:
        String content of the prompt file
        
    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    if prompts_dir is None:
        prompts_dir = get_project_root() / 'prompts'
    else:
        prompts_dir = Path(prompts_dir)
    
    prompt_file = prompts_dir / f"{prompt_name}.txt"
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    return content


def load_template(template_name: str, prompts_dir: Optional[str] = None) -> str:
    """
    Load a template file for rendering.
    
    Args:
        template_name: Name of the template file (e.g., 'base_task.jinja')
        prompts_dir: Optional directory containing templates. If None, uses project_root/prompts/
        
    Returns:
        String content of the template file
        
    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    if prompts_dir is None:
        prompts_dir = get_project_root() / 'prompts'
    else:
        prompts_dir = Path(prompts_dir)
    
    template_file = prompts_dir / template_name
    
    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")
    
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    return content


def render_prompt_template(template_name: str, config: Dict[str, Any], prompts_dir: Optional[str] = None) -> str:
    """
    Load and render a prompt template with configuration values.
    
    Args:
        template_name: Name of the template file (e.g., 'base_task.jinja')
        config: Configuration dictionary to use for template variables
        prompts_dir: Optional directory containing templates. If None, uses project_root/prompts/
        
    Returns:
        Rendered prompt string
        
    Raises:
        FileNotFoundError: If template file doesn't exist
        jinja2.TemplateError: If template rendering fails
    """
    if prompts_dir is None:
        prompts_dir = get_project_root() / 'prompts'
    else:
        prompts_dir = Path(prompts_dir)
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(prompts_dir))
    
    # Load and render the template
    template = env.get_template(template_name)
    rendered = template.render(config)
    
    return rendered.strip()


def render_prompt_string(template_string: str, config: Dict[str, Any]) -> str:
    """
    Render a prompt template string with configuration values.
    
    Args:
        template_string: Template string to render
        config: Configuration dictionary to use for template variables
        
    Returns:
        Rendered prompt string
        
    Raises:
        jinja2.TemplateError: If template rendering fails
    """
    template = Template(template_string)
    rendered = template.render(config)
    
    return rendered.strip()


def get_default_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a configuration value using dot notation path.
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated path to the configuration key (e.g., 'browser.headless')
        default: Default value to return if key is not found
        
    Returns:
        Configuration value or default
    """
    keys = key_path.split('.')
    value = config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def expand_path_template(template: str, **kwargs) -> str:
    """
    Expand a path template with provided kwargs.
    
    Args:
        template: Path template with {placeholder} format
        **kwargs: Values to substitute in the template
        
    Returns:
        Expanded path string
    """
    return template.format(**kwargs)


def get_profile_dir(config: Dict[str, Any], platform: str, custom_dir: Optional[str] = None) -> str:
    """
    Get the profile directory for a platform.
    
    Args:
        config: Configuration dictionary
        platform: Platform name
        custom_dir: Custom directory override
        
    Returns:
        Profile directory path
    """
    if custom_dir:
        return custom_dir
    
    template = get_default_config_value(
        config, 
        'paths.profile_dir_template', 
        '~/.config/browseruse/profiles/{platform}'
    )
    
    return expand_path_template(template, platform=platform)


def get_trace_path(config: Dict[str, Any], platform: str, custom_path: Optional[str] = None) -> str:
    """
    Get the trace path for a platform.
    
    Args:
        config: Configuration dictionary
        platform: Platform name
        custom_path: Custom path override
        
    Returns:
        Trace path
    """
    if custom_path:
        return custom_path
    
    template = get_default_config_value(
        config, 
        'paths.trace_path_template', 
        '/tmp/wifebot/{platform}'
    )
    
    return expand_path_template(template, platform=platform)
