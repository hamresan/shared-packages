import pytest

from instagram_auth.infrastructure.security import SecretsStateGenerator


def test_state_generator_returns_distinct_url_safe_values() -> None:
    generator = SecretsStateGenerator()

    first = generator.generate()
    second = generator.generate()

    assert first != second
    assert len(first) >= 43
    assert all(character.isalnum() or character in "-_" for character in first)


def test_state_generator_rejects_insufficient_entropy() -> None:
    with pytest.raises(ValueError, match="at least 32 bytes"):
        SecretsStateGenerator(entropy_bytes=16)
