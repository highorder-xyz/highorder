import { parser } from "./parser"
import { continuedIndent, delimitedIndent, indentNodeProp, foldNodeProp, foldInside, LRLanguage, LanguageSupport } from "@codemirror/language"

/// A language provider that provides JSON parsing.
export const holaLanguage = LRLanguage.define({
    name: "hola",
    parser: parser.configure({
        props: [
            indentNodeProp.add({
                "Object": continuedIndent({except: /^\s*\}/}),
                List: continuedIndent({except: /^\s*\]/})
            }),
            foldNodeProp.add({
                "Object List": foldInside
            })
        ]
    }),
    languageData: {
        closeBrackets: { brackets: ["[", "{", '"', "'"] },
        indentOnInput: /^\s*[\}\]]$/
    }
})

/// JSON language support.
export function hola() {
    return new LanguageSupport(holaLanguage)
}