"""
Hola语言Python实现

提供parser、compiler和vm功能
"""

from .tokenizer import Tokenizer, Token, TokenKind
from .parser import Parser, ExpressionParser
from .ast import AstRoot, ObjectNode, PropertyValue, Expr
from .compiler import Compiler
from .vm import VM

__version__ = "0.1.0"
__all__ = [
    "Tokenizer",
    "Token",
    "TokenKind",
    "Parser",
    "ExpressionParser",
    "AstRoot",
    "ObjectNode",
    "PropertyValue",
    "Expr",
    "Compiler",
    "VM",
]


def compile(source: str) -> dict:
    """
    编译Hola源代码为JSON格式
    
    Args:
        source: Hola源代码字符串
        
    Returns:
        编译后的JSON字典
    """
    tokenizer = Tokenizer(source)
    tokens = tokenizer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    compiler = Compiler()
    return compiler.compile(ast)


def evaluate_expression(expr: Expr, context: dict = None) -> any:
    """
    求值表达式
    
    Args:
        expr: 表达式AST节点
        context: 变量上下文
        
    Returns:
        求值结果
    """
    vm = VM(context or {})
    return vm.evaluate(expr)