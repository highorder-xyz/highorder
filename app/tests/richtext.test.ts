import { NodeKind, RichTextCompiler, RichTextParser, Tokenizer, TokenKind } from '../src/common/richtext'

test("Tokenizer simple tokenize", () => {
    const t = new Tokenizer()
    const tokens = t.tokenize("ni hao [b]a[/b].")
    // console.log(tokens)
    expect(tokens[0].kind).toEqual(TokenKind.Text);
    expect(tokens[0].value).toEqual('ni hao ')
});

test("Tokenizer simple tokenize2", () => {
    const t = new Tokenizer()
    const tokens = t.tokenize("ni hao [bo=test]ala bo \n sss.[/bo].")
    // console.log(tokens)
    expect(tokens[0].kind).toEqual(TokenKind.Text);
    expect(tokens[0].value).toEqual('ni hao ')
});


test("Tokenizer simple tokenize3", () => {
    const t = new Tokenizer()
    const tokens = t.tokenize("ni hao [bo foo=test]ala bo \n sss.[/bo].")
    // console.log(tokens)
    expect(tokens[0].kind).toEqual(TokenKind.Text);
    expect(tokens[0].value).toEqual('ni hao ')
});

test("Tokenizer simple tokenize4", () => {
    const t = new Tokenizer()
    const tokens = t.tokenize("ni hao [bo foo=foo bar=\"test2\"]ala bo \n sss.[/bo].")
    // console.log(tokens)
    expect(tokens[0].kind).toEqual(TokenKind.Text);
    expect(tokens[0].value).toEqual('ni hao ')
});


test("Tokenizer simple tokenize text contain bracket", () => {
    const t = new Tokenizer()
    const tokens = t.tokenize("unmatched \\[tag\\][b]a\\[a\\][/b]text end.")
    console.log(tokens)
    expect(tokens[0].kind).toEqual(TokenKind.Text);
    expect(tokens[0].value).toEqual('unmatched [tag]')
});

test("Tokenizer simple tokenize5", () => {
    const t = new Tokenizer()
    const tokens = t.tokenize("text before[ao foo=foo bar=\"test2\"]ala [bo bo=boo]bo[/bo] \n sss.[/ao]end.")
    // console.log(tokens)
    expect(tokens[0].kind).toEqual(TokenKind.Text);
    expect(tokens[0].value).toEqual('text before')
});



test("Parser simple parse", () => {
    const p = new RichTextParser()
    const root = p.parse("ni hao [b]a[/b].")
    // console.log(root.children)
    // console.log(root.children[1])
    expect(root.kind).toEqual(NodeKind.Root);
    expect(root.children.length).toEqual(3);
});

test("Parser simple parse error", () => {
    const p = new RichTextParser()
    const root = p.parse("unmatched tag[b]a[/c]text end.")
    console.log(root.children)
    console.log((root.children[1] as any).children)
    expect(root.kind).toEqual(NodeKind.Root);
    expect(root.children.length).toEqual(3);
    const btag = root.children[1] as any
    expect((btag.children[0] as any).value ).toEqual("a")
});


test("Parser simple parse text contain bracket", () => {
    const p = new RichTextParser()
    const root = p.parse("unmatched \\[tag\\][b]a\\[a\\][/b]text end.")
    console.log(root.children)
    console.log((root.children[1] as any).children)
    expect(root.kind).toEqual(NodeKind.Root);
    expect(root.children.length).toEqual(3);
    expect((root.children[0] as any).value).toEqual("unmatched [tag]")
    const btag = root.children[1] as any
    expect((btag.children[0] as any).value ).toEqual("a[a]")
});


test("Parser simple parse2", () => {
    const p = new RichTextParser()
    const root = p.parse("ni hao [bo=test]ala bo \n sss.[/bo].")
    // console.log(root.children)
    // console.log(root.children[1])
    expect(root.kind).toEqual(NodeKind.Root);
    expect(root.children.length).toEqual(3);
    expect((root.children[1] as any).name).toEqual('bo');
    expect((root.children[1] as any).attributes['bo']).toEqual('test');
    // console.log((root.children[1] as any).children[0])
    expect((root.children[1] as any).children.length).toEqual(3);
});


test("Parser simple parse3", () => {
    const p = new RichTextParser()
    const root = p.parse("ni hao [bo foo=test bar=bar ccd=\"hello\"]ala bo \n sss.[/bo].")
    // console.log(root.children)
    // console.log(root.children[1])
    expect(root.kind).toEqual(NodeKind.Root);
    expect(root.children.length).toEqual(3);
    expect((root.children[1] as any).name).toEqual('bo');
    expect((root.children[1] as any).attributes['foo']).toEqual('test');
    expect((root.children[1] as any).attributes['bar']).toEqual('bar');
    expect((root.children[1] as any).attributes['ccd']).toEqual('hello');
    // console.log((root.children[1] as any).children[0])
    expect((root.children[1] as any).children.length).toEqual(3);
});

test("Parser simple parse4", () => {
    const p = new RichTextParser()
    const root = p.parse("text before[ao foo=foo bar=\"test2\"]before bo tag[bo fo=boo]bo[/bo]end of bo[/ao]end.")
    expect(root.kind).toEqual(NodeKind.Root);
    expect(root.children.length).toEqual(3);
    expect((root.children[1] as any).name).toEqual('ao');
    expect((root.children[1] as any).attributes['foo']).toEqual('foo');
    expect((root.children[1] as any).attributes['bar']).toEqual('test2');
    expect((root.children[1] as any).children.length).toEqual(3);
    let botag = (root.children[1] as any).children[1]
    expect((root.children[1] as any).children[0].value).toEqual('before bo tag')
    expect((botag as any).name).toEqual('bo');
    expect((botag as any).attributes['fo']).toEqual('boo');
    expect((root.children[1] as any).children[2].value).toEqual('end of bo')
});


test("Parser parse icon", () => {
    const p = new RichTextParser()
    const root = p.parse("开始(-1[icon src=\"http://www.example.com/main/energy-512.png\"][/icon])")
    expect(root.kind).toEqual(NodeKind.Root);
    expect(root.children.length).toEqual(3);
    expect((root.children[1] as any).name).toEqual('icon');
    expect((root.children[1] as any).attributes['src']).toEqual('http://www.example.com/main/energy-512.png');
});

test("Compiler simple compile", () => {
    const c = new RichTextCompiler()
    const parts = c.compile("ni hao [b]a[/b].")
    // console.log(parts)
    expect(parts.length).toEqual(3);
    // console.log(parts[1].tags)
    expect(parts[1].tags.length).toEqual(1);
    expect(parts[1].tags[0].name).toEqual('b');
});

test("Compiler icon", () => {
    const c = new RichTextCompiler()
    const parts = c.compile("开始(-1[icon src=\"http://www.example.com/main/energy-512.png\"][/icon])")
    // console.log(parts)
    expect(parts.length).toEqual(3);
    // console.log(parts[1].tags)
    expect(parts[1].tags.length).toEqual(1);
    expect(parts[1].tags[0].name).toEqual('icon');
    expect(parts[1].tags[0].attributes.src).toEqual('http://www.example.com/main/energy-512.png');
});
