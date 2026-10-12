"""
DComp320 - Data Structures and Algorithm
Assignment: Stacks Implementation

This program reads mathematical expressions from input.txt, evaluates them
using stack-based processing, and writes the results to output.txt.
No Python eval() or external expression-evaluation library is used.
"""

from __future__ import annotations

import re
import math
from typing import List, Union


Number = Union[int, float]


class Stack:
    """A simple LIFO stack implementation using a Python list."""

    def __init__(self) -> None:
        self._items: List[object] = []

    def push(self, item: object) -> None:
        """Add an item to the top of the stack."""
        self._items.append(item)

    def pop(self) -> object:
        """Remove and return the top item."""
        if self.is_empty():
            raise IndexError("Cannot pop from an empty stack.")
        return self._items.pop()

    def peek(self) -> object:
        """Return the top item without removing it."""
        if self.is_empty():
            raise IndexError("Cannot peek at an empty stack.")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Return True when the stack contains no items."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the number of items currently in the stack."""
        return len(self._items)


# Numbers, operators, and parentheses. Whitespace is ignored.
TOKEN_PATTERN = re.compile(r"\d+(?:\.\d+)?|[()+\-*/]")


def tokenize(expression: str) -> List[str]:
    """Convert an expression into tokens and reject unsupported characters."""
    expression = expression.strip()
    if not expression:
        raise ValueError("Expression is empty.")

    tokens: List[str] = []
    position = 0

    for match in TOKEN_PATTERN.finditer(expression):
        # Any non-whitespace text between recognized tokens is invalid.
        gap = expression[position:match.start()]
        if gap.strip():
            raise ValueError(f"Invalid character(s): {gap.strip()}")
        tokens.append(match.group())
        position = match.end()

    if expression[position:].strip():
        raise ValueError(f"Invalid character(s): {expression[position:].strip()}")

    return tokens


def precedence(operator: str) -> int:
    """Return precedence for a supported operator."""
    if operator in ("+", "-"):
        return 1
    if operator in ("*", "/"):
        return 2
    raise ValueError(f"Unsupported operator: {operator}")


def apply_operator(values: Stack, operator: str) -> None:
    """Pop two operands, apply an operator, and push the result."""
    try:
        right = values.pop()
        left = values.pop()
    except IndexError as exc:
        raise ValueError("Invalid expression: insufficient operands.") from exc

    if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
        raise ValueError("Invalid operand.")

    if operator == "+":
        result = left + right
    elif operator == "-":
        result = left - right
    elif operator == "*":
        result = left * right
    elif operator == "/":
        if right == 0:
            raise ZeroDivisionError("Division by zero is not allowed.")
        result = left / right
    else:
        raise ValueError(f"Unsupported operator: {operator}")

    values.push(result)


def evaluate_expression(expression: str) -> Number:
    """
    Evaluate an infix mathematical expression using two stacks.

    The value stack stores numbers. The operator stack stores operators
    and parentheses. Operator precedence is applied before lower-precedence
    operators, and parentheses are evaluated first.
    """
    tokens = tokenize(expression)
    values = Stack()
    operators = Stack()

    expect_operand = True

    for token in tokens:
        if re.fullmatch(r"\d+(?:\.\d+)?", token):
            number: Number = float(token) if "." in token else int(token)
            values.push(number)
            expect_operand = False

        elif token == "(":
            operators.push(token)
            expect_operand = True

        elif token == ")":
            if expect_operand:
                raise ValueError("Invalid expression near ')'.")
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(values, operators.pop())
            if operators.is_empty():
                raise ValueError("Mismatched parentheses.")
            operators.pop()  # Remove '('
            expect_operand = False

        elif token in "+-*/":
            if expect_operand:
                raise ValueError(f"Operator '{token}' cannot appear here.")

            while (
                not operators.is_empty()
                and operators.peek() != "("
                and precedence(str(operators.peek())) >= precedence(token)
            ):
                apply_operator(values, operators.pop())

            operators.push(token)
            expect_operand = True

        else:
            raise ValueError(f"Unsupported token: {token}")

    if expect_operand:
        raise ValueError("Expression cannot end with an operator.")

    while not operators.is_empty():
        if operators.peek() == "(":
            raise ValueError("Mismatched parentheses.")
        apply_operator(values, operators.pop())

    if values.size() != 1:
        raise ValueError("Invalid expression.")

    return values.pop()  # type: ignore[return-value]


def format_result(result: Number) -> str:
    """Format numeric output without unnecessary trailing .0 or zeros."""
    if isinstance(result, float):
        if math.isclose(result, 0.0, abs_tol=1e-12):
            result = 0.0
        if result.is_integer():
            return str(int(result))
        return f"{result:.10f}".rstrip("0").rstrip(".")
    return str(result)


def process_file(input_file: str = "input.txt", output_file: str = "output.txt") -> None:
    """
    Read expressions and separators from input.txt and write evaluated
    results in the same structure to output.txt.
    """
    with open(input_file, "r", encoding="utf-8") as file:
        lines = [line.rstrip("\n\r") for line in file]

    output_lines: List[str] = []

    for line in lines:
        stripped = line.strip()

        # A line containing no expression/operator content is preserved.
        if not stripped:
            output_lines.append(line)
            continue

        # Separators are lines made only from non-alphanumeric punctuation.
        # The assignment example uses -----.
        if re.fullmatch(r"([-=_*#~.])\1{2,}", stripped):
            output_lines.append(line)
            continue

        try:
            result = evaluate_expression(stripped)
            output_lines.append(format_result(result))
        except Exception as exc:
            # Keep processing subsequent expressions rather than terminating.
            output_lines.append(f"ERROR: {exc}")

    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(output_lines))
        if output_lines:
            file.write("\n")


if __name__ == "__main__":
    process_file()
    print("Evaluation complete. Results written to output.txt.")
