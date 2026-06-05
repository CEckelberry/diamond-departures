# apps/api/app/watch_boards.py
from __future__ import annotations

from collections.abc import Callable

BoardLister        = Callable[[str], list[dict]]
BoardCreator       = Callable[[str, str], dict]
BoardGetter        = Callable[[str, str], dict | None]
BoardRenamer       = Callable[[str, str, str], bool]
BoardDeleter       = Callable[[str, str], bool]
BoardPlayerAdder   = Callable[[str, str, int], bool]
BoardPlayerRemover = Callable[[str, str, int], bool]


def in_memory_board_lister(user_id: str) -> list[dict]: return []
def in_memory_board_creator(user_id: str, name: str) -> dict: return {"id": "stub", "user_id": user_id, "name": name}
def in_memory_board_getter(board_id: str, user_id: str) -> dict | None: return None
def in_memory_board_renamer(board_id: str, user_id: str, name: str) -> bool: return False
def in_memory_board_deleter(board_id: str, user_id: str) -> bool: return False
def in_memory_board_player_adder(board_id: str, user_id: str, player_id: int) -> bool: return False
def in_memory_board_player_remover(board_id: str, user_id: str, player_id: int) -> bool: return False
