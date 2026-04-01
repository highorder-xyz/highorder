export const TokenKind = {
  Unknown: 0,
  Text: 1,
  LBracket: 2,
  RBracket: 3,
  Identifier: 4,
  IdentifierClose: 5,
  Equal: 6,
  StringValue: 7,
  NewLine: 8
}

export class Tokenizer {
  tokenize(text) {
    let pos = 0
    const tokens = []
    let context = {
      in_tag: false,
      start_pos: 0,
      chars: []
    }

    while (pos < text.length) {
      const ch = text[pos]

      if (ch === '[') {
        if (context.chars.length > 0) {
          let kind = TokenKind.Text
          if (context.in_tag) {
            kind = TokenKind.Identifier
          }
          tokens.push({
            kind,
            value: context.chars.join(''),
            start_pos: context.start_pos,
            end_pos: pos - 1
          })
          context.start_pos = pos
          context.chars = []
        }

        tokens.push({ kind: TokenKind.LBracket, value: ch, start_pos: pos, end_pos: pos })
        pos += 1
        context.in_tag = true
        context.start_pos = pos
        context.chars = []
        continue
      }

      if (ch === ']') {
        if (context.chars.length > 0) {
          tokens.push({
            kind: TokenKind.Identifier,
            value: context.chars.join(''),
            start_pos: context.start_pos,
            end_pos: pos - 1
          })
          context.start_pos = pos
          context.chars = []
        }
        tokens.push({ kind: TokenKind.RBracket, value: ch, start_pos: pos, end_pos: pos })
        pos += 1
        context.in_tag = false
        context.start_pos = pos
        context.chars = []
        continue
      }

      if (ch === '\n') {
        if (context.in_tag) {
          pos += 1
          continue
        }
        if (context.chars.length > 0) {
          tokens.push({
            kind: TokenKind.Text,
            value: context.chars.join(''),
            start_pos: context.start_pos,
            end_pos: pos - 1
          })
          context.start_pos = pos
          context.chars = []
        }
        tokens.push({ kind: TokenKind.NewLine, value: '\n', start_pos: pos, end_pos: pos })
        pos += 1
        context.start_pos = pos
        context.chars = []
        continue
      }

      if (ch === '\\') {
        const next = text[pos + 1]
        if (!context.in_tag && (next === ']' || next === '[')) {
          context.chars.push(next)
          pos += 2
        } else {
          context.chars.push(ch)
          pos += 1
        }
        continue
      }

      if (ch === '=') {
        if (context.chars.length > 0) {
          tokens.push({
            kind: TokenKind.Identifier,
            value: context.chars.join(''),
            start_pos: context.start_pos,
            end_pos: pos - 1
          })
          context.start_pos = pos
          context.chars = []
        }
        tokens.push({ kind: TokenKind.Equal, value: ch, start_pos: pos, end_pos: pos })
        pos += 1
        context.start_pos = pos
        context.chars = []
        continue
      }

      if (ch === '"') {
        if (context.in_tag) {
          let lead_pos = pos + 1
          while (lead_pos < text.length) {
            const next = text[lead_pos]
            if (next !== '"') {
              context.chars.push(next)
            } else {
              break
            }
            lead_pos += 1
          }
          tokens.push({
            kind: TokenKind.StringValue,
            value: context.chars.join(''),
            start_pos: pos,
            end_pos: lead_pos
          })
          pos = lead_pos + 1
          context.start_pos = pos
          context.chars = []
        } else {
          context.chars.push(ch)
          pos += 1
        }
        continue
      }

      if (ch === '/') {
        if (context.in_tag) {
          let lead_pos = pos + 1
          while (lead_pos < text.length) {
            const next = text[lead_pos]
            if (next === ']') {
              break
            }
            context.chars.push(next)
            lead_pos += 1
          }
          tokens.push({
            kind: TokenKind.IdentifierClose,
            value: context.chars.join(''),
            start_pos: pos,
            end_pos: lead_pos - 1
          })
          pos = lead_pos
          context.start_pos = pos
          context.chars = []
        } else {
          context.chars.push(ch)
          pos += 1
        }
        continue
      }

      if (ch === ' ') {
        if (context.in_tag) {
          if (context.chars.length > 0) {
            tokens.push({
              kind: TokenKind.Identifier,
              value: context.chars.join(''),
              start_pos: context.start_pos,
              end_pos: pos - 1
            })
          }
          pos += 1
          context.start_pos = pos
          context.chars = []
        } else {
          context.chars.push(ch)
          pos += 1
        }
        continue
      }

      context.chars.push(ch)
      pos += 1
    }

    if (context.chars.length > 0) {
      tokens.push({
        kind: TokenKind.Text,
        value: context.chars.join(''),
        start_pos: context.start_pos,
        end_pos: text.length - 1
      })
    }

    return tokens
  }
}

export const NodeKind = {
  Unknown: 0,
  Root: 1,
  Text: 2,
  Tag: 3,
  NewLine: 4
}

export class RichTextParserError extends Error {
  constructor(message) {
    super(message)
  }
}

export class RichTextParser {
  parse(text) {
    const tokens = new Tokenizer().tokenize(text)
    const root = { kind: NodeKind.Root, children: [] }

    let pos = 0
    while (pos < tokens.length) {
      const ret = this.parse_one(tokens, pos, root)
      if (ret.node) {
        root.children.push(ret.node)
      }
      pos += ret.num
    }
    return root
  }

  parse_one(tokens, pos, current) {
    const token = this.get_token(tokens, pos)

    if (token && token.kind === TokenKind.Text) {
      return this.parse_text(tokens, pos)
    }

    if (token && token.kind === TokenKind.LBracket) {
      const retOpen = this.parse_tag_open(tokens, pos)
      if (retOpen.num === 0 || retOpen.node === undefined) {
        const retClose = this.parse_tag_close(tokens, pos)
        return { num: retClose.num, node: undefined }
      }

      const n = retOpen.node
      let num = retOpen.num
      let p = pos + retOpen.num

      while (p < tokens.length) {
        const ret = this.parse_one(tokens, p, n)
        num += ret.num
        p += ret.num
        if (ret.node) {
          n.children.push(ret.node)
        } else {
          break
        }
      }

      const ret_close = this.parse_tag_close(tokens, p)
      if (ret_close.token && ret_close.token.value === n.name) {
        num += ret_close.num
      }

      return { num, node: n }
    }

    if (token && token.kind === TokenKind.NewLine) {
      return {
        num: 1,
        node: {
          kind: NodeKind.NewLine,
          value: token.value,
          position: { start: token.start_pos, end: token.end_pos }
        }
      }
    }

    return { num: 1, node: undefined }
  }

  get_token(tokens, pos) {
    if (pos >= 0 && pos < tokens.length) return tokens[pos]
    return undefined
  }

  parse_text(tokens, pos) {
    const token = this.get_token(tokens, pos)
    if (token && token.kind === TokenKind.Text) {
      return {
        num: 1,
        node: {
          kind: NodeKind.Text,
          value: token.value,
          position: { start: token.start_pos, end: token.end_pos }
        }
      }
    }
    return { num: 0, node: undefined }
  }

  parse_tag_open(tokens, pos) {
    const token = this.get_token(tokens, pos)
    const next = this.get_token(tokens, pos + 1)
    if (!next || !token) return { num: 0, node: undefined }

    if (next.kind === TokenKind.RBracket) {
      return { num: 2, node: undefined }
    }

    if (next.kind === TokenKind.Identifier) {
      const n = {
        kind: NodeKind.Tag,
        name: next.value,
        attributes: {},
        position: { start: token.start_pos, end: next.end_pos },
        children: []
      }
      let num = 2
      let p = pos + num
      while (p < tokens.length) {
        const ret = this.parse_attribute(tokens, p, n, next.value)
        num += ret.num
        p += ret.num
        if (!ret.more) break
      }
      const rb_token = this.get_token(tokens, p)
      if (rb_token && rb_token.kind === TokenKind.RBracket) {
        num += 1
      }
      return { num, node: n }
    }

    if (next.kind === TokenKind.IdentifierClose) {
      return { num: 0, node: undefined }
    }

    return { num: 1, node: undefined }
  }

  parse_tag_close(tokens, pos) {
    const token = this.get_token(tokens, pos)
    const next = this.get_token(tokens, pos + 1)
    if (!token || token.kind !== TokenKind.LBracket) {
      return { num: 0, token: undefined }
    }
    if (next && next.kind === TokenKind.IdentifierClose) {
      const next2 = this.get_token(tokens, pos + 2)
      if (next2 && next2.kind === TokenKind.RBracket) {
        return { num: 3, token: next }
      }
      return { num: 2, token: next }
    }
    return { num: 1, token: undefined }
  }

  parse_attribute(tokens, pos, current, tag_name) {
    const token = this.get_token(tokens, pos)
    if (!token) return { num: 0, more: false }

    if (token.kind === TokenKind.RBracket) {
      return { num: 0, more: false }
    }

    if (token.kind === TokenKind.Identifier) {
      const name_or_value = token.value
      const next = this.get_token(tokens, pos + 1)
      if (next && next.kind === TokenKind.Equal) {
        const next2 = this.get_token(tokens, pos + 2)
        if (next2 && (next2.kind === TokenKind.Identifier || next2.kind === TokenKind.StringValue)) {
          current.attributes[name_or_value] = next2.value
          return { num: 3, more: true }
        }
      }
      return { num: 1, more: true }
    }

    if (token.kind === TokenKind.Equal) {
      const next = this.get_token(tokens, pos + 1)
      if (next && (next.kind === TokenKind.Identifier || next.kind === TokenKind.StringValue)) {
        if (!(tag_name in current.attributes)) {
          current.attributes[tag_name] = next.value
        }
        return { num: 2, more: true }
      }
      return { num: 1, more: true }
    }

    throw new RichTextParserError(`attribute token expected but ${token.kind} find.`)
  }
}

export class RichTextCompiler {
  compile(text) {
    const ast = new RichTextParser().parse(text)
    return this.transform(ast, [])
  }

  transform(root, context_tags) {
    const parts = []

    if (!root.children || root.children.length === 0) {
      return [{ text: '', tags: context_tags }]
    }

    for (const n of root.children) {
      if (n.kind === NodeKind.Tag) {
        const sub_context_tags = [
          ...context_tags,
          { name: n.name, attributes: n.attributes }
        ]
        const sub_parts = this.transform(n, sub_context_tags)
        for (const part of sub_parts) parts.push(part)
      } else if (n.kind === NodeKind.Text) {
        parts.push({ text: n.value, tags: context_tags })
      } else if (n.kind === NodeKind.NewLine) {
        parts.push({ text: n.value, tags: [] })
      }
    }

    return parts
  }
}
