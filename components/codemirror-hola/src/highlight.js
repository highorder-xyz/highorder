import { styleTags, tags as t } from "@lezer/highlight"

export const holaHighlighting = styleTags({
    ObjectName: t.variableName,
    PropertyIdentifier: t.name,
    String: t.string,
    Number: t.number,
    Boolean: t.bool,
    Null: t.null,
    LineComment: t.lineComment,
    ",": t.separator,
    "[ ]": t.squareBracket,
    "{ }": t.brace
})