"""
Simple script to run ensure_ranks.

Usage:
    python -m script.ensure_ranks
    python -m script.ensure_ranks --force
"""
import sys
from utils.ranking import ensure_ranks

if __name__ == '__main__':
    force = '--force' in sys.argv
    ensure_ranks(force=force)
