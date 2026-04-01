"""
Hola语言错误处理
"""


class HolaError(Exception):
    """Hola语言基础错误"""
    pass


class TokenizeError(HolaError):
    """词法分析错误"""
    pass


class ParseError(HolaError):
    """语法分析错误"""
    pass


class CompileError(HolaError):
    """编译错误"""
    pass


class RuntimeError(HolaError):
    """运行时错误"""
    pass


class ErrorPosition:
    """错误位置信息"""
    
    def __init__(self, line: int, column: int, index: int):
        self.line = line
        self.column = column
        self.index = index
    
    def __str__(self) -> str:
        return f"line {self.line}, column {self.column}"


def format_error(error: HolaError, source: str = None, position: ErrorPosition = None) -> str:
    """格式化错误信息"""
    parts = []
    
    if position:
        parts.append(f"Error at {position}")
    else:
        parts.append("Error")
    
    parts.append(f": {error.__class__.__name__}")
    parts.append(f"\n{str(error)}")
    
    if source and position:
        lines = source.split('\n')
        if 0 <= position.line - 1 < len(lines):
            parts.append(f"\n\n{position.line} | {lines[position.line - 1]}")
            parts.append(f"{' ' * (len(str(position.line)) + 2 + position.column - 1)}^")
    
    return ''.join(parts)
