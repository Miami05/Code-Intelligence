from utils import calculate_sum, MathHelper
from database import get_connection

def main():
    """Main entry point."""
    numbers = [1, 2, 3, 4, 5]
    total = calculate_sum(numbers)
    print(f"Sum: {total}")
    
    math = MathHelper()
    print(f"5! = {math.factorial(5)}")

if __name__ == "__main__":
    main()
