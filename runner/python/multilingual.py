# tamanna_multilingual.py
"""
Tamanna Programming Language - Bangla + English + Math
একটি বহুভাষিক প্রোগ্রামিং ভাষা
"""

import math
import operator
from enum import Enum
from typing import Any, List


class TokenType(Enum):
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"

    # Bangla Keywords (বাংলা কীওয়ার্ড)
    LIKHO = "LIKHO"  # লেখো (print)
    NIRNAY = "NIRNAY"  # নির্ধারণ (set/assign)
    JODI = "JODI"  # যদি (if)
    NAHOLE = "NAHOLE"  # নাহলে (else)
    JABTAK = "JABTAK"  # যতক্ষণ (while)
    JONNO = "JONNO"  # জন্য (for)
    KAJ = "KAJ"  # কাজ (function)
    FEROT = "FEROT"  # ফেরত (return)
    THAM = "THAM"  # থাম (break)
    CHOLBE = "CHOLBE"  # চলবে (continue)

    # English Keywords
    PRINT = "PRINT"
    SET = "SET"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"

    # Math Keywords (গাণিতিক অপারেটর)
    JOG = "JOG"  # যোগ (add)
    BIYOG = "BIYOG"  # বিয়োগ (subtract)
    GUN = "GUN"  # গুণ (multiply)
    BHAG = "BHAG"  # ভাগ (divide)
    SHESH = "SHESH"  # শেষ (modulo)
    GHOTON = "GHOTON"  # ঘাত (power)

    # Comparison (তুলনা)
    SOMAN = "SOMAN"  # সমান (equal)
    ASOMAN = "ASOMAN"  # অসমান (not equal)
    BORO = "BORO"  # বড় (greater)
    CHOTO = "CHOTO"  # ছোট (less)
    BORO_SOMAN = "BORO_SOMAN"  # বড় বা সমান (greater equal)
    CHOTO_SOMAN = "CHOTO_SOMAN"  # ছোট বা সমান (less equal)

    # Logical (লজিক্যাল)
    O = "O"  # বা (or)
    EBONG = "EBONG"  # এবং (and)
    NA = "NA"  # না (not)

    # Special Values
    SATYA = "SATYA"  # সত্য (true)
    MITHA = "MITHA"  # মিথ্যা (false)
    KHALI = "KHALI"  # খালি (null)

    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    POWER = "POWER"

    # Delimiters
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"

    EOF = "EOF"


class Token:
    def __init__(self, type: TokenType, value: Any, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"


class TamannaMultilingualLexer:
    """Lexer for Bangla+English+Math Tamanna Language"""

    # Mixed Bangla + English keywords
    KEYWORDS = {
        # Bangla Keywords
        "লেখো": TokenType.LIKHO,
        "নির্ধারণ": TokenType.NIRNAY,
        "যদি": TokenType.JODI,
        "নাহলে": TokenType.NAHOLE,
        "যতক্ষণ": TokenType.JABTAK,
        "জন্য": TokenType.JONNO,
        "কাজ": TokenType.KAJ,
        "ফেরত": TokenType.FEROT,
        "থাম": TokenType.THAM,
        "চলবে": TokenType.CHOLBE,
        # English Keywords
        "print": TokenType.PRINT,
        "set": TokenType.SET,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "for": TokenType.FOR,
        "function": TokenType.FUNCTION,
        "return": TokenType.RETURN,
        "break": TokenType.BREAK,
        "continue": TokenType.CONTINUE,
        # Math Operators (Bangla)
        "যোগ": TokenType.JOG,
        "বিয়োগ": TokenType.BIYOG,
        "গুণ": TokenType.GUN,
        "ভাগ": TokenType.BHAG,
        "শেষ": TokenType.SHESH,
        "ঘাত": TokenType.GHOTON,
        # Comparison
        "সমান": TokenType.SOMAN,
        "অসমান": TokenType.ASOMAN,
        "বড়": TokenType.BORO,
        "ছোট": TokenType.CHOTO,
        "বড়সমান": TokenType.BORO_SOMAN,
        "ছোটসমান": TokenType.CHOTO_SOMAN,
        # Logical
        "বা": TokenType.O,
        "এবং": TokenType.EBONG,
        "না": TokenType.NA,
        # Special Values
        "সত্য": TokenType.SATYA,
        "মিথ্যা": TokenType.MITHA,
        "খালি": TokenType.KHALI,
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
            elif (
                char.isalpha()
                or char in "অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়"
            ):
                self._handle_identifier()
            elif char == '"' or char == "'" or char == "`":
                self._handle_string()
            else:
                self._handle_operator()

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def _handle_whitespace(self):
        char = self.source_code[self.position]
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1

    def _handle_number(self):
        start_pos = self.position
        start_col = self.column

        # Handle integers and floats
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
        start_pos = self.position
        start_col = self.column

        # Allow Bangla characters, English letters, numbers, and underscores
        while self.position < len(self.source_code) and (
            self.source_code[self.position].isalnum()
            or self.source_code[self.position] == "_"
            or self.source_code[self.position]
            in "অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়"
        ):
            self.position += 1
            self.column += 1

        identifier = self.source_code[start_pos: self.position]
        token_type = self.KEYWORDS.get(identifier, TokenType.IDENTIFIER)

        self.tokens.append(Token(token_type, identifier, self.line, start_col))

    def _handle_string(self):
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
            "=": TokenType.SOMAN,
            "!": TokenType.NA,
        }

        # Two-character operators
        if char == "=" and next_char == "=":
            self.tokens.append(
                Token(TokenType.SOMAN, "==", self.line, self.column))
            self.position += 2
            self.column += 2
            return
        elif char == "!" and next_char == "=":
            self.tokens.append(
                Token(TokenType.ASOMAN, "!=", self.line, self.column))
            self.position += 2
            self.column += 2
            return
        elif char == ">" and next_char == "=":
            self.tokens.append(
                Token(TokenType.BORO_SOMAN, ">=", self.line, self.column)
            )
            self.position += 2
            self.column += 2
            return
        elif char == "<" and next_char == "=":
            self.tokens.append(
                Token(TokenType.CHOTO_SOMAN, "<=", self.line, self.column)
            )
            self.position += 2
            self.column += 2
            return
        elif char == ">" and next_char != "=":
            self.tokens.append(
                Token(TokenType.BORO, ">", self.line, self.column))
            self.position += 1
            self.column += 1
            return
        elif char == "<" and next_char != "=":
            self.tokens.append(
                Token(TokenType.CHOTO, "<", self.line, self.column))
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


# AST Nodes (same as before with enhancements)
class ASTNode:
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


class IfNode(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While({self.condition}, {self.body})"


class TamannaMultilingualParser:
    """Parser for multilingual Tamanna"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    def current_token(self) -> Token:
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]

    def eat(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type == token_type:
            self.position += 1
            return token
        raise SyntaxError(
            f"Expected {token_type}, got {token.type} at line {token.line}"
        )

    def parse(self) -> List[ASTNode]:
        statements = []
        while self.current_token().type != TokenType.EOF:
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self) -> ASTNode:
        token = self.current_token()

        if token.type in [TokenType.LIKHO, TokenType.PRINT]:
            return self.parse_print()
        elif token.type in [TokenType.JODI, TokenType.IF]:
            return self.parse_if()
        elif token.type in [TokenType.JABTAK, TokenType.WHILE]:
            return self.parse_while()
        elif token.type == TokenType.IDENTIFIER:
            if self.position + 1 < len(self.tokens) and self.tokens[
                self.position + 1
            ].type in [TokenType.SOMAN, TokenType.NIRNAY]:
                return self.parse_assignment()
            else:
                return self.parse_expression()
        else:
            return self.parse_expression()

    def parse_print(self) -> PrintNode:
        # Handle both Bangla and English print
        if self.current_token().type in [TokenType.LIKHO, TokenType.PRINT]:
            self.eat(self.current_token().type)
        expr = self.parse_expression()
        return PrintNode(expr)

    def parse_assignment(self) -> AssignNode:
        var_token = self.eat(TokenType.IDENTIFIER)
        # Handle both Bangla and English assignment
        if self.current_token().type in [TokenType.SOMAN, TokenType.NIRNAY]:
            self.eat(self.current_token().type)
        value = self.parse_expression()
        return AssignNode(var_token.value, value)

    def parse_if(self) -> IfNode:
        # Handle both Bangla and English if
        if self.current_token().type in [TokenType.JODI, TokenType.IF]:
            self.eat(self.current_token().type)

        condition = self.parse_expression()
        then_branch = self.parse_statement()

        else_branch = None
        if self.current_token().type in [TokenType.NAHOLE, TokenType.ELSE]:
            self.eat(self.current_token().type)
            else_branch = self.parse_statement()

        return IfNode(condition, then_branch, else_branch)

    def parse_while(self) -> WhileNode:
        # Handle both Bangla and English while
        if self.current_token().type in [TokenType.JABTAK, TokenType.WHILE]:
            self.eat(self.current_token().type)

        condition = self.parse_expression()
        body = self.parse_statement()

        return WhileNode(condition, body)

    def parse_expression(self) -> ASTNode:
        return self.parse_comparison()

    def parse_comparison(self) -> ASTNode:
        node = self.parse_addition()

        while self.current_token().type in [
            TokenType.SOMAN,
            TokenType.ASOMAN,
            TokenType.BORO,
            TokenType.CHOTO,
            TokenType.BORO_SOMAN,
            TokenType.CHOTO_SOMAN,
        ]:
            token = self.current_token()
            self.eat(token.type)
            node = BinaryOpNode(node, token.value, self.parse_addition())

        return node

    def parse_addition(self) -> ASTNode:
        node = self.parse_multiplication()

        while self.current_token().type in [
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.JOG,
            TokenType.BIYOG,
        ]:
            token = self.current_token()
            self.eat(token.type)
            node = BinaryOpNode(node, token.value, self.parse_multiplication())

        return node

    def parse_multiplication(self) -> ASTNode:
        node = self.parse_power()

        while self.current_token().type in [
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.MODULO,
            TokenType.GUN,
            TokenType.BHAG,
            TokenType.SHESH,
        ]:
            token = self.current_token()
            self.eat(token.type)
            node = BinaryOpNode(node, token.value, self.parse_power())

        return node

    def parse_power(self) -> ASTNode:
        node = self.parse_atom()

        while self.current_token().type in [TokenType.POWER, TokenType.GHOTON]:
            token = self.current_token()
            self.eat(token.type)
            node = BinaryOpNode(node, token.value, self.parse_atom())

        return node

    def parse_atom(self) -> ASTNode:
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
        elif token.type in [TokenType.SATYA, TokenType.MITHA]:
            self.eat(token.type)
            return NumberNode(1 if token.type == TokenType.SATYA else 0)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.parse_expression()
            self.eat(TokenType.RPAREN)
            return node
        else:
            raise SyntaxError(
                f"Unexpected token {token.type} at line {token.line}")


class TamannaMultilingualInterpreter:
    """Interpreter for multilingual Tamanna"""

    def __init__(self):
        self.variables = {
            "pi": math.pi,
            "e": math.e,
            "গণিত_pi": math.pi,
            "গণিত_e": math.e,
        }
        self.functions = {}
        self.output = []

    def interpret(self, ast_nodes: List[ASTNode]):
        for node in ast_nodes:
            self.visit(node)

    def visit(self, node: ASTNode) -> Any:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: ASTNode):
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

    def visit_PrintNode(self, node: PrintNode):
        value = self.visit(node.expression)
        self.output.append(str(value))
        print(value)

    def visit_IfNode(self, node: IfNode):
        condition = self.visit(node.condition)
        if condition:
            self.visit(node.then_branch)
        elif node.else_branch:
            self.visit(node.else_branch)

    def visit_WhileNode(self, node: WhileNode):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)

        operator_map = {
            "+": operator.add,
            "যোগ": operator.add,
            "JOG": operator.add,
            "-": operator.sub,
            "বিয়োগ": operator.sub,
            "BIYOG": operator.sub,
            "*": operator.mul,
            "গুণ": operator.mul,
            "GUN": operator.mul,
            "/": operator.truediv,
            "ভাগ": operator.truediv,
            "BHAG": operator.truediv,
            "%": operator.mod,
            "শেষ": operator.mod,
            "SHESH": operator.mod,
            "^": operator.pow,
            "ঘাত": operator.pow,
            "GHOTON": operator.pow,
            "==": operator.eq,
            "সমান": operator.eq,
            "SOMAN": operator.eq,
            "!=": operator.ne,
            "অসমান": operator.ne,
            "ASOMAN": operator.ne,
            ">": operator.gt,
            "বড়": operator.gt,
            "BORO": operator.gt,
            "<": operator.lt,
            "ছোট": operator.lt,
            "CHOTO": operator.lt,
            ">=": operator.ge,
            "বড়সমান": operator.ge,
            "BORO_SOMAN": operator.ge,
            "<=": operator.le,
            "ছোটসমান": operator.le,
            "CHOTO_SOMAN": operator.le,
        }

        if node.operator in operator_map:
            return operator_map[node.operator](left, right)
        else:
            raise Exception(f"Unknown operator {node.operator}")


class TamannaMultilingual:
    """Main Multilingual Tamanna System"""

    def __init__(self):
        self.lexer = None
        self.parser = None
        self.interpreter = None

    def execute(self, code: str) -> List[str]:
        try:
            self.lexer = TamannaMultilingualLexer(code)
            tokens = self.lexer.tokenize()

            self.parser = TamannaMultilingualParser(tokens)
            ast = self.parser.parse()

            self.interpreter = TamannaMultilingualInterpreter()
            self.interpreter.interpret(ast)

            return self.interpreter.output

        except Exception as e:
            return [f"Error: {str(e)}"]

    def repl(self):
        """Read-Eval-Print Loop"""
        print("Tamanna Programming Language - Bangla + English + Math")
        print("বাংলা + ইংরেজি + গণিত প্রোগ্রামিং ভাষা")
        print("Type 'exit' or 'প্রস্থান' to exit\n")

        while True:
            try:
                code = input("তামান্না> ")
                if code.strip().lower() in ["exit", "প্রস্থান"]:
                    break

                output = self.execute(code)
                for line in output:
                    print(line)

            except KeyboardInterrupt:
                print("\nবিদায়! (Goodbye!)")
                break
            except Exception as e:
                print(f"ত্রুটি: {e}")


# Example Programs in Mixed Languages
SAMPLE_PROGRAMS = {
    "hello_bangla": """
লেখো "স্বাগতম তামান্না প্রোগ্রামিং ভাষায়!"
লেখো "Welcome to Tamanna Programming Language!"
""",
    "math_operations": """
নির্ধারণ x = 10
নির্ধারণ y = 3

লেখো "যোগ: " + (x + y)
লেখো "বিয়োগ: " + (x - y) 
লেখো "গুণ: " + (x * y)
লেখো "ভাগ: " + (x / y)
লেখো "ঘাত: " + (x ^ y)
""",
    "mixed_language": """
set নাম = "তামান্না"
নির্ধারণ বয়স = 25

print "Name: " + নাম
লেখো "Age: " + বয়স

যদি বয়স > 18:
    লেখো "বড় হয়েছে!"
নাহলে:
    print "Still young!"
""",
    "calculator": """
নির্ধারণ a = 15
set b = 4

লেখো "যোগ: " + (a যোগ b)
লেখো "বিয়োগ: " + (a বিয়োগ b)
লেখো "গুণ: " + (a গুণ b) 
লেখো "ভাগ: " + (a ভাগ b)
লেখো "শেষ: " + (a শেষ b)
""",
    "advanced_math": """
নির্ধারণ ব্যাস = 10
নির্ধারণ ব্যাসার্ধ = ব্যাস / 2
নির্ধারণ পরিধি = 2 * গণিত_pi * ব্যাসার্ধ
নির্ধারণ ক্ষেত্রফল = গণিত_pi * ব্যাসার্ধ ^ 2

লেখো "ব্যাস: " + ব্যাস
লেখো "পরিধি: " + পরিধি
লেখো "ক্ষেত্রফল: " + ক্ষেত্রফল
""",
}


class MathLibrary:
    """Mathematical function library for Tamanna"""

    @staticmethod
    def যোগ(a, b):
        return a + b

    @staticmethod
    def বিয়োগ(a, b):
        return a - b

    @staticmethod
    def গুণ(a, b):
        return a * b

    @staticmethod
    def ভাগ(a, b):
        return a / b

    @staticmethod
    def ঘাত(a, b):
        return a**b

    @staticmethod
    def বর্গ(a):
        return a**2

    @staticmethod
    def বর্গমূল(a):
        return math.sqrt(a)

    @staticmethod
    def পরিধি(ব্যাসার্ধ):
        return 2 * math.pi * ব্যাসার্ধ

    @staticmethod
    def ক্ষেত্রফল(ব্যাসার্ধ):
        return math.pi * (ব্যাসার্ধ**2)


def main():
    """Main function"""
    tamanna = TamannaMultilingual()

    # Add math functions to interpreter
    math_lib = MathLibrary()
    tamanna.interpreter = TamannaMultilingualInterpreter()

    for method_name in dir(math_lib):
        if not method_name.startswith("_"):
            method = getattr(math_lib, method_name)
            tamanna.interpreter.functions[method_name] = method

    print("=== Tamanna Language Examples ===")
    print("তামান্না ভাষার উদাহরণ\n")

    for name, code in SAMPLE_PROGRAMS.items():
        print(f"\n--- {name} ---")
        print("Code:")
        print(code)
        print("Output:")
        output = tamanna.execute(code)
        for line in output:
            print(line)
        print("-" * 40)

    # Start REPL
    print("\nStarting REPL...")
    tamanna.repl()


if __name__ == "__main__":
    main()
