import os

environment = os.getenv("DJANGO_ENV", "local").lower()

if environment == "production":
    from .production import *  # noqa: F403
else:
    from .local import *  # noqa: F403