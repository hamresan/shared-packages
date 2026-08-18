from decimal import Decimal

from store.domain import StoreAddress


class StoreAddressPersistenceMapper:
    def to_record(self, address: StoreAddress | None) -> dict[str, object] | None:
        if address is None:
            return None
        return {
            "state_or_province": address.state_or_province,
            "city": address.city,
            "area": address.area,
            "street": address.street,
            "building": address.building,
            "postal_code": address.postal_code,
            "additional_details": address.additional_details,
            "latitude": str(address.latitude) if address.latitude is not None else None,
            "longitude": str(address.longitude) if address.longitude is not None else None,
        }

    def to_domain(self, record: dict[str, object] | None) -> StoreAddress | None:
        if record is None:
            return None
        state_or_province = record.get("state_or_province")
        city = record.get("city")
        area = record.get("area")
        street = record.get("street")
        building = record.get("building")
        postal_code = record.get("postal_code")
        additional_details = record.get("additional_details")
        latitude = record.get("latitude")
        longitude = record.get("longitude")
        return StoreAddress(
            state_or_province=state_or_province if isinstance(state_or_province, str) else None,
            city=city if isinstance(city, str) else None,
            area=area if isinstance(area, str) else None,
            street=street if isinstance(street, str) else None,
            building=building if isinstance(building, str) else None,
            postal_code=postal_code if isinstance(postal_code, str) else None,
            additional_details=(
                additional_details if isinstance(additional_details, str) else None
            ),
            latitude=Decimal(str(latitude)) if latitude is not None else None,
            longitude=Decimal(str(longitude)) if longitude is not None else None,
        )
