from typing import cast

import httpx


class HttpSmsResponseMapper:
    def get_provider_message_id(self, response: httpx.Response) -> str | None:
        if not response.content:
            return None

        raw_data: object = response.json()
        if not isinstance(raw_data, dict):
            return None

        data = cast(dict[str, object], raw_data)
        raw_message_id = data.get("message_id")
        return raw_message_id if isinstance(raw_message_id, str) else None
