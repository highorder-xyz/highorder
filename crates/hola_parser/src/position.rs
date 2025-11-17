/// Byte position in source code
#[derive(Debug, Copy, Clone, PartialEq, PartialOrd, Eq, Ord, Default)]
pub struct BytePos(pub u32);

impl BytePos {
    /// Shift the position by the length of a character
    pub fn shift(self, ch: char) -> Self {
        BytePos(self.0 + ch.len_utf8() as u32)
    }

    /// Create a new position from an offset
    pub fn from_offset(offset: usize) -> Self {
        BytePos(offset as u32)
    }
}

/// A span of source code
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
pub struct Span {
    pub start: BytePos,
    pub end: BytePos,
}

impl Span {
    /// Create a new span from start and end positions
    pub fn new(start: BytePos, end: BytePos) -> Self {
        Span { start, end }
    }

    /// Create a new span from unchecked offsets
    pub fn new_unchecked(start: u32, end: u32) -> Self {
        Span {
            start: BytePos(start),
            end: BytePos(end),
        }
    }

    /// Create an empty span
    pub const fn empty() -> Self {
        Span {
            start: BytePos(0),
            end: BytePos(0),
        }
    }

    /// Union two spans
    pub fn union_span(a: Self, b: Self) -> Self {
        use std::cmp;

        Span {
            start: cmp::min(a.start, b.start),
            end: cmp::max(a.end, b.end),
        }
    }

    /// Union two WithSpan values
    pub fn union<A, B>(a: &WithSpan<A>, b: &WithSpan<B>) -> Self {
        Self::union_span(a.span, b.span)
    }

    /// Get the length of the span
    pub fn len(&self) -> usize {
        (self.end.0 - self.start.0) as usize
    }

    /// Check if the span is empty
    pub fn is_empty(&self) -> bool {
        self.start == self.end
    }
}

impl<T> From<WithSpan<T>> for Span {
    fn from(with_span: WithSpan<T>) -> Span {
        with_span.span
    }
}

impl<T> From<&WithSpan<T>> for Span {
    fn from(with_span: &WithSpan<T>) -> Span {
        with_span.span
    }
}

/// A value with associated source span
#[derive(Debug, PartialEq, Clone)]
pub struct WithSpan<T> {
    pub value: T,
    pub span: Span,
}

impl<T> WithSpan<T> {
    /// Create a new value with span
    pub const fn new(value: T, span: Span) -> Self {
        WithSpan { value, span }
    }

    /// Create a value with empty span
    pub const fn empty(value: T) -> Self {
        Self {
            value,
            span: Span::empty(),
        }
    }

    /// Create a value with unchecked span
    pub fn new_unchecked(value: T, start: u32, end: u32) -> Self {
        Self {
            value,
            span: Span {
                start: BytePos(start),
                end: BytePos(end),
            },
        }
    }

    /// Get a reference with the same span
    pub const fn as_ref(&self) -> WithSpan<&T> {
        WithSpan {
            span: self.span,
            value: &self.value,
        }
    }

    /// Map the value while preserving the span
    pub fn map<U, F>(self, f: F) -> WithSpan<U>
    where
        F: FnOnce(T) -> U,
    {
        WithSpan {
            value: f(self.value),
            span: self.span,
        }
    }
}

/// Diagnostic severity level
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DiagnosticLevel {
    Error,
    Warning,
    Info,
}

/// A diagnostic message with location
#[derive(Debug, Clone, PartialEq)]
pub struct Diagnostic {
    pub level: DiagnosticLevel,
    pub span: Span,
    pub message: String,
}

impl Diagnostic {
    /// Create an error diagnostic
    pub fn error(span: Span, message: String) -> Self {
        Diagnostic {
            level: DiagnosticLevel::Error,
            span,
            message,
        }
    }

    /// Create a warning diagnostic
    pub fn warning(span: Span, message: String) -> Self {
        Diagnostic {
            level: DiagnosticLevel::Warning,
            span,
            message,
        }
    }

    /// Create an info diagnostic
    pub fn info(span: Span, message: String) -> Self {
        Diagnostic {
            level: DiagnosticLevel::Info,
            span,
            message,
        }
    }

    /// Format the diagnostic with source context
    pub fn format(&self, source: &str, line_offsets: &LineOffsets) -> String {
        let start_line = line_offsets.line(self.span.start);
        let end_line = line_offsets.line(self.span.end);
        let start_col = line_offsets.column(self.span.start);
        let end_col = line_offsets.column(self.span.end);

        let level_str = match self.level {
            DiagnosticLevel::Error => "error",
            DiagnosticLevel::Warning => "warning",
            DiagnosticLevel::Info => "info",
        };

        if start_line == end_line {
            format!(
                "{}: {} at line {}, column {}-{}\n{}",
                level_str,
                self.message,
                start_line,
                start_col,
                end_col,
                self.format_source_line(source, line_offsets, start_line, start_col, end_col)
            )
        } else {
            format!(
                "{}: {} at line {}, column {} to line {}, column {}",
                level_str, self.message, start_line, start_col, end_line, end_col
            )
        }
    }

    fn format_source_line(
        &self,
        source: &str,
        line_offsets: &LineOffsets,
        line: usize,
        start_col: usize,
        end_col: usize,
    ) -> String {
        let line_start = line_offsets.line_start(line);
        let line_end = line_offsets.line_end(line);
        let line_text = &source[line_start..line_end];

        let mut result = String::new();
        result.push_str(&format!(" {} | {}\n", line, line_text));
        result.push_str(&format!(" {} | ", " ".repeat(line.to_string().len())));
        result.push_str(&" ".repeat(start_col - 1));
        result.push_str(&"^".repeat((end_col - start_col).max(1)));
        result
    }
}

/// Helper struct to convert BytePos into line and column numbers
pub struct LineOffsets {
    offsets: Vec<u32>,
    len: u32,
}

impl LineOffsets {
    /// Create line offsets from source code
    pub fn new(data: &str) -> Self {
        let mut offsets = vec![0];
        let len = data.len() as u32;

        for (i, val) in data.bytes().enumerate() {
            if val == b'\n' {
                offsets.push((i + 1) as u32);
            }
        }

        Self { offsets, len }
    }

    /// Get the line number (1-based) for a byte position
    pub fn line(&self, pos: BytePos) -> usize {
        let offset = pos.0;

        assert!(offset <= self.len, "Position out of bounds");

        match self.offsets.binary_search(&offset) {
            Ok(line) => line + 1,
            Err(line) => line,
        }
    }

    /// Get the column number (1-based) for a byte position
    pub fn column(&self, pos: BytePos) -> usize {
        let line = self.line(pos);
        let line_start = self.line_start(line);
        (pos.0 as usize - line_start) + 1
    }

    /// Get the byte offset of the start of a line (1-based)
    pub fn line_start(&self, line: usize) -> usize {
        if line == 0 || line > self.offsets.len() {
            0
        } else {
            self.offsets[line - 1] as usize
        }
    }

    /// Get the byte offset of the end of a line (1-based)
    pub fn line_end(&self, line: usize) -> usize {
        if line == 0 || line > self.offsets.len() {
            self.len as usize
        } else if line == self.offsets.len() {
            self.len as usize
        } else {
            (self.offsets[line] - 1) as usize
        }
    }

    /// Get the total number of lines
    pub fn line_count(&self) -> usize {
        self.offsets.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_line_offsets() {
        let source = "abc\ndef\nghi";
        let offsets = LineOffsets::new(source);

        assert_eq!(offsets.line(BytePos(0)), 1);
        assert_eq!(offsets.line(BytePos(1)), 1);
        assert_eq!(offsets.line(BytePos(3)), 1);
        assert_eq!(offsets.line(BytePos(4)), 2);
        assert_eq!(offsets.line(BytePos(7)), 2);
        assert_eq!(offsets.line(BytePos(8)), 3);

        assert_eq!(offsets.column(BytePos(0)), 1);
        assert_eq!(offsets.column(BytePos(1)), 2);
        assert_eq!(offsets.column(BytePos(4)), 1);
        assert_eq!(offsets.column(BytePos(5)), 2);
    }

    #[test]
    fn test_span_union() {
        let span1 = Span::new_unchecked(0, 5);
        let span2 = Span::new_unchecked(3, 10);
        let union = Span::union_span(span1, span2);

        assert_eq!(union.start.0, 0);
        assert_eq!(union.end.0, 10);
    }

    #[test]
    fn test_diagnostic_format() {
        let source = "Page {\n  name: 123\n}";
        let offsets = LineOffsets::new(source);
        let diagnostic = Diagnostic::error(
            Span::new_unchecked(15, 18),
            "Expected string, found number".to_string(),
        );

        let formatted = diagnostic.format(source, &offsets);
        assert!(formatted.contains("error"));
        assert!(formatted.contains("line 2"));
    }
}
