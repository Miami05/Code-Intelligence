def calculate_sum(numbers):
    """Calculate sum of numbers."""
    return sum(numbers)

def calculate_average(numbers):
    """Calculate average."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

class MathHelper:
    """Math utility class."""
    
    def factorial(self, n):
        """Calculate factorial."""
        if n <= 1:
            return 1
        return n * self.factorial(n - 1)
    
    def fibonacci(self, n):
        """Calculate nth Fibonacci number."""
        if n <= 1:
            return n
        return self.fibonacci(n-1) + self.fibonacci(n-2)
