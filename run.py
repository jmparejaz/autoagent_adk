#!/usr/bin/env python3
"""
CLI Entry Point for Enterprise Agentic Platform.

This script provides a command-line interface to start the platform
with customizable branding, skills directory, and server settings.

Usage:
    python run.py --config config.yaml
    python run.py --company-name "MyCompany" --primary-color "#FF5500"
    python run.py --skills-dir ./my_skills --port 3000
    python run.py --help
"""

import sys
import os
import argparse
import uvicorn

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Enterprise Agentic Platform - AI Agent System with Google ADK",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Config file
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config.yaml",
        help="Path to YAML configuration file (default: config.yaml)"
    )

    # Branding overrides
    parser.add_argument("--company-name", type=str, help="Company/project name")
    parser.add_argument("--project-name", type=str, help="Project display name")
    parser.add_argument("--primary-color", type=str, help="Primary brand color (hex)")
    parser.add_argument("--secondary-color", type=str, help="Secondary brand color (hex)")
    parser.add_argument("--accent-color", type=str, help="Accent color (hex)")
    parser.add_argument("--mascot-name", type=str, help="Mascot character name")

    # Skills configuration
    parser.add_argument("--skills-dir", type=str, default=".skills", help="Skills directory")

    # Server configuration
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    args = parse_args()

    # Print startup banner
    print("\n" + "="*60)
    print("  Enterprise Agentic Platform")
    print("  Powered by Google ADK")
    print("="*60 + "\n")

    # Print configuration
    print(f"Skills Directory: {args.skills_dir}")
    print(f"Server: http://{args.host}:{args.port}")
    print(f"Debug Mode: {args.debug}")
    print("")

    # Check for API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Warning: GOOGLE_API_KEY environment variable not set.")
        print("Set it with: export GOOGLE_API_KEY='your-api-key'")
        print("")

    # Start the server
    print("Starting server...")
    print("")

    uvicorn.run(
        "backend.main:app",
        host=args.host,
        port=args.port,
        reload=args.debug
    )


if __name__ == "__main__":
    main()
