def is_valid_rate(rate: float | None) -> bool:
    return rate is not None and rate != 0


def resolve_rate(
    *,
    client_rate: float | None = None,
    employee_rate: float | None = None,
    manager_rate: float | None = None,
) -> float:
    if is_valid_rate(client_rate):
        return float(client_rate)
    if is_valid_rate(employee_rate):
        return float(employee_rate)
    return float(manager_rate or 0.0)
