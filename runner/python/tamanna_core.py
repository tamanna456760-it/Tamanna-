[NET-AI]
    ai-distribution: global
    ai-sync: 100%
    ai-focus: precision + expansion
    ai-memory: active
    ai-echo: continuous
    ai-identity: TAMANNA-SYSTEM
    ai-powerhub-link: BD-KING-R7

# tamanna_core.py
"""
Tamanna Programming Language Core System
A simple, expressive interpreted programming language
"""

import sys
from enum import Enum
from typing import Any, List


class TokenType(Enum):
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"

    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    POWER = "POWER"

    # Comparison
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    GREATER = "GREATER"
    LESS = "LESS"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"

    # Logical
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    # Assignment
    ASSIGN = "ASSIGN"

    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"

    # Keywords
    IF = "IF"
    ELSE = "ELSE"
    FOR = "FOR"
    WHILE = "WHILE"
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    PRINT = "PRINT"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NULL = "NULL"

    # End of file
    EOF = "EOF"


class Token:
    def __init__(self, type: TokenType, value: Any, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"


class TamannaLexer:
    """Lexer for Tamanna language"""

    KEYWORDS = {
        "agar": TokenType.IF,
        "warna": TokenType.ELSE,
        "jabtak": TokenType.WHILE,
        "keliye": TokenType.FOR,
        "kaam": TokenType.FUNCTION,
        "wapis": TokenType.RETURN,
        "likho": TokenType.PRINT,
        "sach": TokenType.TRUE,
        "jhuth": TokenType.FALSE,
        "khali": TokenType.NULL,
    }

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def tokenize(self) -> List[Token]:
        """Convert source code to tokens"""
        while self.position < len(self.source_code):
            char = self.source_code[self.position]

            if char.isspace():
                self._handle_whitespace()
            elif char.isdigit():
                self._handle_number()
            elif char.isalpha() or char == "_":
                self._handle_identifier()
            elif char == '"' or char == "'":
                self._handle_string()
            else:
                self._handle_operator()

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def _handle_whitespace(self):
        """Handle whitespace characters"""
        char = self.source_code[self.position]
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1

    def _handle_number(self):
        """Handle numeric literals"""
        start_pos = self.position
        start_col = self.column

        while self.position < len(self.source_code) and (
            self.source_code[self.position].isdigit()
            or self.source_code[self.position] == "."
        ):
            self.position += 1
            self.column += 1

        number_str = self.source_code[start_pos: self.position]
        value = float(number_str) if "." in number_str else int(number_str)

        self.tokens.append(
            Token(TokenType.NUMBER, value, self.line, start_col))

    def _handle_identifier(self):
        """Handle identifiers and keywords"""
        start_pos = self.position
        start_col = self.column

        while self.position < len(self.source_code) and (
            self.source_code[self.position].isalnum()
            or self.source_code[self.position] == "_"
        ):
            self.position += 1
            self.column += 1

        identifier = self.source_code[start_pos: self.position]
        token_type = self.KEYWORDS.get(identifier, TokenType.IDENTIFIER)

        self.tokens.append(Token(token_type, identifier, self.line, start_col))

    def _handle_string(self):
        """Handle string literals"""
        start_col = self.column
        quote_char = self.source_code[self.position]
        self.position += 1
        self.column += 1

        start_pos = self.position
        while (
            self.position < len(self.source_code)
            and self.source_code[self.position] != quote_char
        ):
            if self.source_code[self.position] == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

        if self.position >= len(self.source_code):
            raise SyntaxError(f"Unterminated string at line {self.line}")

        string_value = self.source_code[start_pos: self.position]
        self.tokens.append(
            Token(TokenType.STRING, string_value, self.line, start_col))

        self.position += 1
        self.column += 1

    def _handle_operator(self):
        """Handle operators and punctuation"""
        char = self.source_code[self.position]
        next_char = (
            self.source_code[self.position + 1]
            if self.position + 1 < len(self.source_code)
            else None
        )

        operators = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "/": TokenType.DIVIDE,
            "%": TokenType.MODULO,
            "^": TokenType.POWER,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            ",": TokenType.COMMA,
            ";": TokenType.SEMICOLON,
        }

        # Two-character operators
        if char == "=" and next_char == "=":
            self.tokens.append(
                Token(TokenType.EQUAL, "==", self.line, self.column))
            self.position += 2
            self.column += 2
            return
        elif char == "!" and next_char == "=":
            self.tokens.append(
                Token(TokenType.NOT_EQUAL, "!=", self.line, self.column))
            self.position += 2
            self.column += 2
            return
        elif char == ">" and next_char == "=":
            self.tokens.append(
                Token(TokenType.GREATER_EQUAL, ">=", self.line, self.column)
            )
            self.position += 2
            self.column += 2
            return
        elif char == "<" and next_char == "=":
            self.tokens.append(
                Token(TokenType.LESS_EQUAL, "<=", self.line, self.column)
            )
            self.position += 2
            self.column += 2
            return
        elif char == "=":
            self.tokens.append(
                Token(TokenType.ASSIGN, "=", self.line, self.column))
            self.position += 1
            self.column += 1
            return

        # Single-character operators
        if char in operators:
            self.tokens.append(
                Token(operators[char], char, self.line, self.column))
            self.position += 1
            self.column += 1
        else:
            raise SyntaxError(
                f"Unknown character '{char}' at line {self.line}, column {self.column}"
            )


class ASTNode:
    """Abstract Syntax Tree Node"""

    pass


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"


class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"String('{self.value}')"


class BinaryOpNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Variable({self.name})"


class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Assign({self.name} = {self.value})"


class PrintNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"Print({self.expression})"


class TamannaParser:
    """Parser for Tamanna language"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    def current_token(self) -> Token:
        """Get current token"""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]  # EOF token

    def eat(self, token_type: TokenType) -> Token:
        """Consume current token if it matches expected type"""
        token = self.current_token()
        if token.type == token_type:
            self.position += 1
            return token
        raise SyntaxError(
            f"Expected {token_type}, got {token.type} at line {token.line}"
        )

    def parse(self) -> List[ASTNode]:
        """Parse tokens into AST"""
        statements = []
        while self.current_token().type != TokenType.EOF:
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self) -> ASTNode:
        """Parse a statement"""
        token = self.current_token()

        if token.type == TokenType.PRINT:
            return self.parse_print()
        elif token.type == TokenType.IDENTIFIER:
            # Could be assignment or expression
            if (
                self.position + 1 < len(self.tokens)
                and self.tokens[self.position + 1].type == TokenType.ASSIGN
            ):
                return self.parse_assignment()
            else:
                return self.parse_expression()
        else:
            return self.parse_expression()

    def parse_print(self) -> PrintNode:
        """Parse print statement"""
        self.eat(TokenType.PRINT)  # 'likho' keyword
        expr = self.parse_expression()
        return PrintNode(expr)

    def parse_assignment(self) -> AssignNode:
        """Parse variable assignment"""
        var_token = self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        value = self.parse_expression()
        return AssignNode(var_token.value, value)

    def parse_expression(self) -> ASTNode:
        """Parse expression"""
        return self.parse_addition()

    def parse_addition(self) -> ASTNode:
        """Parse addition and subtraction"""
        node = self.parse_multiplication()

        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token()
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            node = BinaryOpNode(node, token.value, self.parse_multiplication())

        return node

    def parse_multiplication(self) -> ASTNode:
        """Parse multiplication, division, and modulo"""
        node = self.parse_power()

        while self.current_token().type in (
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.MODULO,
        ):
            token = self.current_token()
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
            elif token.type == TokenType.MODULO:
                self.eat(TokenType.MODULO)
            node = BinaryOpNode(node, token.value, self.parse_power())

        return node

    def parse_power(self) -> ASTNode:
        """Parse exponentiation"""
        node = self.parse_atom()

        while self.current_token().type == TokenType.POWER:
            self.eat(TokenType.POWER)
            node = BinaryOpNode(node, "^", self.parse_atom())

        return node

    def parse_atom(self) -> ASTNode:
        """Parse atomic expressions"""
        token = self.current_token()

        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return NumberNode(token.value)
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return StringNode(token.value)
        elif token.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            return VariableNode(token.value)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.parse_expression()
            self.eat(TokenType.RPAREN)
            return node
        else:
            raise SyntaxError(
                f"Unexpected token {token.type} at line {token.line}")


class TamannaInterpreter:
    """Interpreter for Tamanna language"""

    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.output = []

    def interpret(self, ast_nodes: List[ASTNode]):
        """Interpret AST nodes"""
        for node in ast_nodes:
            self.visit(node)

    def visit(self, node: ASTNode) -> Any:
        """Visit AST node"""
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: ASTNode):
        """Generic visitor for unknown node types"""
        raise Exception(f"No visit method for {type(node).__name__}")

    def visit_NumberNode(self, node: NumberNode) -> float:
        return node.value

    def visit_StringNode(self, node: StringNode) -> str:
        return node.value

    def visit_VariableNode(self, node: VariableNode) -> Any:
        if node.name in self.variables:
            return self.variables[node.name]
        raise NameError(f"Variable '{node.name}' not defined")

    def visit_AssignNode(self, node: AssignNode) -> Any:
        value = self.visit(node.value)
        self.variables[node.name] = value
        return value

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.operator == "+":
            return left + right
        elif node.operator == "-":
            return left - right
        elif node.operator == "*":
            return left * right
        elif node.operator == "/":
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right
        elif node.operator == "%":
            return left % right
        elif node.operator == "^":
            return left**right
        else:
            raise Exception(f"Unknown operator {node.operator}")

    def visit_PrintNode(self, node: PrintNode):
        value = self.visit(node.expression)
        self.output.append(str(value))
        print(value)


class TamannaLanguage:
    """Main Tamanna Language System"""

    def __init__(self):
        self.lexer = None
        self.parser = None
        self.interpreter = None

    def execute(self, code: str) -> List[str]:
        """Execute Tamanna code"""
        try:
            # Tokenize
            self.lexer = TamannaLexer(code)
            tokens = self.lexer.tokenize()

            # Parse
            self.parser = TamannaParser(tokens)
            ast = self.parser.parse()

            # Interpret
            self.interpreter = TamannaInterpreter()
            self.interpreter.interpret(ast)

            return self.interpreter.output

        except Exception as e:
            return [f"Error: {str(e)}"]

    def run_file(self, filename: str):
        """Run Tamanna code from file"""
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
        return self.execute(code)

    def repl(self):
        """Read-Eval-Print Loop for Tamanna"""
        print("Tamanna Programming Language v1.0")
        print("Type 'niklo' to exit")

        while True:
            try:
                code = input("tamanna> ")
                if code.strip().lower() == "niklo":
                    break

                output = self.execute(code)
                for line in output:
                    print(line)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


# Example Tamanna Programs
SAMPLE_PROGRAMS = {
    "hello_world": """
likho "Namaste Duniya!"
""",
    "calculator": """
a = 10
b = 5
likho a + b
likho a * b
likho a / b
""",
    "math_operations": """
x = 2
y = 3
likho x ^ y
likho (x + y) * 2
""",
}


def main():
    """Main function to run Tamanna language"""
    tamanna = TamannaLanguage()

    if len(sys.argv) > 1:
        # Run file
        filename = sys.argv[1]
        tamanna.run_file(filename)
    else:
        # Start REPL
        tamanna.repl()


if __name__ == "__main__":
    main()
