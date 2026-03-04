"""
Configuration System for Enterprise Agentic Platform.
Supports YAML config files with CLI argument overrides.
"""

import os
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class BrandingConfig(BaseModel):
    """Branding configuration for the platform."""
    company_name: str = "Agent Platform"
    project_name: str = "Enterprise Agentic Platform"
    tagline: str = "Powered by Google ADK"

    # Color Palette (Marine Blue / Ultramar Blue defaults)
    primary_color: str = "#0066B3"  # Marine Blue
    primary_dark: str = "#004C85"
    primary_light: str = "#0080D4"
    secondary_color: str = "#1E3A8A"  # Ultramar Blue
    secondary_dark: str = "#152a66"
    secondary_light: str = "#2563EB"
    accent_color: str = "#0EA5E9"  # Sky Blue
    background_color: str = "#F0F7FF"
    text_primary: str = "#1E3A5F"
    text_secondary: str = "#475569"

    # Mascot
    mascot_name: str = "Marina"
    mascot_path: str = "/mascot"
    mascot_idle: str = "mascot-idle.svg"
    mascot_thinking: str = "mascot-thinking.svg"
    mascot_error: str = "mascot-error.svg"


class SkillsConfig(BaseModel):
    """Skills configuration."""
    skills_dir: str = ".skills"
    auto_reload: bool = True
    reload_interval: int = 30  # seconds


class ModelConfig(BaseModel):
    """Model configuration."""
    provider: str = "google"
    model_name: str = "gemini-2.5-flash"
    api_key_env: str = "GOOGLE_API_KEY"
    temperature: float = 0.7
    max_tokens: int = 2048


class WorkflowConfig(BaseModel):
    """Workflow configuration."""
    name: str
    description: str
    tools: List[str] = Field(default_factory=list)
    system_prompt: str = ""


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])


class AppConfig(BaseModel):
    """Main application configuration."""
    branding: BrandingConfig = Field(default_factory=BrandingConfig)
    skills: SkillsConfig = Field(default_factory=SkillsConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    workflows: Dict[str, WorkflowConfig] = Field(default_factory=dict)
    server: ServerConfig = Field(default_factory=ServerConfig)


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    path = Path(config_path)

    if not path.exists():
        print(f"Warning: Config file {config_path} not found. Using defaults.")
        return {}

    with open(path, 'r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML config: {e}")
            return {}


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two configuration dictionaries."""
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def parse_cli_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Enterprise Agentic Platform - AI Agent System with Google ADK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m backend.main --config config.yaml
  python -m backend.main --company-name "MyCompany" --primary-color "#FF5500"
  python -m backend.main --config config.yaml --port 3000 --debug
        """
    )

    # Config file
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config.yaml",
        help="Path to YAML configuration file (default: config.yaml)"
    )

    # Branding overrides
    branding_group = parser.add_argument_group("Branding Options")
    branding_group.add_argument(
        "--company-name",
        type=str,
        help="Company/project name"
    )
    branding_group.add_argument(
        "--project-name",
        type=str,
        help="Project display name"
    )
    branding_group.add_argument(
        "--primary-color",
        type=str,
        help="Primary brand color (hex)"
    )
    branding_group.add_argument(
        "--secondary-color",
        type=str,
        help="Secondary brand color (hex)"
    )
    branding_group.add_argument(
        "--mascot-name",
        type=str,
        help="Mascot character name"
    )
    branding_group.add_argument(
        "--mascot-path",
        type=str,
        help="Path to mascot assets directory"
    )

    # Skills configuration
    skills_group = parser.add_argument_group("Skills Options")
    skills_group.add_argument(
        "--skills-dir",
        type=str,
        help="Directory containing skill markdown files (default: .skills)"
    )
    skills_group.add_argument(
        "--no-auto-reload",
        action="store_true",
        help="Disable automatic skill reloading"
    )

    # Model configuration
    model_group = parser.add_argument_group("Model Options")
    model_group.add_argument(
        "--model",
        type=str,
        help="Model name (e.g., gemini-2.0-flash)"
    )
    model_group.add_argument(
        "--api-key",
        type=str,
        help="API key (or set GOOGLE_API_KEY env var)"
    )
    model_group.add_argument(
        "--temperature",
        type=float,
        help="Model temperature (0.0-1.0)"
    )

    # Server configuration
    server_group = parser.add_argument_group("Server Options")
    server_group.add_argument(
        "--host",
        type=str,
        help="Server host (default: 0.0.0.0)"
    )
    server_group.add_argument(
        "--port",
        type=int,
        help="Server port (default: 8000)"
    )
    server_group.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    return parser.parse_args()


def create_config_from_args(args: argparse.Namespace) -> AppConfig:
    """Create configuration from CLI arguments and config file."""
    # Load YAML config
    yaml_config = load_yaml_config(args.config)

    # Build override config from CLI args
    cli_overrides = {}

    # Branding overrides
    if args.company_name:
        cli_overrides.setdefault("branding", {})["company_name"] = args.company_name
    if args.project_name:
        cli_overrides.setdefault("branding", {})["project_name"] = args.project_name
    if args.primary_color:
        cli_overrides.setdefault("branding", {})["primary_color"] = args.primary_color
    if args.secondary_color:
        cli_overrides.setdefault("branding", {})["secondary_color"] = args.secondary_color
    if args.mascot_name:
        cli_overrides.setdefault("branding", {})["mascot_name"] = args.mascot_name
    if args.mascot_path:
        cli_overrides.setdefault("branding", {})["mascot_path"] = args.mascot_path

    # Skills overrides
    if args.skills_dir:
        cli_overrides.setdefault("skills", {})["skills_dir"] = args.skills_dir
    if args.no_auto_reload:
        cli_overrides.setdefault("skills", {})["auto_reload"] = False

    # Model overrides
    if args.model:
        cli_overrides.setdefault("model", {})["model_name"] = args.model
    if args.api_key:
        cli_overrides.setdefault("model", {})["api_key"] = args.api_key
    if args.temperature is not None:
        cli_overrides.setdefault("model", {})["temperature"] = args.temperature

    # Server overrides
    if args.host:
        cli_overrides.setdefault("server", {})["host"] = args.host
    if args.port:
        cli_overrides.setdefault("server", {})["port"] = args.port
    if args.debug:
        cli_overrides.setdefault("server", {})["debug"] = True

    # Merge configs: defaults -> YAML -> CLI overrides
    final_config = merge_configs(yaml_config, cli_overrides)

    return AppConfig(**final_config)


def get_default_config() -> AppConfig:
    """Get default configuration."""
    return AppConfig(
        branding=BrandingConfig(),
        skills=SkillsConfig(),
        model=ModelConfig(),
        workflows={
            "data_analysis": WorkflowConfig(
                name="Data Analysis",
                description="Analyze data, generate insights, create charts",
                tools=["data_query", "chart_generator", "report_builder"]
            ),
            "code_gen": WorkflowConfig(
                name="Code Generation",
                description="Write, review, and debug code",
                tools=["code_writer", "code_reviewer", "bug_detector"]
            ),
            "research": WorkflowConfig(
                name="Research",
                description="Search and summarize information",
                tools=["web_search", "content_summarizer", "citation_generator"]
            ),
            "general_chat": WorkflowConfig(
                name="General Chat",
                description="General conversation and assistance",
                tools=[]
            )
        },
        server=ServerConfig()
    )


def generate_sample_config(output_path: str = "config.yaml") -> None:
    """Generate a sample configuration file."""
    config = get_default_config()

    yaml_content = f"""# Enterprise Agentic Platform Configuration
# Generated sample configuration

# Branding Configuration
branding:
  company_name: "{config.branding.company_name}"
  project_name: "{config.branding.project_name}"
  tagline: "{config.branding.tagline}"

  # Color Palette (Marine Blue / Ultramar Blue)
  primary_color: "{config.branding.primary_color}"
  primary_dark: "{config.branding.primary_dark}"
  primary_light: "{config.branding.primary_light}"
  secondary_color: "{config.branding.secondary_color}"
  secondary_dark: "{config.branding.secondary_dark}"
  secondary_light: "{config.branding.secondary_light}"
  accent_color: "{config.branding.accent_color}"
  background_color: "{config.branding.background_color}"
  text_primary: "{config.branding.text_primary}"
  text_secondary: "{config.branding.text_secondary}"

  # Mascot Configuration
  mascot_name: "{config.branding.mascot_name}"
  mascot_path: "{config.branding.mascot_path}"
  mascot_idle: "{config.branding.mascot_idle}"
  mascot_thinking: "{config.branding.mascot_thinking}"
  mascot_error: "{config.branding.mascot_error}"

# Skills Configuration
skills:
  skills_dir: "{config.skills.skills_dir}"
  auto_reload: {config.skills.auto_reload}
  reload_interval: {config.skills.reload_interval}

# Model Configuration
model:
  provider: "{config.model.provider}"
  model_name: "{config.model.model_name}"
  api_key_env: "{config.model.api_key_env}"
  temperature: {config.model.temperature}
  max_tokens: {config.model.max_tokens}

# Workflows Configuration
workflows:
  data_analysis:
    name: "Data Analysis"
    description: "Analyze data, generate insights, create charts"
    tools:
      - data_query
      - chart_generator
      - report_builder
  code_gen:
    name: "Code Generation"
    description: "Write, review, and debug code"
    tools:
      - code_writer
      - code_reviewer
      - bug_detector
  research:
    name: "Research"
    description: "Search and summarize information"
    tools:
      - web_search
      - content_summarizer
      - citation_generator
  general_chat:
    name: "General Chat"
    description: "General conversation and assistance"
    tools: []

# Server Configuration
server:
  host: "{config.server.host}"
  port: {config.server.port}
  debug: {config.server.debug}
  cors_origins:
    - "*"
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    print(f"Sample configuration written to {output_path}")


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = get_default_config()
    return _config


def set_config(config: AppConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def init_config(args: argparse.Namespace = None) -> AppConfig:
    """Initialize configuration from args or create default."""
    global _config
    if args:
        _config = create_config_from_args(args)
    else:
        _config = get_default_config()
    return _config
