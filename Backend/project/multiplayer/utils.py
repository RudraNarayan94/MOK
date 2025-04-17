from django.utils.crypto import get_random_string
from .models import Room

def generate_unique_room_code(length=8):
    """
    Generate a random uppercase code of given length
    that does not collide with existing Room.code.
    """
    while True:
        code = get_random_string(length).upper()
        if not Room.objects.filter(code=code).exists():
            return code
