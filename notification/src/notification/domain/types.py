type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]


def empty_json_object() -> dict[str, JsonValue]:
    return {}
