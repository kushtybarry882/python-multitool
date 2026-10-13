from .console import ConsoleUI, Colors
from .putty import PuttyUI

try:
    from rich.console import Console
    _HAS_RICH = True
except Exception:
    _HAS_RICH = False

def get_ui():
    """Return the PuTTY-style UI as default, or ConsoleUI if PuTTY is unavailable."""
    try:
        ui = PuttyUI()
        return ui
    except Exception:
        if _HAS_RICH:
            try:
                return ConsoleUI()
            except Exception:
                return None
        return None

__all__ = ["ConsoleUI", "PuttyUI", "Colors", "get_ui"]
