import importlib.util
import re

import pytest

if importlib.util.find_spec('jwt') is None:
    pytest.skip('PyJWT is not installed in this environment.', allow_module_level=True)

from app.main import build_origin_regex


def test_cloudflare_pages_origin_regex_allows_preview_subdomains():
    pattern = build_origin_regex('https://keepiq31.pages.dev')

    assert pattern is not None
    assert re.fullmatch(pattern, 'https://keepiq31.pages.dev')
    assert re.fullmatch(pattern, 'https://44231e74.keepiq31.pages.dev')
    assert not re.fullmatch(pattern, 'https://keepiq31.pages.dev.evil.com')
    assert not re.fullmatch(pattern, 'https://evil.pages.dev')


def test_non_pages_domain_does_not_enable_regex():
    assert build_origin_regex('https://keepiq.example.com') is None
