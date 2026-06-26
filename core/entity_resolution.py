def normalize_company(name: str) -> str:
    """
    Canonical company normalization.
    More sophisticated logic will be added later.
    """

    if not name:
        return ""

    return " ".join(name.strip().split())
