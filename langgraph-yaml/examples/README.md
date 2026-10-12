# Sellora deterministic example

The YAML topology in `sellora_workflow.yaml` describes a bounded, synthetic product-selection loop followed by checkout, review, mock payment, and tracking. The planned Python example will inject handlers and execute the graph using LangGraph. No real payment or external store is involved.
