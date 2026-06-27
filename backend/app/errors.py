# encoding: utf-8

class BackendError(Exception):
    """Base class for exceptions in the backend.

    Attributes:
        message (str): The error message.
        context (str): The context in which the error occurred.

    Example:
        raise BackendError(
            message=f"My error message",
            context=f"expected {int.__name__}, got {type(1.0).__name__}"
        )
    """

    def __init__(self, message, context=None):
        """Initializes the BackendError instance.

        Args:
            message (str): The error message.
            context (str): The context in which the error occurred.
        """
        self.message = message
        self.context = context
        super().__init__(self.message)

    def __str__(self):
        context = f"({self.context})" if self.context else ""
        return f"{self.__class__.__name__}: {self.message} {context}"

    def __repr__(self):
        return str(self)


def demo():
    """Demonstrates how to use the BackendError class."""

    try:
        raise BackendError(
            message="My error message",
            context=f"expected {int.__name__}, got {type(1.0).__name__}"
        )

    except BackendError as e:
        print(e)


if __name__ == '__main__':
    demo()