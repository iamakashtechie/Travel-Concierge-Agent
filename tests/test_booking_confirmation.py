from travel_concierge.tools.booking_confirmation import confirm_booking


def test_confirmation_requires_explicit_approval():
  result = confirm_booking(
    item_type="flight",
    selection={"airline": "Demo Air"},
  )

  assert result["status"] == "confirmation_required"


def test_confirmation_returns_demo_reference_after_approval():
  result = confirm_booking(
    item_type="hotel",
    selection={"name": "Demo Central Hotel"},
    confirmed=True,
  )

  assert result["status"] == "success"
  assert result["demo_only"] is True
  assert result["booking_reference"] == "DEMO-HOTEL-001"


def test_confirmation_rejects_unknown_item_type():
  result = confirm_booking(
    item_type="train",
    selection={"name": "Demo Train"},
    confirmed=True,
  )

  assert result["status"] == "error"