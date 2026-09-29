def get_destination_info(destination: str) -> dict:
	"""Returns basic information about a travel destination.

	Args:
		destination: The city the user wants information about.

	Returns:
		A dictionary containing basic destination information.
	"""

	destinations = {
		"amsterdam": {
			"country": "Netherlands",
			"continent": "Europe",
			"currency": "Euro",
			"language": "Dutch",
		},
		"kolkata": {
			"country": "India",
			"continent": "Asia",
			"currency": "Indian Rupee",
			"language": "Bengali",
		},
		"tokyo": {
			"country": "Japan",
			"continent": "Asia",
			"currency": "Japanese Yen",
			"language": "Japanese",
		},
	}

	result = destinations.get(destination.lower())

	if result is None:
		return {
			"error": f"I don't have information about {destination}."
		}

	return result