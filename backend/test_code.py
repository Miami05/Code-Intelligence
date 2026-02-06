def hello_world():
    """Greet the world."""
    print("Hello, World!")


def add_numbers(a, b):
    """Add two numbers."""
    return a + b


def multiply(x, y):
    """Multiply two numbers."""
    return x * y


class Calculator:
    """Simple calculator."""

    def divide(self, x, y):
        """Divide x by y."""
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y

    def power(self, base, exp):
        """Calculate base^exp."""
        return base**exp


class StringHelper:
    """String utilities."""

    def reverse(self, text):
        """Reverse a string."""
        return text[::-1]

    def uppercase(self, text):
        """Convert to uppercase."""
        return text.upper()


if __name__ == "__main__":
    calc = Calculator()
    print(calc.divide(10, 2))
