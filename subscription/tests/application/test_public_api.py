import subscription.application as application


def test_application_package_exports_stage_five_api() -> None:
    assert "CreatePlanService" in application.__all__
    assert "CreateSubscriptionService" in application.__all__
    assert "ResolveEntitlementsService" in application.__all__
    assert "RecordUsageService" in application.__all__
    assert "EvaluateTrialService" in application.__all__
