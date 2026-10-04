from dataclasses import dataclass


@dataclass
class User:
    username: str
    id: int | None = None

    def __post_init__(self) -> None:
        self.username = self.username.strip()
        if len(self.username) < 3:
            raise ValueError("Username must have at least 3 characters.")
        if len(self.username) > 30:
            raise ValueError("Username must not exceed 30 characters.")