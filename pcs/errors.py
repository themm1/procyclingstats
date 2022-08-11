from typing import Any, Optional


class ExpectedParsingError(Exception):
    """
    Exception to raise when data can't be parsed due to some known factor

    :param message: exception message to print when raised
    """

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class UnexpectedParsingError(ExpectedParsingError):
    """
    Exception to raise when data can't be parsed due to some unknown factor

    :param message: exception message to print when raised
    """

    def __init__(self,
                 message: str = "Unexpected parsing error occured") -> None:
        super().__init__(message)


class ParsedValueInvalidError(Exception):
    """
    Exception to raise when parsed value didn't pass some kind of validity check

    :param message: exception message to print when raised
    """

    def __init__(self, value: Any,
                 custom_message: Optional[str] = None) -> None:
        self.value = value
        self.custom_message = custom_message

    def __str__(self) -> str:
        if self.custom_message:
            return self.custom_message
        return f"Parsed value '{self.value}' didn't pass validity check. "
