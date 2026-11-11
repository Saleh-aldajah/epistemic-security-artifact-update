#!/usr/bin/env python3
"""Print an offline test token; used only with the bundled offline JWKS fixture."""
from tests.offline_fixtures import make_token

if __name__ == "__main__":
    print(make_token())
