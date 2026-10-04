import re
from dataclasses import dataclass


@dataclass
class Student:
    student_id: str
    name: str

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.student_id, str):
            raise TypeError(
                f"Student ID must be a string, got {type(self.student_id).__name__}. "
                "Do not pass raw numbers like 12345."
            )
        if not isinstance(self.name, str):
            raise TypeError(
                f"Student name must be a string, got {type(self.name).__name__}."
            )

        if not self.student_id.strip():
            raise ValueError("Student ID cannot be empty or whitespace.")

        if not self.name.strip():
            raise ValueError("Student name cannot be empty or whitespace.")

        id_pattern = r"^\d{5}-\d{4}$"
        if not re.match(id_pattern, self.student_id.strip()):
            raise ValueError(
                f"Invalid Student ID format: '{self.student_id}'. "
                "Must match pattern '00000-YYYY' (5 digits followed by a 4-digit year)."
            )
