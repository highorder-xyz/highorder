
export enum TokenKind {
    Unknown,
    Text,
    LBracket,
    RBracket,
    Identifier,
    IdentifierClose,
    Equal,
    StringValue,
    NewLine
}


export interface Token {
    kind: TokenKind,
    value: string
    start_pos: number,
    end_pos: number
}

interface TokenizeContext {
    in_tag: boolean,
    start_pos: number,
    chars: string[]
}

export class Tokenizer {
    tokenize(text: string) {
        let pos = 0;
        const tokens: Token[] = []
        let context: TokenizeContext = {
            in_tag: false,
            start_pos: 0,
            chars: []
        }
        while (pos < text.length) {
            let ch = text[pos]
            if (ch == '[') {
                if (context.chars.length > 0) {
                    let kind = TokenKind.Text
                    if (context.in_tag) {
                        kind = TokenKind.Identifier
                    }
                    tokens.push({
                        kind: kind,
                        value: context.chars.join(""),
                        start_pos: context.start_pos,
                        end_pos: pos - 1
                    })
                    context.start_pos = pos
                    context.chars = []
                }

                tokens.push({
                    kind: TokenKind.LBracket,
                    value: ch,
                    start_pos: pos,
                    end_pos: pos
                })
                pos += 1
                context.in_tag = true
                context.start_pos = pos
                context.chars = []
                continue
            } else if (ch == ']') {
                if (context.chars.length > 0) {
                    tokens.push({
                        kind: TokenKind.Identifier,
                        value: context.chars.join(""),
                        start_pos: context.start_pos,
                        end_pos: pos - 1
                    })
                    context.start_pos = pos
                    context.chars = []
                }
                tokens.push({
                    kind: TokenKind.RBracket,
                    value: ch,
                    start_pos: pos,
                    end_pos: pos
                })
                pos += 1
                context.in_tag = false
                context.start_pos = pos
                context.chars = []
                continue
            } else if (ch == '\n') {
                if (context.in_tag){
                    pos += 1
                    continue
                }
                if (context.chars.length > 0) {
                    tokens.push({
                        kind: TokenKind.Text,
                        value: context.chars.join(""),
                        start_pos: context.start_pos,
                        end_pos: pos - 1
                    })
                    context.start_pos = pos
                    context.chars = []
                }
                tokens.push({
                    kind: TokenKind.NewLine,
                    value: ch,
                    start_pos: pos,
                    end_pos: pos
                })
                pos += 1
                context.start_pos = pos
                context.chars = []
                continue
            } else if (ch == '\\') {
                let next = text[pos + 1]
                if (!context.in_tag && (next == ']' || next == '[')) {
                    context.chars.push(next)
                    pos += 2
                } else {
                    context.chars.push(ch)
                    pos += 1
                }
                continue
            } else if (ch == '=') {
                if (context.chars.length > 0) {
                    tokens.push({
                        kind: TokenKind.Identifier,
                        value: context.chars.join(""),
                        start_pos: context.start_pos,
                        end_pos: pos - 1
                    })
                    context.start_pos = pos
                    context.chars = []
                }
                tokens.push({
                    kind: TokenKind.Equal,
                    value: ch,
                    start_pos: pos,
                    end_pos: pos
                })
                pos += 1
                context.start_pos = pos
                context.chars = []
                continue
            } else if (ch == '"') {
                if (context.in_tag) {
                    let lead_pos = pos + 1
                    while (lead_pos < text.length) {
                        let next = text[lead_pos]
                        if (next != '"') {
                            context.chars.push(next)
                        } else {
                            break
                        }
                        lead_pos += 1
                    }
                    tokens.push({
                        kind: TokenKind.StringValue,
                        value: context.chars.join(""),
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
            } else if (ch == '/') {
                if (context.in_tag) {
                    let lead_pos = pos + 1
                    while (lead_pos < text.length) {
                        let next = text[lead_pos]
                        if (next == "]") {
                            break
                        } else {
                            context.chars.push(next)
                        }
                        lead_pos += 1
                    }
                    tokens.push({
                        kind: TokenKind.IdentifierClose,
                        value: context.chars.join(""),
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
            } else if (ch == ' ') {
                if (context.in_tag) {
                    if (context.chars.length > 0) {
                        tokens.push({
                            kind: TokenKind.Identifier,
                            value: context.chars.join(""),
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
            } else {
                context.chars.push(ch)
                pos += 1
                continue
            }
        }
        if (context.chars.length > 0) {
            tokens.push({
                kind: TokenKind.Text,
                value: context.chars.join(""),
                start_pos: context.start_pos,
                end_pos: text.length - 1
            })
        }
        return tokens
    }
}

export enum NodeKind {
    Unknown,
    Root,
    Text,
    Tag,
    NewLine
}

interface RichRootNode {
    kind: NodeKind,
    children: RichNode[]
}

interface NodePosition {
    start: number,
    end: number
}

interface RichTagNode {
    kind: NodeKind,
    name: string,
    attributes: Record<string, string>
    children: RichNode[]
    position: NodePosition
}


interface RichTextNode {
    kind: NodeKind,
    value: string,
    position: NodePosition
}

interface RichNewLineNode {
    kind: NodeKind,
    value: string,
    position: NodePosition
}

type RichNode = RichTagNode | RichTextNode | RichNewLineNode

export interface RichTextTag {
    name: string,
    attributes: Record<string, string>
}

export interface RichTextPart {
    text: string,
    tags: RichTextTag[]
}

export class RichTextParserError extends Error {
    constructor(message: string) {
        super(message);
    }
}

export class RichTextParser {
    parse(text: string) {
        const tokens = new Tokenizer().tokenize(text)
        const root: RichRootNode = {
            kind: NodeKind.Root,
            children: []
        }
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

    parse_one(tokens: Token[], pos: number, current: RichRootNode | RichTagNode) {
        const token = this.get_token(tokens, pos)

        if (token && token.kind == TokenKind.Text) {
            return this.parse_text(tokens, pos, current)
        } else if (token && token.kind == TokenKind.LBracket) {
            let ret = this.parse_tag_open(tokens, pos, current)
            if (ret.num == 0 || ret.node === undefined){
                // return num must be greater than 0
                const ret = this.parse_tag_close(tokens, pos, current)
                return {num: ret.num, node:undefined}
            }
            let n = ret.node
            if(n == undefined){
                throw new RichTextParserError("parse tag must return a valid node.")
            }
            let num = ret.num
            let p = pos + ret.num
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

            const ret_close = this.parse_tag_close(tokens, p, n)

            if(ret_close.token && ret_close.token.value == n.name){
                num += ret_close.num
            }

            return {num: num, node: n}
        } else if (token && token.kind == TokenKind.NewLine) {
            return {num: 1, node: {
                kind: NodeKind.NewLine,
                value: token.value,
                position: {
                    start: token.start_pos,
                    end: token.end_pos
                }
            }}
        } else {
            return { num: 1, node: undefined }
        }
    }

    get_token(tokens: Token[], pos: number) {
        if (pos >= 0 && pos < tokens.length) {
            return tokens[pos]
        }
        return undefined
    }


    parse_text(tokens: Token[], pos: number, current: RichRootNode | RichTagNode) {
        const token = this.get_token(tokens, pos)
        if (token && token.kind == TokenKind.Text) {
            const n = {
                kind: NodeKind.Text,
                value: token.value,
                position: {
                    start: token.start_pos,
                    end: token.end_pos
                }
            }
            return { num: 1, node: n }
        } else {
            return { num: 0, node: undefined }
        }
    }

    parse_tag_open(tokens: Token[], pos: number, current: RichRootNode | RichTagNode) {
        const token = this.get_token(tokens, pos)
        const next = this.get_token(tokens, pos + 1)
        if (!next || !token) {
            return { num: 0, node: undefined }
        }
        if (next.kind == TokenKind.RBracket) {
            return { num: 2, node: undefined}
        } else if (next.kind == TokenKind.Identifier) {
            const n = {
                kind: NodeKind.Tag,
                name: next.value,
                attributes: {},
                position: { start: token!.start_pos, end: next.end_pos },
                children: ([] as RichNode[])
            }
            let num = 2
            let p = pos + num
            while (p < tokens.length) {
                const ret = this.parse_attribute(tokens, p, n, next.value)
                num += ret.num
                p += ret.num
                if (!ret.more) {
                    break
                }
            }
            const rb_token = this.get_token(tokens, p)
            if(rb_token && rb_token.kind == TokenKind.RBracket){
                num += 1
            }
            return { num: num, node: n }
        } else if (next.kind == TokenKind.IdentifierClose) {
            return { num: 0, node: undefined}
        } else {
            return { num: 1, node: undefined }
        }
    }

    parse_tag_close(tokens: Token[], pos: number, current: RichTagNode | RichRootNode) {
        const token = this.get_token(tokens, pos)
        const next = this.get_token(tokens, pos+1)
        if(!token || token.kind != TokenKind.LBracket){
            return {num: 0, token: undefined}
        }
        if(next && next.kind == TokenKind.IdentifierClose){
            const next2 = this.get_token(tokens, pos+2)
            if(next2 && next2.kind == TokenKind.RBracket){
                return {num: 3, token: next}
            }
            return {num: 2, token: next}
        }
        return {num: 1, token: undefined}
    }

    parse_attribute(tokens: Token[], pos: number, current: RichTagNode, tag_name:string) {
        const token = this.get_token(tokens, pos)
        if (!token) {
            return { num: 0, more: false }
        }
        if (token.kind == TokenKind.RBracket) {
            return { num: 0, more: false }
        } else if (token.kind == TokenKind.Identifier) {
            const name_or_value = token.value
            const next = this.get_token(tokens, pos+1)
            if(next && next.kind == TokenKind.Equal){
                const next2_token = this.get_token(tokens, pos+2)
                if(next2_token && (next2_token.kind == TokenKind.Identifier || next2_token.kind == TokenKind.StringValue)){
                    current.attributes[name_or_value] = next2_token.value
                    return {num: 3, more: true}
                }
            }
            return {num: 1, more:true}
        } else if (token.kind == TokenKind.Equal) {
            const next = this.get_token(tokens, pos+1)
            if(next && (next.kind == TokenKind.Identifier || next.kind == TokenKind.StringValue)){
                if(!(tag_name in current.attributes)){
                    current.attributes[tag_name] = next.value
                }

                return {num: 2, more: true}
            }
            return {num: 1, more:true}
        } else {
            console.log(token.kind, token.value, token.start_pos)
            throw new RichTextParserError(`attribute token expected but ${token.kind} find.`)
        }
    }
}

export class RichTextCompiler {
    compile(text: string) {
        const ast = new RichTextParser().parse(text)
        return this.transform(ast, [])
    }

    transform(root: RichRootNode | RichTagNode, context_tags: RichTextTag[]) {
        const parts: RichTextPart[] = []
        if(root.children.length === 0){
            return [{
                text: "",
                tags: context_tags
            }]
        }
        for(const n of root.children){
            if(n.kind == NodeKind.Tag){
                const sub_context_tags = [...context_tags, {
                    name: (n as RichTagNode).name,
                    attributes: (n as RichTagNode).attributes
                }]
                const sub_parts = this.transform(n as RichTagNode, sub_context_tags)
                for(const part of sub_parts){
                    parts.push(part)
                }
            } else if (n.kind == NodeKind.Text){
                parts.push({
                    text: (n as RichTextNode).value,
                    tags: context_tags
                })
            } else if (n.kind == NodeKind.NewLine){
                parts.push({
                    text: (n as RichNewLineNode).value,
                    tags: []
                })
            }
        }
        return parts
    }
}