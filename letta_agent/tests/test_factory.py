from letta_agent import LettaAgentService, LettaAgentServiceFactory


def test_factory_builds_public_service() -> None:
    service = LettaAgentServiceFactory().build(
        api_key="test-key",
        base_url=None,
    )

    assert isinstance(service, LettaAgentService)
