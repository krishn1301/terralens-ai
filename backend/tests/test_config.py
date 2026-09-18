from app.config import DEFAULT_CORS_ORIGINS, cors_origins


def test_cors_defaults_to_local_development_origins():
    assert cors_origins(None) == DEFAULT_CORS_ORIGINS
    assert "http://localhost:5173" in DEFAULT_CORS_ORIGINS


def test_cors_adds_configured_origins_without_duplicates_or_trailing_slashes():
    origins = cors_origins(" https://example.github.io/ ,http://localhost:5173,, https://demo.example.org")
    assert origins[: len(DEFAULT_CORS_ORIGINS)] == DEFAULT_CORS_ORIGINS
    assert origins.count("http://localhost:5173") == 1
    assert "https://example.github.io" in origins
    assert "https://demo.example.org" in origins


def test_cors_ignores_wildcard_and_non_http_origins():
    origins = cors_origins("*, null, ftp://files.example.org, https://ok.example.org")
    assert "*" not in origins
    assert "null" not in origins
    assert "ftp://files.example.org" not in origins
    assert "https://ok.example.org" in origins
