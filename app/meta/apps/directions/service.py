from ..users.decorators import except_shell
from .models import Direction


class DirectionService:

    @staticmethod
    @except_shell((Direction.DoesNotExist,))
    def get_direction(title: str) -> Direction:
        return Direction.objects.get(title=title)
