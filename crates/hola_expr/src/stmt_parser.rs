use super::ast::*;
use super::token::*;
use crate::common::*;
use crate::parser::Parser;
use crate::position::Span;
use crate::position::WithSpan;

fn parse_program(it: &mut Parser) -> Result<Vec<WithSpan<Stmt>>, ()> {
    let mut statements = Vec::new();
    while !it.is_eof() {
        statements.push(parse_declaration(it)?);
    }

    Ok(statements)
}

fn parse_declaration(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    match it.peek() {
        TokenKind::Var => parse_var_declaration(it),
        TokenKind::Function => parse_function_declaration(it),
        _ => parse_statement(it),
    }
}

fn parse_statement(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    match it.peek() {
        TokenKind::Print => parse_print_statement(it),
        TokenKind::If => parse_if_statement(it),
        TokenKind::LeftBrace => parse_block_statement(it),
        TokenKind::While => parse_while_statement(it),
        TokenKind::Return => parse_return_statement(it),
        TokenKind::For => parse_for_statement(it),
        TokenKind::Import => parse_import_statement(it),
        _ => parse_expr_statement(it),
    }
}

fn parse_function_declaration(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    let begin_span = it.expect(TokenKind::Function)?;
    let function = parse_function(it)?;

    let span = Span::union(begin_span, &function);
    Ok(WithSpan::new(function.value, span))
}

fn parse_function(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    let name = expect_identifier(it)?;
    it.expect(TokenKind::LeftParen)?;
    let params = if !it.check(TokenKind::RightParen) {
        parse_params(it)?
    } else {
        Vec::new()
    };
    it.expect(TokenKind::RightParen)?;
    it.expect(TokenKind::LeftBrace)?;
    let mut body: Vec<WithSpan<Stmt>> = Vec::new();
    while !it.check(TokenKind::RightBrace) {
        body.push(parse_declaration(it)?);
    }
    let end_span = it.expect(TokenKind::RightBrace)?;
    Ok(WithSpan::new(Stmt::Function(name.clone(), params, body), Span::union(&name, end_span)))
}

fn parse_params(it: &mut Parser) -> Result<Vec<WithSpan<Identifier>>, ()> {
    let mut params: Vec<WithSpan<Identifier>> = Vec::new();
    params.push(expect_identifier(it)?);
    while it.check(TokenKind::Comma) {
        it.expect(TokenKind::Comma)?;
        params.push(expect_identifier(it)?);
    }
    Ok(params)
}

fn parse_var_declaration(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    let begin_span = it.expect(TokenKind::Var)?;
    let name = expect_identifier(it)?;
    let mut initializer = None;

    if it.optionally(TokenKind::Equal)? {
        initializer = Some(parse_expr(it)?);
    }

    let end_span = it.expect(TokenKind::Semicolon)?;

    Ok(WithSpan::new(Stmt::Var(name, initializer.map(Box::new)), Span::union(begin_span, end_span)))
}

fn parse_expr(it: &mut Parser) -> Result<WithSpan<Expr>, ()> {
    super::expr_parser::parse(it)
}

fn parse_for_statement(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    it.expect(TokenKind::For)?;
    it.expect(TokenKind::LeftParen)?;
    let initializer = match it.peek() {
        TokenKind::Var => Some(parse_var_declaration(it)?),
        TokenKind::Semicolon => {
            it.expect(TokenKind::Semicolon)?;
            None
        }
        _ => Some(parse_expr_statement(it)?),
    };
    let condition = if !it.check(TokenKind::Semicolon) {
        parse_expr(it)?
    } else {
        WithSpan::empty(Expr::Boolean(true))
    };
    it.expect(TokenKind::Semicolon)?;
    let increment = if !it.check(TokenKind::RightParen) {
        Some(parse_expr(it)?)
    } else {
        None
    };
    it.expect(TokenKind::RightParen)?;
    let body = parse_statement(it)?;

    // Add increment if it exists
    let body = match increment {
        Some(expr) => {
            let span = expr.span;
            WithSpan::new(Stmt::Block(vec![body, WithSpan::new(Stmt::Expression(Box::new(expr)), span)]), span)
        },
        None => body,
    };
    let span = Span::union(&condition, &body);
    let body = WithSpan::new(Stmt::While(Box::new(condition), Box::new(body)), span);
    let body = match initializer {
        Some(stmt) => {
            let span = Span::union( &stmt, &body);
            WithSpan::new(Stmt::Block(vec![stmt, body]), span)
        },
        None => body,
    };

    Ok(body)
}

fn parse_import_statement(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    let begin_span = it.expect(TokenKind::Import)?;
    let name = expect_string(it)?;
    let params = if it.check(TokenKind::For) {
        it.expect(TokenKind::For)?;
        Some(parse_params(it)?)
    } else {
        None
    };
    let end_span = it.expect(TokenKind::Semicolon)?;

    Ok(WithSpan::new(Stmt::Import(name, params), Span::union(begin_span, end_span)))
}

fn parse_return_statement(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    let begin_span = it.expect(TokenKind::Return)?;
    let mut expr = None;
    if !it.check(TokenKind::Semicolon) {
        expr = Some(parse_expr(it)?);
    }
    let end_span = it.expect(TokenKind::Semicolon)?;
    Ok(WithSpan::new(Stmt::Return(expr.map(Box::new)), Span::union(begin_span, end_span)))
}

fn parse_expr_statement(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    let expr = parse_expr(it)?;
    let end_span = it.expect(TokenKind::Semicolon)?;

    let span = Span::union(&expr, end_span);
    Ok(WithSpan::new(Stmt::Expression(Box::new(expr)), span))
}

fn parse_block_statement(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    let begin_span = it.expect(TokenKind::LeftBrace)?;
    let mut statements: Vec<WithSpan<Stmt>> = Vec::new();
    while !it.check(TokenKind::RightBrace) {
        statements.push(parse_declaration(it)?);
    }
    let end_span = it.expect(TokenKind::RightBrace)?;
    Ok(WithSpan::new(Stmt::Block(statements), Span::union(begin_span, end_span)))
}

fn parse_while_statement(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
   let begin_span =  it.expect(TokenKind::While)?;
    it.expect(TokenKind::LeftParen)?;
    let condition = parse_expr(it)?;
    it.expect(TokenKind::RightParen)?;
    let statement = parse_statement(it)?;
    let span = Span::union(begin_span, &statement);
    Ok(WithSpan::new(Stmt::While(Box::new(condition), Box::new(statement)), span))
}

fn parse_if_statement(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    let begin_token = it.expect(TokenKind::If)?;
    it.expect(TokenKind::LeftParen)?;
    let condition = parse_expr(it)?;
    it.expect(TokenKind::RightParen)?;
    let if_stmt = parse_statement(it)?;
    let mut end_span = if_stmt.span;
    let mut else_stmt: Option<WithSpan<Stmt>> = None;

    if it.optionally(TokenKind::Else)? {
        let stmt = parse_statement(it)?;
        end_span = stmt.span;
        else_stmt = Some(stmt);
    }

    Ok(WithSpan::new(Stmt::If(
        Box::new(condition),
        Box::new(if_stmt),
        else_stmt.map(Box::new),
    ), Span::union_span(begin_token.span, end_span)))
}

fn parse_print_statement(it: &mut Parser) -> Result<WithSpan<Stmt>, ()> {
    let begin_token = it.expect(TokenKind::Print)?;
    let expr = parse_expr(it)?;
    let end_token = it.expect(TokenKind::Semicolon)?;
    Ok( WithSpan::new(Stmt::Print(Box::new(expr)), Span::union(begin_token, end_token)) )
}

pub fn parse(it: &mut Parser) -> Result<Vec<WithSpan<Stmt>>, ()> {
    parse_program(it)
}

#[cfg(test)]
mod tests {
    use std::ops::Range;

    use crate::position::Diagnostic;

    use super::super::tokenizer::*;
    use super::*;
    fn parse_str(data: &str) -> Result<Vec<WithSpan<Stmt>>, Vec<Diagnostic>> {
        let tokens = tokenize_with_context(data);
        let mut parser = crate::parser::Parser::new(&tokens);
        match parse(&mut parser) {
            Ok(ast) => Ok(ast),
            Err(_) => Err(parser.diagnostics().to_vec()),
        }
    }

    pub fn ws<T>(value: T, range: Range<u32>) -> WithSpan<T> {
        WithSpan::new_unchecked(value, range.start, range.end)
    }

    fn assert_errs(data: &str, errs: &[&str]) {
        let x = parse_str(data);
        assert!(x.is_err());
        let diagnostics = x.unwrap_err();
        for diag in diagnostics {
            assert!(errs.contains(&&diag.message.as_str()), "{}", diag.message);
        }
    }

    #[test]
    fn test_expr_stmt() {
        assert_eq!(
            parse_str("null;"),
            Ok(vec![
                ws(Stmt::Expression(Box::new(ws(Expr::Null, 0..4))), 0..5)
            ])
        );
        assert_eq!(
            parse_str("null;null;"),
            Ok(vec![
                ws(Stmt::Expression(Box::new(ws(Expr::Null, 0..4))), 0..5),
                ws(Stmt::Expression(Box::new(ws(Expr::Null, 5..9))), 5..10),
            ])
        );
    }

    #[test]
    fn test_print_stmt() {
        assert_eq!(
            parse_str("print null;"),
            Ok(vec![
                ws(Stmt::Print(Box::new(ws(Expr::Null, 6..10))), 0..11),
            ])
        );
    }

    fn make_span_string(string: &str, offset: u32) -> WithSpan<String> {
        WithSpan::new_unchecked(string.into(), offset, offset+string.len() as u32)
    }

    #[test]
    fn test_var_decl() {
        assert_eq!(
            parse_str("var beverage;"),
            Ok(vec![
                ws(Stmt::Var(make_span_string("beverage", 4), None), 0..13),
            ])
        );
        assert_eq!(
            parse_str("var beverage = null;"),
            Ok(vec![
                ws(Stmt::Var(
                    make_span_string("beverage", 4),
                    Some(Box::new(ws(Expr::Null, 15..19)))
                ), 0..20),
            ])
        );

        assert_eq!(
            parse_str("var beverage = x = null;"),
            Ok(vec![
                ws(Stmt::Var(
                    make_span_string("beverage", 4),
                    Some(Box::new(ws(Expr::Assign(
                        WithSpan::new_unchecked("x".into(), 15, 16),
                        Box::new(ws(Expr::Null, 19..23))
                    ), 15..23)))
                ), 0..24),
            ])
        );

        assert_errs("if (null) var beverage = null;", &["Unexpected 'var'"]);
    }

    #[test]
    fn test_if_stmt() {
        assert_eq!(
            parse_str("if(null) print null;"),
            Ok(vec![
                ws(Stmt::If(
                    Box::new(ws(Expr::Null, 3..7)),
                    Box::new(ws(Stmt::Print(Box::new(ws(Expr::Null, 15..19))), 9..20)),
                    None,
                ), 0..20),
            ])
        );
        assert_eq!(
            parse_str("if(null) print null; else print false;"),
            Ok(vec![
                ws(Stmt::If(
                    Box::new(ws(Expr::Null, 3..7)),
                    Box::new(ws(Stmt::Print(Box::new(ws(Expr::Null, 15..19))), 9..20)),
                    Some(Box::new(
                        ws(Stmt::Print(Box::new(ws(Expr::Boolean(false), 32..37))), 26..38),
                    )),
                ), 0..38),
            ])
        );
    }

    #[test]
    fn test_block_stmt() {
        assert_eq!(parse_str("{}"), Ok(vec![
            ws(Stmt::Block(vec![]), 0..2),
        ]));
        assert_eq!(
            parse_str("{null;}"),
            Ok(vec![
                ws(Stmt::Block(vec![
                    ws(Stmt::Expression(Box::new(
                        ws(Expr::Null, 1..5)
                    )), 1..6),
                ]), 0..7),
            ])
        );
        assert_eq!(
            parse_str("{null;null;}"),
            Ok(vec![
                ws(Stmt::Block(vec![
                    ws(Stmt::Expression(Box::new(ws(Expr::Null, 1..5))), 1..6),
                    ws(Stmt::Expression(Box::new(ws(Expr::Null, 6..10))), 6..11),
                ]), 0..12),
            ])
        );
    }

    #[test]
    fn test_while_stmt() {
        assert_eq!(
            parse_str("while(null)false;"),
            Ok(vec![
                ws(Stmt::While(
                    Box::new(ws(Expr::Null, 6..10)),
                    Box::new(ws(Stmt::Expression(Box::new(ws(Expr::Boolean(false), 11..16))), 11..17)),
                ), 0..17),
            ])
        );
    }

    #[test]
    fn test_return_stmt() {
        assert_eq!(parse_str("return;"), Ok(vec![
            ws(Stmt::Return(None), 0..7),
        ]));
        assert_eq!(
            parse_str("return null;"),
            Ok(vec![
                ws(Stmt::Return(Some(Box::new(ws(Expr::Null, 7..11)))), 0..12),
            ])
        );
    }

    #[test]
    fn test_import_stmt() {
        assert_eq!(parse_str("import \"mymodule\";"), Ok(vec![
            ws(Stmt::Import(
                ws("mymodule".into(), 7..17),
                None
            ), 0..18),
        ]));

        assert_eq!(parse_str("import \"mymodule\" for message;"), Ok(vec![
            ws(Stmt::Import(
                ws("mymodule".into(), 7..17),
                Some(vec![
                    ws("message".into(), 22..29),
                ])
            ), 0..30),
        ]));
    }

    #[test]
    fn test_function_stmt() {
        assert_eq!(
            parse_str("function test(){}"),
            Ok(vec![
                ws(Stmt::Function(
                    WithSpan::new_unchecked("test".into(), 9, 13),
                    vec![],
                    vec![]
                ), 0..17),
            ])
        );
        assert_eq!(
            parse_str("function test(a){}"),
            Ok(vec![
                ws(Stmt::Function(
                    WithSpan::new_unchecked("test".into(), 9, 13),
                    vec![WithSpan::new_unchecked("a".into(), 14, 15)],
                    vec![]
                ), 0..18),
            ])
        );
        assert_eq!(
            parse_str("function test(){null;}"),
            Ok(vec![
                ws(Stmt::Function(
                    WithSpan::new_unchecked("test".into(), 9, 13),
                    vec![],
                    vec![ws(Stmt::Expression(Box::new(ws(Expr::Null, 16..20))), 16..21),]
                ), 0..22),
            ])
        );
    }

    #[test]
    fn test_for() {
        fn block(what: Vec<WithSpan<Stmt>>, r: Range<u32>) -> WithSpan<Stmt> {
            ws(Stmt::Block(what), r)
        }
        fn var_i_zero(start: u32, r: Range<u32>) -> WithSpan<Stmt> {
            ws(Stmt::Var(make_span_string("i", 8), Some(Box::new(ws(Expr::Number(0.), start..start+1)))), r)
        }
        fn null() -> Expr {
            Expr::Null
        }
        fn while_stmt(e: WithSpan<Expr>, s: WithSpan<Stmt>, r: Range<u32>) -> WithSpan<Stmt> {
            ws(Stmt::While(Box::new(e), Box::new(s)), r)
        }

        assert_eq!(
            parse_str("for(;;){}"),
            Ok(vec![
                while_stmt(ws(Expr::Boolean(true), 0..0), ws(Stmt::Block(vec![]), 7..9), 0..9),
            ])
        );
        assert_eq!(
            parse_str("for(var i=0;;){}"),
            Ok(vec![block(vec![
                var_i_zero(10, 4..12),
                while_stmt(ws(Expr::Boolean(true), 0..0), ws(Stmt::Block(vec![]), 14..16), 0..16),
            ], 0..16)])
        );
        assert_eq!(
            parse_str("for(null;null;null){}"),
            Ok(vec![block(vec![
                ws(Stmt::Expression(Box::new(ws(null(), 4..8))), 4..9),
                while_stmt(
                    ws(Expr::Null, 9..13),
                    ws(Stmt::Block(vec![ws(Stmt::Block(vec![]), 19..21), ws(Stmt::Expression(Box::new(ws(null(), 14..18))), 14..18), ]), 14..18),
                    9..18,
                ),
            ], 4..18)])
        );
    }
}