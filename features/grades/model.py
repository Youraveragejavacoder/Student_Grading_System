import re
from dataclasses import dataclass

@dataclass
class Grade:
    student_id: str
    subject: str
    score: float

    def __post_init__(self):
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.student_id, str):
            raise TypeError(
                f"Student ID must be a string, got {type(self.student_id).__name__}."
            )
        if not isinstance(self.subject, str):
            raise TypeError(
                f"Subject must be a string, got {type(self.subject).__name__}."
            )
        if isinstance(self.score, bool) or not isinstance(self.score, (int, float)):
            raise TypeError(
                f"Score must be a number (int or float), got {type(self.score).__name__}."
            )

        if not self.student_id.strip():
            raise ValueError("Student ID cannot be empty or whitespace.")
        if not self.subject.strip():
            raise ValueError("Subject cannot be empty or whitespace.")

        id_pattern = r"^\d{5}-\d{4}$"
        if not re.match(id_pattern, self.student_id.strip()):
            raise ValueError(
                f"Invalid Student ID format: '{self.student_id}'. "
                "Must match pattern '00000-YYYY' (5 digits followed by a 4-digit year)."
            )

        float_score = float(self.score)
        if float_score < 0.0 or float_score > 100.0:
            raise ValueError(f"Score must be between 0.0 and 100.0, got {self.score}.")
