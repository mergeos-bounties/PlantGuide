"""Optional FastAPI surface (bounty).

Run with::

    pip install -e ".[api]"
    uvicorn plantguide.api.app:app --reload
"""

from plantguide.api.app import app

__all__ = ["app"]