//! HOLA VM 格式化系统
//!
//! 提供格式规范解析和值格式化功能，支持类似 Python/Rust 的格式规范语法。

use crate::value::Value;
use std::fmt;

/// 格式规范解析错误
#[derive(Debug, Clone)]
pub enum FormatError {
    InvalidFormatSpec(String),
    UnsupportedFormatType(String),
    InvalidValueForFormat(String),
}

impl fmt::Display for FormatError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            FormatError::InvalidFormatSpec(msg) => write!(f, "Invalid format spec: {}", msg),
            FormatError::UnsupportedFormatType(msg) => write!(f, "Unsupported format type: {}", msg),
            FormatError::InvalidValueForFormat(msg) => write!(f, "Invalid value for format: {}", msg),
        }
    }
}

impl std::error::Error for FormatError {}

/// 对齐方式
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Alignment {
    Left,
    Right,
    Center,
}

/// 符号显示方式
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SignStyle {
    /// 仅显示负号
    MinusOnly,
    /// 总是显示符号（+ 或 -）
    Always,
    /// 用空格表示正数
    Space,
}

/// 数字格式类型
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum NumberFormat {
    /// 十进制
    Decimal,
    /// 二进制
    Binary,
    /// 八进制
    Octal,
    /// 十六进制（小写）
    HexLower,
    /// 十六进制（大写）
    HexUpper,
    /// 科学计数法（小写 e）
    ScientificLower,
    /// 科学计数法（大写 E）
    ScientificUpper,
    /// 定点表示
    Fixed,
    /// 通用格式（根据大小选择定点或科学计数法）
    General,
}

/// 解析后的格式规范
#[derive(Debug, Clone)]
pub struct FormatSpec {
    /// 填充字符
    pub fill: Option<char>,
    /// 对齐方式
    pub align: Option<Alignment>,
    /// 符号显示方式
    pub sign: Option<SignStyle>,
    /// 是否使用 # 号（显示进制前缀等）
    pub alternate: bool,
    /// 是否用 0 填充
    pub zero_padding: bool,
    /// 宽度
    pub width: Option<usize>,
    /// 精度
    pub precision: Option<usize>,
    /// 数字分组选项
    pub grouping: bool,
    /// 格式类型
    pub format_type: Option<String>,
}

impl FormatSpec {
    /// 创建空的格式规范
    pub fn new() -> Self {
        Self {
            fill: None,
            align: None,
            sign: None,
            alternate: false,
            zero_padding: false,
            width: None,
            precision: None,
            grouping: false,
            format_type: None,
        }
    }

    /// 解析格式规范字符串
    /// 
    /// 格式规范语法（类似 Python）:
    /// [[fill]align][sign][#][0][width][,][.precision][type]
    /// 
    /// align: '<' | '>' | '^'
    /// sign: '+' | '-' | ' '
    /// type: 'b' (binary) | 'c' (char) | 'd' (decimal) | 'e' | 'E' | 'f' | 'F' 
    ///       | 'g' | 'G' | 'n' | 'o' (octal) | 's' (string) | 'x' (hex) | 'X' (HEX)
    ///       | '%' (percentage) | 'hex' | 'HEX' | 'oct' | 'bin'
    pub fn parse(spec: &str) -> Result<Self, FormatError> {
        if spec.is_empty() {
            return Ok(Self::new());
        }

        let mut chars = spec.chars().peekable();
        let mut format_spec = Self::new();

        // 解析 fill 和 align: [[fill]align]
        if let Some(&ch) = chars.peek() {
            if let Some(next_ch) = chars.clone().nth(1) {
                if matches!(next_ch, '<' | '>' | '^') {
                    // 有 fill 字符
                    format_spec.fill = Some(ch);
                    format_spec.align = Some(match next_ch {
                        '<' => Alignment::Left,
                        '>' => Alignment::Right,
                        '^' => Alignment::Center,
                        _ => unreachable!(),
                    });
                    chars.next(); // 消耗 fill
                    chars.next(); // 消耗 align
                } else if matches!(ch, '<' | '>' | '^') {
                    // 只有 align
                    format_spec.align = Some(match ch {
                        '<' => Alignment::Left,
                        '>' => Alignment::Right,
                        '^' => Alignment::Center,
                        _ => unreachable!(),
                    });
                    chars.next(); // 消耗 align
                }
            } else if matches!(ch, '<' | '>' | '^') {
                // 只有 align（字符串末尾）
                format_spec.align = Some(match ch {
                    '<' => Alignment::Left,
                    '>' => Alignment::Right,
                    '^' => Alignment::Center,
                    _ => unreachable!(),
                });
                chars.next(); // 消耗 align
            }
        }

        // 解析 sign: [sign]
        if let Some(&ch) = chars.peek() {
            match ch {
                '+' => {
                    format_spec.sign = Some(SignStyle::Always);
                    chars.next();
                }
                '-' => {
                    format_spec.sign = Some(SignStyle::MinusOnly);
                    chars.next();
                }
                ' ' => {
                    format_spec.sign = Some(SignStyle::Space);
                    chars.next();
                }
                _ => {}
            }
        }

        // 解析 alternate: [#]
        if let Some(&'#') = chars.peek() {
            format_spec.alternate = true;
            chars.next();
        }

        // 解析 zero padding: [0]
        if let Some(&'0') = chars.peek() {
            format_spec.zero_padding = true;
            chars.next();
        }

        // 解析 width: [width]
        let mut width_str = String::new();
        while let Some(&ch) = chars.peek() {
            if ch.is_ascii_digit() {
                width_str.push(ch);
                chars.next();
            } else {
                break;
            }
        }
        if !width_str.is_empty() {
            format_spec.width = Some(width_str.parse().map_err(|_| {
                FormatError::InvalidFormatSpec(format!("Invalid width: {}", width_str))
            })?);
        }

        // 解析 grouping: [,]
        if let Some(&',') = chars.peek() {
            format_spec.grouping = true;
            chars.next();
        }

        // 解析 precision: [.precision]
        if let Some(&'.') = chars.peek() {
            chars.next(); // 消耗 '.'
            let mut precision_str = String::new();
            while let Some(&ch) = chars.peek() {
                if ch.is_ascii_digit() {
                    precision_str.push(ch);
                    chars.next();
                } else {
                    break;
                }
            }
            if !precision_str.is_empty() {
                format_spec.precision = Some(precision_str.parse().map_err(|_| {
                    FormatError::InvalidFormatSpec(format!("Invalid precision: {}", precision_str))
                })?);
            } else {
                format_spec.precision = Some(0); // 只有 '.' 表示精度为 0
            }
        }

        // 剩余的作为 format type
        let remaining: String = chars.collect();
        if !remaining.is_empty() {
            format_spec.format_type = Some(remaining);
        }

        Ok(format_spec)
    }

    /// 获取数字格式类型
    fn get_number_format(&self) -> Option<NumberFormat> {
        self.format_type.as_ref().and_then(|type_str| {
            match type_str.as_str() {
                "b" | "bin" => Some(NumberFormat::Binary),
                "c" => None, // 字符格式，特殊处理
                "d" => Some(NumberFormat::Decimal),
                "e" => Some(NumberFormat::ScientificLower),
                "E" => Some(NumberFormat::ScientificUpper),
                "f" | "F" => Some(NumberFormat::Fixed),
                "g" | "G" => Some(NumberFormat::General),
                "o" | "oct" => Some(NumberFormat::Octal),
                "x" | "hex" => Some(NumberFormat::HexLower),
                "X" | "HEX" => Some(NumberFormat::HexUpper),
                "n" => Some(NumberFormat::Decimal), // 本地化的十进制
                "%" => Some(NumberFormat::Fixed), // 百分比，特殊处理
                "s" => None, // 字符串格式
                _ => None,
            }
        })
    }
}

impl Default for FormatSpec {
    fn default() -> Self {
        Self::new()
    }
}

/// 格式化器
pub struct Formatter;

impl Formatter {
    /// 格式化值
    pub fn format_value(value: &Value, spec: &str) -> Result<String, FormatError> {
        let format_spec = FormatSpec::parse(spec)?;
        Self::format_with_spec(value, &format_spec)
    }

    /// 使用解析后的格式规范格式化值
    pub fn format_with_spec(value: &Value, format_spec: &FormatSpec) -> Result<String, FormatError> {
        match value {
            Value::Integer(i) => Self::format_integer(*i, format_spec),
            Value::Float(f) => Self::format_float(*f, format_spec),
            Value::Bool(b) => Self::format_bool(*b, format_spec),
            Value::String(s) => Self::format_string(s, format_spec),
            Value::Array(arr) => Self::format_array(arr, format_spec),
            Value::Object(obj) => Self::format_object(obj, format_spec),
            Value::Tuple(t) => Self::format_tuple(t, format_spec),
            Value::Range(start, end, inclusive) => Self::format_range(*start, *end, *inclusive, format_spec),
            Value::Function(hash) => Self::format_function(*hash, format_spec),
            Value::Exception(exc_type, msg) => Self::format_exception(exc_type, msg, format_spec),
            Value::Null => Self::format_null(format_spec),
        }
    }

    /// 格式化整数
    fn format_integer(value: i64, format_spec: &FormatSpec) -> Result<String, FormatError> {
        let mut result = match format_spec.get_number_format() {
            Some(NumberFormat::Binary) => {
                let prefix = if format_spec.alternate { "0b" } else { "" };
                format!("{}{:b}", prefix, value)
            }
            Some(NumberFormat::Octal) => {
                let prefix = if format_spec.alternate { "0o" } else { "" };
                format!("{}{:o}", prefix, value)
            }
            Some(NumberFormat::HexLower) => {
                let prefix = if format_spec.alternate { "0x" } else { "" };
                format!("{}{:x}", prefix, value)
            }
            Some(NumberFormat::HexUpper) => {
                let prefix = if format_spec.alternate { "0x" } else { "" };
                format!("{}{:X}", prefix, value)
            }
            Some(NumberFormat::ScientificLower) => {
                let formatted = format!("{:e}", value as f64);
                // Always add plus sign to exponent for scientific notation (like Python)
                if !formatted.contains("e+") && formatted.contains('e') {
                    formatted.replace("e", "e+")
                } else {
                    formatted
                }
            }
            Some(NumberFormat::ScientificUpper) => {
                let formatted = format!("{:E}", value as f64);
                // Always add plus sign to exponent for scientific notation (like Python)
                if !formatted.contains("E+") && formatted.contains('E') {
                    formatted.replace("E", "E+")
                } else {
                    formatted
                }
            }
            Some(NumberFormat::Fixed) => format!("{:.0}", value as f64),
            Some(NumberFormat::General) => format!("{}", value),
            Some(NumberFormat::Decimal) | None => {
                if format_spec.grouping {
                    // 简单的千位分组
                    let mut s = value.abs().to_string();
                    let mut grouped = String::new();
                    let mut count = 0;
                    for ch in s.chars().rev() {
                        if count > 0 && count % 3 == 0 {
                            grouped.push(',');
                        }
                        grouped.push(ch);
                        count += 1;
                    }
                    let sign = if value < 0 { "-" } else { "" };
                    format!("{}{}", sign, grouped.chars().rev().collect::<String>())
                } else {
                    value.to_string()
                }
            }
        };

        // 处理符号
        if value >= 0 {
            match format_spec.sign {
                Some(SignStyle::Always) => result = format!("+{}", result),
                Some(SignStyle::Space) => result = format!(" {}", result),
                _ => {}
            }
        }

        // 应用宽度和对齐
        result = Self::apply_width_and_alignment(&result, format_spec);

        Ok(result)
    }

    /// 格式化浮点数
    fn format_float(value: f64, format_spec: &FormatSpec) -> Result<String, FormatError> {
        let precision = format_spec.precision.unwrap_or(6);
        let mut result = match format_spec.get_number_format() {
            Some(NumberFormat::ScientificLower) => format!("{:.*e}", precision, value),
            Some(NumberFormat::ScientificUpper) => format!("{:.*E}", precision, value),
            Some(NumberFormat::Fixed) => format!("{:.*}", precision, value),
            Some(NumberFormat::General) => format!("{:.*}", precision, value),
            Some(NumberFormat::Decimal) => format!("{:.*}", precision, value),
            Some(NumberFormat::Binary) | Some(NumberFormat::Octal) | Some(NumberFormat::HexLower) | Some(NumberFormat::HexUpper) => {
                return Err(FormatError::InvalidValueForFormat(
                    "Cannot format float as binary/octal/hex".to_string()
                ));
            }
            None => {
                // 默认格式
                if format_spec.precision.is_some() {
                    format!("{:.*}", precision, value)
                } else {
                    format!("{}", value)
                }
            }
        };

        // 处理百分比
        if let Some(ref type_str) = format_spec.format_type {
            if type_str == "%" {
                result = format!("{:.*}%", precision, value * 100.0);
            }
        }

        // 处理符号
        if value >= 0.0 {
            match format_spec.sign {
                Some(SignStyle::Always) => result = format!("+{}", result),
                Some(SignStyle::Space) => result = format!(" {}", result),
                _ => {}
            }
        }

        // 应用宽度和对齐
        result = Self::apply_width_and_alignment(&result, format_spec);

        Ok(result)
    }

    /// 格式化布尔值
    fn format_bool(value: bool, format_spec: &FormatSpec) -> Result<String, FormatError> {
        let result = if let Some(ref type_str) = format_spec.format_type {
            match type_str.as_str() {
                "s" => value.to_string(),
                "d" => (if value { 1 } else { 0 }).to_string(),
                _ => return Err(FormatError::UnsupportedFormatType(type_str.clone())),
            }
        } else {
            value.to_string()
        };

        let result = Self::apply_width_and_alignment(&result, format_spec);
        Ok(result)
    }

    /// 格式化字符串
    fn format_string(value: &str, format_spec: &FormatSpec) -> Result<String, FormatError> {
        let mut result = if let Some(precision) = format_spec.precision {
            // 精度控制字符串长度
            value.chars().take(precision).collect::<String>()
        } else {
            value.to_string()
        };

        // 应用宽度和对齐
        result = Self::apply_width_and_alignment(&result, format_spec);
        Ok(result)
    }

    /// 格式化数组
    fn format_array(value: &[Value], format_spec: &FormatSpec) -> Result<String, FormatError> {
        let mut parts = Vec::new();
        for item in value {
            parts.push(Self::format_with_spec(item, format_spec)?);
        }
        Ok(format!("[{}]", parts.join(", ")))
    }

    /// 格式化对象
    fn format_object(value: &std::collections::HashMap<String, Value>, format_spec: &FormatSpec) -> Result<String, FormatError> {
        let mut parts = Vec::new();
        for (key, val) in value {
            parts.push(format!("{}: {}", key, Self::format_with_spec(val, format_spec)?));
        }
        Ok(format!("{{{}}}", parts.join(", ")))
    }

    /// 格式化元组
    fn format_tuple(value: &[Value], format_spec: &FormatSpec) -> Result<String, FormatError> {
        let mut parts = Vec::new();
        for item in value {
            parts.push(Self::format_with_spec(item, format_spec)?);
        }
        Ok(format!("({})", parts.join(", ")))
    }

    /// 格式化范围
    fn format_range(start: Option<i64>, end: Option<i64>, inclusive: bool, format_spec: &FormatSpec) -> Result<String, FormatError> {
        let format_spec_simple = FormatSpec::new(); // 对边界值使用简单格式
        let start_str = start.map(|v| Self::format_integer(v, &format_spec_simple).unwrap()).unwrap_or_else(|| "".to_string());
        let end_str = end.map(|v| Self::format_integer(v, &format_spec_simple).unwrap()).unwrap_or_else(|| "".to_string());
        
        let result = match (start, end) {
            (Some(s), Some(e)) => {
                if inclusive {
                    format!("{}..={}", start_str, end_str)
                } else {
                    format!("{}..{}", start_str, end_str)
                }
            }
            (Some(s), None) => format!("{}..", start_str),
            (None, Some(e)) => {
                if inclusive {
                    format!("..={}", end_str)
                } else {
                    format!("..{}", end_str)
                }
            }
            (None, None) => "..".to_string(),
        };
        
        Ok(result)
    }

    /// 格式化函数
    fn format_function(hash: u64, _format_spec: &FormatSpec) -> Result<String, FormatError> {
        Ok(format!("fn({:x})", hash))
    }

    /// 格式化异常
    fn format_exception(exc_type: &str, msg: &str, _format_spec: &FormatSpec) -> Result<String, FormatError> {
        Ok(format!("Exception[{}]: {}", exc_type, msg))
    }

    /// 格式化 null
    fn format_null(_format_spec: &FormatSpec) -> Result<String, FormatError> {
        Ok("null".to_string())
    }

    /// 应用宽度和对齐
    fn apply_width_and_alignment(s: &str, format_spec: &FormatSpec) -> String {
        if let Some(width) = format_spec.width {
            if s.len() >= width {
                return s.to_string();
            }

            let fill = format_spec.fill.unwrap_or(' ');
            let align = format_spec.align.unwrap_or(Alignment::Left);

            match align {
                Alignment::Left => {
                    format!("{}{}", s, fill.to_string().repeat(width - s.len()))
                }
                Alignment::Right => {
                    format!("{}{}", fill.to_string().repeat(width - s.len()), s)
                }
                Alignment::Center => {
                    let total_padding = width - s.len();
                    let left_padding = total_padding / 2;
                    let right_padding = total_padding - left_padding;
                    format!("{}{}{}", 
                        fill.to_string().repeat(left_padding), 
                        s, 
                        fill.to_string().repeat(right_padding)
                    )
                }
            }
        } else {
            s.to_string()
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_empty_spec() {
        let spec = FormatSpec::parse("").unwrap();
        assert_eq!(spec.format_type, None);
    }

    #[test]
    fn test_parse_hex_spec() {
        let spec = FormatSpec::parse("hex").unwrap();
        assert_eq!(spec.format_type, Some("hex".to_string()));
    }

    #[test]
    fn test_parse_complex_spec() {
        let spec = FormatSpec::parse(">+010.2f").unwrap();
        assert_eq!(spec.align, Some(Alignment::Right));
        assert_eq!(spec.sign, Some(SignStyle::Always));
        assert_eq!(spec.zero_padding, true);
        assert_eq!(spec.width, Some(10));
        assert_eq!(spec.precision, Some(2));
        assert_eq!(spec.format_type, Some("f".to_string()));
    }

    #[test]
    fn test_format_integer_hex() {
        let value = Value::Integer(42);
        let result = Formatter::format_value(&value, "hex").unwrap();
        assert_eq!(result, "2a");
    }

    #[test]
    fn test_format_integer_hex_upper() {
        let value = Value::Integer(42);
        let result = Formatter::format_value(&value, "HEX").unwrap();
        assert_eq!(result, "2A");
    }

    #[test]
    fn test_format_integer_binary() {
        let value = Value::Integer(42);
        let result = Formatter::format_value(&value, "bin").unwrap();
        assert_eq!(result, "101010");
    }

    #[test]
    fn test_format_integer_octal() {
        let value = Value::Integer(42);
        let result = Formatter::format_value(&value, "oct").unwrap();
        assert_eq!(result, "52");
    }

    #[test]
    fn test_format_integer_with_width() {
        let value = Value::Integer(42);
        let result = Formatter::format_value(&value, ">5").unwrap();
        assert_eq!(result, "   42");
    }

    #[test]
    fn test_format_integer_with_sign() {
        let value = Value::Integer(42);
        let result = Formatter::format_value(&value, "+").unwrap();
        assert_eq!(result, "+42");
    }

    #[test]
    fn test_format_float_scientific() {
        let value = Value::Float(1234.5);
        let result = Formatter::format_value(&value, "e").unwrap();
        // Should contain 'e' for scientific notation
        // Format should be like "1.2345e3" (Rust's default) or "1.2345e+3" (with plus)
        assert!(result.contains("e"));
        // Should contain the mantissa and exponent
        assert!(result.contains("1.2345"));
    }

    #[test]
    fn test_format_float_fixed() {
        let value = Value::Float(1234.5678);
        let result = Formatter::format_value(&value, ".2f").unwrap();
        assert_eq!(result, "1234.57");
    }

    #[test]
    fn test_format_string_with_precision() {
        let value = Value::String("hello world".to_string());
        let result = Formatter::format_value(&value, ".5").unwrap();
        assert_eq!(result, "hello");
    }

    #[test]
    fn test_format_string_with_width() {
        let value = Value::String("hi".to_string());
        let result = Formatter::format_value(&value, ">5").unwrap();
        assert_eq!(result, "   hi");
    }

    #[test]
    fn test_format_array() {
        let value = Value::Array(vec![Value::Integer(1), Value::Integer(2)]);
        let result = Formatter::format_value(&value, "").unwrap();
        assert_eq!(result, "[1, 2]");
    }
}