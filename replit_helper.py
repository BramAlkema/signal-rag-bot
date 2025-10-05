#!/usr/bin/env python3
"""
Replit Helper - Auto-configuration for Replit environment
This module detects Replit and applies optimized settings
"""

import os
import sys


def is_replit():
    """Check if running on Replit"""
    return os.environ.get('REPL_ID') is not None or \
           os.environ.get('REPLIT_DB_URL') is not None


def configure_for_replit():
    """Apply Replit-optimized settings"""
    if not is_replit():
        return False

    print("🔧 Detected Replit environment - applying optimizations...")

    # Memory optimizations
    os.environ.setdefault('CHUNK_SIZE', '800')
    os.environ.setdefault('CHUNK_OVERLAP', '150')
    os.environ.setdefault('SEARCH_K', '2')
    os.environ.setdefault('MAX_TOKENS', '150')

    # Logging optimizations
    os.environ.setdefault('LOG_LEVEL', 'WARNING')

    # Python optimizations
    os.environ.setdefault('PYTHONOPTIMIZE', '1')
    os.environ.setdefault('PYTHONUNBUFFERED', '1')

    # Replit-specific paths
    signal_cli_path = "/home/runner/.local/share/signal-cli-bin/bin"
    current_path = os.environ.get('PATH', '')
    if signal_cli_path not in current_path:
        os.environ['PATH'] = f"{signal_cli_path}:{current_path}"

    print("✅ Replit optimizations applied:")
    print(f"   - CHUNK_SIZE: {os.environ.get('CHUNK_SIZE')}")
    print(f"   - SEARCH_K: {os.environ.get('SEARCH_K')}")
    print(f"   - LOG_LEVEL: {os.environ.get('LOG_LEVEL')}")

    return True


def check_replit_secrets():
    """Verify required secrets are set in Replit"""
    required_secrets = ['OPENAI_API_KEY', 'SIGNAL_PHONE_NUMBER']
    missing = []

    for secret in required_secrets:
        if not os.environ.get(secret):
            missing.append(secret)

    if missing:
        print("\n❌ Missing required secrets!")
        print("   Go to Secrets tab (🔒) and add:")
        for secret in missing:
            print(f"   - {secret}")
        print()
        return False

    print("✅ All required secrets are set")
    return True


def setup_replit_directories():
    """Create necessary directories for Replit"""
    directories = [
        'logs',
        'index',
        '/home/runner/.local/share/signal-cli'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    print("✅ Directories created")


def get_replit_url():
    """Get the public URL for this Replit"""
    repl_slug = os.environ.get('REPL_SLUG')
    repl_owner = os.environ.get('REPL_OWNER')

    if repl_slug and repl_owner:
        return f"https://{repl_slug}.{repl_owner}.repl.co"
    return None


def display_replit_info():
    """Display Replit-specific information"""
    if not is_replit():
        return

    print("\n" + "="*50)
    print("  Signal RAG Bot on Replit")
    print("="*50)

    url = get_replit_url()
    if url:
        print(f"URL: {url}")

    print(f"Repl ID: {os.environ.get('REPL_ID', 'Unknown')}")
    print(f"Storage: {os.environ.get('REPL_HOME', '/home/runner')}")

    # Check if Always-On is enabled
    is_always_on = os.environ.get('REPLIT_CLUSTER') == 'prod'
    print(f"Always-On: {'✅ Enabled' if is_always_on else '❌ Disabled (will sleep when inactive)'}")

    print("="*50 + "\n")


def main():
    """Run Replit helper checks"""
    if not is_replit():
        print("ℹ️  Not running on Replit")
        return

    display_replit_info()
    configure_for_replit()
    setup_replit_directories()

    if not check_replit_secrets():
        sys.exit(1)

    print("\n✅ Replit environment ready!")
    print("\nNext steps:")
    print("1. Link Signal: signal-cli link -n 'RAG-Bot'")
    print("2. Build index: python custom_rag.py build")
    print("3. Run bot: python signal_bot_rag.py")
    print()


if __name__ == '__main__':
    main()
