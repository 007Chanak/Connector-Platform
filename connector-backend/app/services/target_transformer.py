def transform_using_target_mapping(
    unified_record,
    mapping
):

    payload = {}

    for unified_field, target_field in mapping.items():

        payload[target_field] = (
            unified_record.get(
                unified_field
            )
        )

    return payload