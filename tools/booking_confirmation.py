def confirm_booking(
  item_type: str,
  selection: dict,
  confirmed: bool = False,
) -> dict:
  """Returns a deterministic demo confirmation after explicit approval."""

  if not confirmed:
    return {
      "status": "confirmation_required",
      "message": "Explicit user confirmation is required before proceeding.",
    }

  if item_type not in {"flight", "hotel", "activity"}:
    return {
      "status": "error",
      "message": "item_type must be flight, hotel, or activity.",
    }

  if not isinstance(selection, dict) or not selection:
    return {
      "status": "error",
      "message": "A selected booking option is required.",
    }

  return {
    "status": "success",
    "demo_only": True,
    "message": "Demo confirmation created. No real reservation or payment was made.",
    "booking_reference": f"DEMO-{item_type.upper()}-001",
    "item_type": item_type,
    "selection": selection,
  }