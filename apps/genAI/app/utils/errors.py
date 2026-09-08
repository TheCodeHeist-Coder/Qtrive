from fastapi import HTTPException


def provider_http_error(exc: Exception) -> HTTPException:
    """Translate an LLM provider failure into a useful HTTP error.

    Provider SDKs raise their own exception types, so match on the class
    name and status code rather than importing every SDK here.
    """

    name = type(exc).__name__
    status = getattr(exc, "status_code", None)

    message = str(exc).lower()

    # Google's SDK does not use the standard AuthenticationError class,
    # so fall back to matching the message for key problems.
    looks_like_bad_key = any(
        hint in message
        for hint in ("api key", "api_key", "unauthenticated", "credential")
    )

    if name == "AuthenticationError" or status == 401 or looks_like_bad_key:
        return HTTPException(
            status_code=502,
            detail="The AI provider rejected the API key. Check the keys in "
                   "apps/genAI/.env are valid and not expired.",
        )

    if name == "PermissionDeniedError" or status == 403:
        return HTTPException(
            status_code=502,
            detail="The AI provider denied access to this model. Check your "
                   "account has access to the configured model.",
        )

    if name == "RateLimitError" or status == 429:
        return HTTPException(
            status_code=429,
            detail="The AI provider rate limit was hit. Wait a moment and "
                   "try again, or request fewer questions.",
        )

    if name in ("APIConnectionError", "APITimeoutError"):
        return HTTPException(
            status_code=504,
            detail="Could not reach the AI provider. Check the service's "
                   "network connection.",
        )

    return HTTPException(
        status_code=502,
        detail=f"The AI provider failed: {name}",
    )
