"""PlantGuide FastAPI REST API.

Start the server::

    uvicorn plantguide.api.routes:app --reload --host 127.0.0.1 --port 8000

Or via::

    pip install plantguide[api]
    plantguide serve
"""

from plantguide.api.routes import app  # noqa: F401
