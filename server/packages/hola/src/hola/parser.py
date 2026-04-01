"""
Hola语法分析器 - 包含语法解析和表达式解析
"""

from typing import List
from .tokenizer import Token, TokenKind
from .ast import (
    AstRoot, ObjectNode, PropertyValue,
    Expr, BinaryExpr, LogicalExpr, UnaryExpr, VariableExpr,
    CallExpr, GetExpr, LiteralExpr, GroupingExpr, ListExpr, ListGetExpr,
    LiteralKind, NumberValue, BinaryOperator, UnaryOperator, LogicalOperator
)
from .error import ParseError, ErrorPosition


class Precedence:
    """运算符优先级"""
    NONE = 0
    ASSIGNMENT = 1
    OR = 2
    AND = 3
    EQUALITY = 4
    COMPARISON = 5
    TERM = 6
    FACTOR = 7
    UNARY = 8
    CALL = 9
    INDEX = 10
    PRIMARY = 11


class Parser:
    """Hola语法分析器"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> AstRoot:
        """解析token列表为AST"""
        objects = []
        
        while not self._is_at_end():
            self._skip_breaks_and_comments()
            
            if self._is_at_end():
                break
            
            obj = self._parse_object()
            objects.append(obj)
            
            self._skip_breaks_and_comments()
        
        return AstRoot(objects)
    
    def _parse_object(self) -> ObjectNode:
        """解析对象"""
        # 解析类型名（可选）
        name = ""
        if self._check(TokenKind.Identifier):
            name = self._advance().value
            
            # 支持命名空间: System.Collections.Generic.List
            while self._check(TokenKind.Dot):
                self._advance()
                if self._check(TokenKind.Identifier):
                    name += "." + self._advance().value
                else:
                    raise ParseError(f"Expected identifier after '.' in type name")
        
        # 期望左大括号
        self._consume(TokenKind.LBrace, "Expected '{{' to start object block")
        self._skip_breaks_and_comments()
        
        properties = {}
        children = []
        
        while not self._check(TokenKind.RBrace) and not self._is_at_end():
            if self._check(TokenKind.PropertyName) or self._check(TokenKind.StringLiteral):
                # 解析属性
                key, value = self._parse_property()
                properties[key] = value
            elif self._check(TokenKind.Identifier) or self._check(TokenKind.LBrace):
                # 解析子对象
                child = self._parse_object()
                children.append(child)
            else:
                token = self._peek()
                raise ParseError(f"Unexpected token {token.kind.name} in object body")
            
            self._skip_separators()
        
        self._consume(TokenKind.RBrace, "Expected '}}' to close object block")
        
        return ObjectNode(name=name, properties=properties, children=children)
    
    def _parse_property(self) -> tuple[str, PropertyValue]:
        """解析属性"""
        # 属性键
        if self._check(TokenKind.PropertyName) or self._check(TokenKind.StringLiteral):
            key = self._advance().value
        else:
            token = self._peek()
            raise ParseError(f"Expected property name, found {token.kind.name}")
        
        # 期望冒号
        self._consume(TokenKind.Colon, "Expected ':' after property name")
        
        # 解析值
        value = self._parse_value()
        
        return (key, value)
    
    def _parse_value(self) -> PropertyValue:
        """解析值"""
        token = self._peek()
        
        match token.kind:
            case TokenKind.StringLiteral:
                self._advance()
                from .ast import LiteralKind
                return PropertyValue(LiteralKind(token.value))
            
            case TokenKind.NumberLiteral:
                self._advance()
                from .ast import LiteralKind, NumberValue
                # 尝试解析为整数或浮点数
                if '.' in token.value:
                    num = NumberValue(float(token.value.replace('_', '')))
                else:
                    try:
                        num = NumberValue(int(token.value.replace('_', '')))
                    except ValueError:
                        num = NumberValue(float(token.value.replace('_', '')))
                return PropertyValue(LiteralKind(num))
            
            case TokenKind.ColorLiteral:
                self._advance()
                from .ast import LiteralKind
                return PropertyValue(LiteralKind(token.value))
            
            case TokenKind.BoolLiteral:
                self._advance()
                from .ast import LiteralKind
                return PropertyValue(LiteralKind(token.value == 'true'))
            
            case TokenKind.NullLiteral:
                self._advance()
                from .ast import LiteralKind
                return PropertyValue(LiteralKind(None))
            
            case TokenKind.LBracket:
                return self._parse_list()
            
            case TokenKind.LBrace | TokenKind.Identifier:
                return PropertyValue(self._parse_object())
            
            case TokenKind.LBraceLBrace:
                return self._parse_expression_block()
            
            case _:
                raise ParseError(f"Unexpected token {token.kind.name} for value")
    
    def _parse_list(self) -> PropertyValue:
        """解析列表"""
        self._consume(TokenKind.LBracket, "Expected '[' to start list")
        
        items = []
        last_was_sep = True  # 开始时，逗号表示前导null
        
        while not self._check(TokenKind.RBracket) and not self._is_at_end():
            # 跳过换行符
            had_break = False
            while self._check(TokenKind.LineBreak) or self._check(TokenKind.Comment):
                if self._check(TokenKind.LineBreak):
                    had_break = True
                self._advance()
            
            if had_break:
                last_was_sep = True
            
            # 检查列表结束
            if self._check(TokenKind.RBracket):
                break
            
            # 处理逗号分隔符
            if self._check(TokenKind.Comma):
                self._advance()
                if last_was_sep:
                    # 前导或连续逗号 => 空位(null)
                    from .ast import LiteralKind
                    items.append(PropertyValue(LiteralKind(None)))
                last_was_sep = True
                continue
            
            # 解析元素
            value = self._parse_value()
            items.append(value)
            last_was_sep = False
        
        self._consume(TokenKind.RBracket, "Expected ']' to close list")
        
        return PropertyValue(items)
    
    def _parse_expression_block(self) -> PropertyValue:
        """解析表达式块"""
        self._consume(TokenKind.LBraceLBrace, "Expected '{{' to start expression")
        
        # 收集表达式token
        expr_tokens = []
        while not self._check(TokenKind.RBraceRBrace) and not self._is_at_end():
            expr_tokens.append(self._advance())
        
        self._consume(TokenKind.RBraceRBrace, "Expected '}}' to close expression")
        
        # 使用表达式解析器解析
        expr_parser = ExpressionParser(expr_tokens)
        expr = expr_parser.parse()
        
        return PropertyValue(expr)
    
    # ========== 辅助方法 ==========
    
    def _advance(self) -> Token:
        """前进并返回当前token"""
        if not self._is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]
    
    def _peek(self) -> Token:
        """查看当前token但不消费"""
        if self.current >= len(self.tokens):
            # 返回一个虚拟的EOF token
            return Token(TokenKind.Eof, "", 0, 0, 0)
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """返回上一个token"""
        return self.tokens[self.current - 1]
    
    def _check(self, kind: TokenKind) -> bool:
        """检查当前token是否为指定类型"""
        return self._peek().kind == kind
    
    def _is_at_end(self) -> bool:
        """检查是否到达末尾"""
        if self.current >= len(self.tokens):
            return True
        return self.tokens[self.current].kind == TokenKind.Eof
    
    def _consume(self, kind: TokenKind, message: str) -> Token:
        """消费指定类型的token，否则报错"""
        if self._check(kind):
            return self._advance()
        
        token = self._peek()
        raise ParseError(f"{message}, found {token.kind.name}")
    
    def _skip_breaks_and_comments(self):
        """跳过换行和注释"""
        while self._check(TokenKind.LineBreak) or self._check(TokenKind.Comment):
            self._advance()
    
    def _skip_separators(self):
        """跳过分隔符（逗号、换行、注释）"""
        while (self._check(TokenKind.Comma) or 
               self._check(TokenKind.LineBreak) or 
               self._check(TokenKind.Comment)):
            self._advance()


class ExpressionParser:
    """表达式解析器 - Pratt Parser实现"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> Expr:
        """解析表达式"""
        expr = self._parse_precedence(Precedence.ASSIGNMENT)
        
        if not self._is_at_end():
            token = self._peek()
            raise ParseError(f"Unexpected token {token.kind.name} after expression")
        
        return expr
    
    def _parse_precedence(self, precedence: int) -> Expr:
        """按优先级解析表达式"""
        expr = self._parse_prefix()
        
        while True:
            if self._is_at_end():
                break
            
            token = self._peek()
            next_precedence = self._get_precedence(token.kind)
            
            if precedence >= next_precedence:
                break
            
            match token.kind:
                case TokenKind.Dot:
                    expr = self._parse_get_expression(expr)
                case TokenKind.LParen:
                    expr = self._parse_call_expression(expr)
                case TokenKind.LBracket:
                    expr = self._parse_list_get(expr)
                case _:
                    expr = self._parse_infix(expr)
        
        return expr
    
    def _parse_prefix(self) -> Expr:
        """解析前缀表达式"""
        token = self._advance()
        
        match token.kind:
            case TokenKind.NumberLiteral:
                # 解析数字
                if '.' in token.value:
                    num = NumberValue(float(token.value.replace('_', '')))
                else:
                    try:
                        num = NumberValue(int(token.value.replace('_', '')))
                    except ValueError:
                        num = NumberValue(float(token.value.replace('_', '')))
                return LiteralExpr(LiteralKind(num))
            
            case TokenKind.StringLiteral:
                return LiteralExpr(LiteralKind(token.value))
            
            case TokenKind.ColorLiteral:
                return LiteralExpr(LiteralKind(token.value))
            
            case TokenKind.BoolLiteral:
                return LiteralExpr(LiteralKind(token.value == 'true'))
            
            case TokenKind.NullLiteral:
                return LiteralExpr(LiteralKind(None))
            
            case TokenKind.Identifier:
                return VariableExpr(token.value)
            
            case TokenKind.Minus | TokenKind.Bang:
                # 一元运算符
                op = UnaryOperator.Negate if token.kind == TokenKind.Minus else UnaryOperator.Not
                right = self._parse_precedence(Precedence.UNARY)
                return UnaryExpr(op, right)
            
            case TokenKind.LParen:
                # 分组表达式
                expr = self._parse_precedence(Precedence.ASSIGNMENT)
                self._consume(TokenKind.RParen, "Expected ')' after expression")
                return GroupingExpr(expr)
            
            case TokenKind.LBracket:
                # 列表字面量
                return self._parse_list_literal()
            
            case _:
                raise ParseError(f"Unexpected token {token.kind.name} in expression")
    
    def _parse_infix(self, left: Expr) -> Expr:
        """解析中缀表达式"""
        token = self._advance()
        
        match token.kind:
            case TokenKind.Plus:
                op = BinaryOperator.Add
            case TokenKind.Minus:
                op = BinaryOperator.Subtract
            case TokenKind.Star:
                op = BinaryOperator.Multiply
            case TokenKind.Slash:
                op = BinaryOperator.Divide
            case TokenKind.EqualEqual:
                op = BinaryOperator.Equal
            case TokenKind.BangEqual:
                op = BinaryOperator.NotEqual
            case TokenKind.Greater:
                op = BinaryOperator.Greater
            case TokenKind.GreaterEqual:
                op = BinaryOperator.GreaterEqual
            case TokenKind.Less:
                op = BinaryOperator.Less
            case TokenKind.LessEqual:
                op = BinaryOperator.LessEqual
            case TokenKind.AndAnd:
                # 逻辑运算符
                right = self._parse_precedence(Precedence.AND)
                return LogicalExpr(left, LogicalOperator.And, right)
            case TokenKind.OrOr:
                # 逻辑运算符
                right = self._parse_precedence(Precedence.OR)
                return LogicalExpr(left, LogicalOperator.Or, right)
            case _:
                raise ParseError(f"Unexpected infix operator {token.kind.name}")
        
        # 获取运算符优先级
        precedence = self._get_precedence(token.kind)
        right = self._parse_precedence(precedence)
        
        return BinaryExpr(left, op, right)
    
    def _parse_get_expression(self, object: Expr) -> Expr:
        """解析成员访问表达式: obj.prop"""
        self._consume(TokenKind.Dot, "Expected '.' after object")
        
        if self._check(TokenKind.Identifier):
            name = self._advance().value
            return GetExpr(object, name)
        else:
            token = self._peek()
            raise ParseError(f"Expected property name after '.', found {token.kind.name}")
    
    def _parse_call_expression(self, callee: Expr) -> Expr:
        """解析函数调用表达式: func(arg1, arg2)"""
        self._consume(TokenKind.LParen, "Expected '(' after callee")
        
        arguments = []
        
        if not self._check(TokenKind.RParen):
            arguments.append(self._parse_precedence(Precedence.ASSIGNMENT))
            
            while self._check(TokenKind.Comma):
                self._advance()
                arguments.append(self._parse_precedence(Precedence.ASSIGNMENT))
        
        self._consume(TokenKind.RParen, "Expected ')' after arguments")
        
        return CallExpr(callee, arguments)
    
    def _parse_list_get(self, list_expr: Expr) -> Expr:
        """解析列表索引表达式: list[index]"""
        self._consume(TokenKind.LBracket, "Expected '[' after list")
        
        index = self._parse_precedence(Precedence.ASSIGNMENT)
        
        self._consume(TokenKind.RBracket, "Expected ']' after index")
        
        return ListGetExpr(list_expr, index)
    
    def _parse_list_literal(self) -> Expr:
        """解析列表字面量: [expr1, expr2, ...]"""
        elements = []
        
        if not self._check(TokenKind.RBracket):
            elements.append(self._parse_precedence(Precedence.ASSIGNMENT))
            
            while self._check(TokenKind.Comma):
                self._advance()
                elements.append(self._parse_precedence(Precedence.ASSIGNMENT))
        
        self._consume(TokenKind.RBracket, "Expected ']' to close list literal")
        
        return ListExpr(elements)
    
    def _get_precedence(self, kind: TokenKind) -> int:
        """获取token的优先级"""
        precedence_map = {
            TokenKind.Equal: Precedence.ASSIGNMENT,
            TokenKind.Plus: Precedence.TERM,
            TokenKind.Minus: Precedence.TERM,
            TokenKind.Star: Precedence.FACTOR,
            TokenKind.Slash: Precedence.FACTOR,
            TokenKind.Bang: Precedence.UNARY,
            TokenKind.EqualEqual: Precedence.EQUALITY,
            TokenKind.BangEqual: Precedence.EQUALITY,
            TokenKind.Greater: Precedence.COMPARISON,
            TokenKind.GreaterEqual: Precedence.COMPARISON,
            TokenKind.Less: Precedence.COMPARISON,
            TokenKind.LessEqual: Precedence.COMPARISON,
            TokenKind.AndAnd: Precedence.AND,
            TokenKind.OrOr: Precedence.OR,
            TokenKind.Dot: Precedence.CALL,
            TokenKind.LParen: Precedence.CALL,
            TokenKind.LBracket: Precedence.INDEX,
        }
        
        return precedence_map.get(kind, Precedence.NONE)
    
    # ========== 辅助方法 ==========
    
    def _advance(self) -> Token:
        """前进并返回当前token"""
        if not self._is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]
    
    def _peek(self) -> Token:
        """查看当前token但不消费"""
        if self._is_at_end():
            return self.tokens[-1]  # 返回最后一个token
        return self.tokens[self.current]
    
    def _check(self, kind: TokenKind) -> bool:
        """检查当前token是否为指定类型"""
        if self._is_at_end():
            return False
        return self._peek().kind == kind
    
    def _is_at_end(self) -> bool:
        """检查是否到达末尾"""
        return self.current >= len(self.tokens)
    
    def _consume(self, kind: TokenKind, message: str) -> Token:
        """消费指定类型的token，否则报错"""
        if self._check(kind):
            return self._advance()
        
        token = self._peek()
        raise ParseError(f"{message}, found {token.kind.name}")
