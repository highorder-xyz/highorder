
import { EditorState, Compartment } from "@codemirror/state"
import { defaultKeymap, indentWithTab, history, historyKeymap } from "@codemirror/commands"
import {
    EditorView, keymap, highlightSpecialChars, drawSelection, highlightActiveLine, dropCursor,
    rectangularSelection, crosshairCursor,
    lineNumbers, highlightActiveLineGutter
} from "@codemirror/view"
import {
    defaultHighlightStyle, syntaxHighlighting, indentOnInput, bracketMatching,
    foldGutter, foldKeymap, indentUnit
} from "@codemirror/language"
import { searchKeymap, highlightSelectionMatches } from "@codemirror/search"
import { autocompletion, completionKeymap, closeBrackets, closeBracketsKeymap } from "@codemirror/autocomplete"
import { lintKeymap } from "@codemirror/lint"

import { tomorrow } from './theme';
import { hola } from "./hola"

let language = new Compartment, tabSize = new Compartment

class CodeSyncer {
    constructor(changed_cb) {
        this.changed_cb = changed_cb
        this.code = undefined
        this.watch = undefined
        this.unchanged_times = 0
    }

    start_watch() {
        if (!this.watch) {
            this.watch = setInterval(() => {
                this.sync()
            }, 2000)
            this.unchanged_times = 0
        }
    }

    stop_watch() {
        if (this.watch) {
            clearInterval(this.watch)
            this.watch = undefined
            this.unchanged_times = 0
        }
    }

    code_changed(code) {
        if (!this.changed_cb) {
            return
        }
        if (!this.watch) {
            this.start_watch()
        }
        this.code = code
    }

    sync() {
        console.log('code sync ')
        if (!this.changed_cb || !this.code) {
            this.unchanged_times += 1
            if (this.unchanged_times >= 10) {
                this.stop_watch()
            }
            return
        }
        const code = this.code
        this.code = undefined
        if (this.changed_cb) {
            this.changed_cb(code)
        }
    }
}

export function hola_editor(options) {
    const changed_cb = options["changed_cb"]
    const codesyncer = new CodeSyncer(changed_cb)
    const viewTheme = EditorView.theme({
        "&": {
            fontSize: "14px",
            border: "2px solid #c0c0c0",
            height: "100%",
            width: "100%"
        },
        ".cm-content": {
            fontFamily: "'JetBrains Mono', Menlo, Monaco, Lucida Console, Consolas, monospace",
            minHeight: "300px",
        },
        ".cm-gutters": {
            fontFamily: "'JetBrains Mono', Menlo, Monaco, Lucida Console, Consolas, monospace",
            minHeight: "300px",
            height: "100%"
        },
        ".cm-scroller": {
            overflow: "auto",
            height: "100%"
        }
    }, { dark: false });

    let updateListenerExtension = EditorView.updateListener.of((update) => {
        if (update.docChanged) {
            codesyncer.code_changed(update.view.state.doc.toString())
        }
    });

    let startState = EditorState.create({
        doc: options["code"] ?? "",
        extensions: [
            lineNumbers(),
            highlightActiveLineGutter(),
            highlightSpecialChars(),
            history(),
            foldGutter(),
            dropCursor(),
            EditorState.allowMultipleSelections.of(false),
            indentOnInput(),
            syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
            bracketMatching(),
            closeBrackets(),
            autocompletion(),
            rectangularSelection(),
            crosshairCursor(),
            highlightActiveLine(),
            highlightSelectionMatches(),
            keymap.of([
                ...closeBracketsKeymap,
                ...defaultKeymap,
                ...searchKeymap,
                ...historyKeymap,
                ...foldKeymap,
                ...completionKeymap,
                ...lintKeymap
            ]),
            viewTheme,
            tomorrow,
            language.of(hola()),
            indentUnit.of("    "),
            tabSize.of(EditorState.tabSize.of(4)),
            updateListenerExtension,
            keymap.of([defaultKeymap, indentWithTab])
        ]
    })

    let view = new EditorView({
        state: startState,
        parent: document.getElementById(options["parent_id"])
    })
}
