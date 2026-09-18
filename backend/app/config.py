"""Runtime configuration read from environment variables."""

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
]


def cors_origins(raw: str | None) -> list[str]:
    """Return local development origins plus explicit comma-separated extras.

    Wildcards and non-HTTP origins are ignored so a misconfigured value can
    never open the API to every site.
    """
    origins = list(DEFAULT_CORS_ORIGINS)
    for item in (raw or "").split(","):
        origin = item.strip().rstrip("/")
        if origin.startswith(("http://", "https://")) and "*" not in origin and origin not in origins:
            origins.append(origin)
    return origins
