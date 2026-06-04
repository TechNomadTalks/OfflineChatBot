"""
Autonomous code analysis and suggestion system.
Runs only when explicitly triggered with strict instructions.
"""

import os
import ast
import re
from .config import config


class AutonomousAgent:
    """Performs autonomous code analysis and suggestions."""
    
    def __init__(self):
        self.allowed_actions = ['analyze', 'suggest', 'review', 'check']
        self.name = "Jarvis"
    
    def execute(self, command: str) -> str:
        """Execute autonomous command."""
        if not command or command.lower() not in self.allowed_actions:
            return f"[ERROR] Unknown autonomous command. Allowed: {', '.join(self.allowed_actions)}"
        
        return getattr(self, f"_do_{command.lower()}")()
    
    def _do_analyze(self) -> str:
        """Analyze the codebase for issues."""
        issues = []
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        py_files = []
        
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in ['tests', '__pycache__', 'venv', '.git']]
            for f in files:
                if f.endswith('.py'):
                    py_files.append(os.path.join(root, f))
        
        for filepath in py_files[:20]:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'TODO' in content or 'FIXME' in content:
                    issues.append(f"{os.path.relpath(filepath, base_dir)}: Has TODO/FIXME")
                
                if 'import *' in content:
                    issues.append(f"{os.path.relpath(filepath, base_dir)}: Wildcard import")
                    
            except Exception:
                pass
        
        if issues:
            return f"[ANALYSIS] Complete:\n" + "\n".join(issues[:10])
        return "[OK] No obvious issues found in recent files."
    
    def _do_suggest(self) -> str:
        """Provide suggestions for improvement."""
        suggestions = []
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        suggestions.append("[SUGGESTIONS]")
        suggestions.append("  - Review config.ini for actual API keys before deployment")
        suggestions.append("  - Consider adding rate limiting for API calls")
        suggestions.append("  - Memory system uses JSON - consider migration to SQLite for concurrency")
        suggestions.append("  - Add unit tests for tts.py module")
        
        return "\n".join(suggestions)
    
    def _do_review(self) -> str:
        """Review code quality."""
        return self._do_analyze()
    
    def _do_check(self) -> str:
        """Check system status."""
        checks = []
        
        zai_key = config.get_zai_api_key()
        if zai_key:
            checks.append("[OK] Z.AI API key configured")
        else:
            checks.append("[MISSING] Z.AI API key")
        
        elevenlabs_key = config.get_elevenlabs_api_key()
        if elevenlabs_key:
            checks.append("[OK] ElevenLabs API key configured")
        else:
            checks.append("[MISSING] ElevenLabs API key (using pyttsx3 fallback)")
        
        tts_provider = config.get_tts_provider()
        checks.append(f"[INFO] TTS provider: {tts_provider}")
        
        memory_enabled = config.is_memory_enabled()
        checks.append(f"[INFO] Memory: {'enabled' if memory_enabled else 'disabled'}")
        
        return "\n".join(checks)


autonomous_agent = AutonomousAgent()


def run_autonomous(command: str) -> str:
    """Run autonomous task with explicit command."""
    return autonomous_agent.execute(command)