import dateparser
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def normalize_date(date_str: str) -> str:
    """
    Rule 6: No 'smart' guessing. Converts '20th Dec', 'next Friday', 
    or '20/12' into a clean ISO YYYY-MM-DD.
    """
    if not date_str or date_str.lower() in ["/skip", "none", "no"]:
        return "No deadline"

    # Rule 13: 2025 Standard - Timezone aware parsing
    settings = {
        'RELATIVE_BASE': datetime.now(timezone.utc),
        'PREFER_DATES_FROM': 'future',
        'RETURN_AS_TIMEZONE_AWARE': True
    }
    
    parsed = dateparser.parse(date_str, settings=settings)
    
    if parsed:
        # Rule 1: Ensuring a predictable format for storage
        return parsed.date().isoformat()
    
    return "No deadline"
