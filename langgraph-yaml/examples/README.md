# Sellora deterministic workflow example

From the `langgraph-yaml` directory:

```bash
uv run --extra dev python examples/sellora_mock.py
```

This example loads `sellora_workflow.yaml`, injects an in-memory catalog, and invokes a real LangGraph graph. The finite sequence `sku-1`, `sku-1`, `sku-2` yields cart quantities 2 and 1, then mock checkout, review, payment, and tracking. The printed trace makes the execution inspectable.

This is **one synthetic invocation**, not an interactive multi-message conversation. Payment and tracking do not contact external services. Unknown SKUs raise an explicit error. An empty selection proceeds to mock checkout with an empty cart for demonstration purposes, not as a production policy.

The graph uses `recursion_limit=50`. This is sufficient for the documented sequence, not an unlimited-loop guarantee. Longer selection sequences require an appropriately higher limit.
