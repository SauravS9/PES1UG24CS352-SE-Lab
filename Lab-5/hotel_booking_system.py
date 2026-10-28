"""Hotel room reservation and booking management module.

Lab 5 - Static Code Analysis
Author: R Saurav Srrinivas (PES1UG24CS352)
"""

import hashlib
import json
import os
import secrets

room_inventory = {
    "101": {"type": "Deluxe", "price": 150.0, "is_booked": False},
    "102": {"type": "Suite", "price": 300.0, "is_booked": True},
    "103": {"type": "Standard", "price": 90.0, "is_booked": False},
}


def book_room(room_num, guest_name, booking_log=None):
    """Reserve a room for a guest and record it in the booking log.

    Returns True if the room was booked, False if it does not exist
    or is already booked.
    """
    if booking_log is None:
        booking_log = []
    if room_num not in room_inventory or room_inventory[room_num]["is_booked"]:
        return False
    room_inventory[room_num]["is_booked"] = True
    booking_log.append(f"Reserved room {room_num} for guest {guest_name}")
    return True


def cancel_booking(room_num):
    """Release a room reservation.

    Returns True if a booking was released, False if the room does not
    exist or was not booked in the first place.
    """
    room = room_inventory.get(room_num)
    if room is None:
        print(f"Cannot cancel: room {room_num} does not exist")
        return False
    if not room["is_booked"]:
        print(f"Cannot cancel: room {room_num} is not booked")
        return False
    room["is_booked"] = False
    return True


def check_room_status(room_num):
    """Return True if the room exists and is available to book."""
    if room_inventory.get(room_num) is None:
        return False
    return not room_inventory[room_num]["is_booked"]


def compute_seasonal_rate(room_num, surge_multiplier):
    """Return the room price after applying a seasonal surge multiplier.

    Raises KeyError for an unknown room and ValueError if the
    multiplier is not a positive number. The result is rounded to
    2 decimal places so it is a valid money amount.
    """
    if room_num not in room_inventory:
        raise KeyError(f"Unknown room: {room_num}")
    multiplier = float(surge_multiplier)
    if multiplier <= 0:
        raise ValueError("Surge multiplier must be a positive number")
    base_price = room_inventory[room_num]["price"]
    return round(base_price * multiplier, 2)


def generate_guest_hash(guest_id):
    """Return a SHA-256 hash of the guest ID."""
    return hashlib.sha256(guest_id.encode()).hexdigest()


def generate_booking_ref():
    """Return a random 4-digit booking reference number."""
    return 1000 + secrets.randbelow(9000)


def export_room_ledger(filename="hotel_ledger.txt"):
    """Write the current room inventory to a ledger file as JSON."""
    with open(filename, "w", encoding="utf-8") as ledger_file:
        json.dump(room_inventory, ledger_file, indent=2)
    print("Hotel ledger exported to:", filename)


def main():
    """Run a sample sequence of hotel booking operations."""
    hotel_secret_key = os.environ.get("HOTEL_SECRET_KEY")
    booking_log = []
    print("Book 101:", book_room("101", "Emma Watson", booking_log))
    print("Cancel 102:", cancel_booking("102"))
    print("Is 103 available:", check_room_status("103"))
    print("Surge price:", compute_seasonal_rate("101", 1.25))
    print("Guest Hash:", generate_guest_hash("GUEST_991"))
    print("Booking Reference:", generate_booking_ref())
    print("Booking log:", booking_log)
    export_room_ledger()
    print("Secret key configured:", hotel_secret_key is not None)


if __name__ == "__main__":
    main()
