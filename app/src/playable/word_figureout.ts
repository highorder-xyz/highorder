import { h, defineComponent, VNode, PropType } from 'vue';
import { ApplyResponse, ConditionResponse, LevelInfo, PlayableResult } from './defines';
import styles from './word_figureout.module.css'


export interface ChengYuDetail {
    derivation: string,
    example: string,
    explanation: string,
    pinyin: string,
    word: string,
    abbreviation: string
}

export interface WordFigureOutSceneConfig {
    idiom: string,
    keys: string[],
    pinyin: { [letter: string]: string | string[] }
    detail: {
        derivation: string,
        example: string,
        explanation: string,
        pinyin: string,
        word: string,
        abbreviation: string
    }

}

function getPinyinOne(letter: string, pinyindb: object): string | undefined {
    let letterPinyin = undefined
    for (const [key, value] of Object.entries(pinyindb)) {
        if (letter === key) {
            letterPinyin = value
        } else if (key.includes(letter)) {
            const idx = key.indexOf(letter)
            return (value as string[])[idx]
        }
    }
    return letterPinyin
}

function getIdiomPinyin(idiom: string, pinyindb: object): string[] | undefined {
    for (const [key, value] of Object.entries(pinyindb)) {
        if (key.startsWith(idiom)) {
            return (value as string[]).slice(0, idiom.length)
        }
    }
    return undefined
}


export const enum LetterState {
    INITIAL = 'initial',
    CORRECT = 'correct',
    PRESENT = 'present',
    ABSENT = 'absent',
    DISABLED = 'disabled'
}

interface Letter {
    letter: string,
    pinyin?: string,
    state: LetterState,
    canDelete: boolean
}

export const Tile = defineComponent({
    name: 'LetterTile',
    props: {
        letter: { type: Object as PropType<Letter>, required: true },
        current: { type: Boolean, default: false }
    },
    setup(props) {
        return () => {
            const tileClass = [styles["letter"], props.letter.letter ? styles["lettered"] : "",
            props.letter.state === LetterState.INITIAL ? styles['initial'] : styles[props.letter.state],
            props.letter.state === LetterState.INITIAL ? '' : styles['letter-anim'],
            props.current ? styles["current_tile"] : ''
            ]
            const rubyClass = [props.letter.state === LetterState.INITIAL ? '' : styles["letter_flip_back"]]
            return h('div', { "class": tileClass },
                h('ruby', { "class": rubyClass }, [
                    props.letter.letter || h('span', { "style": { opacity: 0 } }),
                    h('rp', "("),
                    h('rt', props.letter.pinyin || " "),
                    h('rp', ")")
                ])
            )
        }

    }
});


export const KeyBoard = defineComponent({
    name: 'KeyBoard',
    props: {
        letters: { type: Array as PropType<Array<Letter>>, required: true },
        showEnter: { Type: Boolean, default: true },
        showBackspace: { Type: Boolean, default: true },
        showHowto: {Type:Boolean, default: true}
    },
    methods: {
        renderKey(letter: Letter): VNode {
            const letterClass: string = letter.state === LetterState.INITIAL ? "" : styles[letter.state];
            return h('button', {
                "class": letterClass,
                'tableIndex': -1,
                onClick: () => { if (letter.state !== LetterState.DISABLED) { this.$emit("letterTouched", letter.letter) } }
            },
                h('ruby', [
                    letter.letter,
                    h('rp', '('),
                    h('rt', letter.pinyin || " "),
                    h('rp', ')')
                ]))
        },

        renderKeys(): VNode[] {
            return Array.from(this.letters, (letter) => (this.renderKey(letter)))
        },

        renderBackspace(): VNode {
            return h('svg', { viewBox: "0 0 24 24", fill: "currentColor", width: "24", height: "24" },
                h('path', { d: "M22 3H7c-.69 0-1.23.35-1.59.88L0 12l5.41 8.11c.36.53.9.89 1.59.89h15c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H7.07L2.4 12l4.66-7H22v14zm-11.59-2L14 13.41 17.59 17 19 15.59 15.41 12 19 8.41 17.59 7 14 10.59 10.41 7 9 8.41 12.59 12 9 15.59z" }))
        },

        renderControls(): VNode[] {
            const controls: VNode[] = []
            if (this.$props.showEnter) {
                controls.push(h('button', { onClick: () => { this.$emit("enter") } }, "Enter"))
            }else {
                controls.push(h('div', { 'class': styles['blank-button'] }))
            }

            if (this.$props.showHowto){
                controls.push(h('button', { 'class': styles['howto-button'], onClick: () => { this.$emit("howto") } }, '如何玩'))
            }

            if (this.$props.showBackspace) {
                controls.push(h('button', { onClick: () => { this.$emit("backspace") } }, this.renderBackspace()))
            } else {
                controls.push(h('div', { 'class': 'blank-button' }))
            }
            return controls;
        }
    },
    emits: {
        letterTouched: (letter: string) => { return true },
        enter: null,
        backspace: null,
        howto: null
    },
    render() {
        return h('div', { 'id': styles['keyboard'] },
            h('div', { "class": styles["inner"] }, [
                h('div', { "class": styles["keys"] }, this.renderKeys()),
                h('div', { "class": styles["row"] }, [
                    ...this.renderControls()
                ])

            ]))
    }
});


class WordFigureOutScene {
    config: WordFigureOutSceneConfig
    idiom: string
    idiomPinyin: string[]
    keys: Letter[]
    board: Letter[]
    input_indexes: number[]
    entered_indexes: number[]
    show_error = false
    won = false
    lost = false
    notify_cb: Function

    constructor(config: WordFigureOutSceneConfig, callback: Function) {
        this.idiom = config.idiom
        this.keys = []
        this.board = []
        this.config = config
        this.entered_indexes = []
        this.input_indexes = []
        this.notify_cb = callback
        const keys: Letter[] = []
        for (const key of config.keys) {
            const py = getPinyinOne(key, this.config.pinyin) ?? ""
            keys.push({ letter: key, pinyin: py, state: LetterState.INITIAL, canDelete: true })
        }

        this.keys = keys

        let idiomPinyin = getIdiomPinyin(this.idiom, this.config.pinyin)
        if (idiomPinyin === undefined) {
            idiomPinyin = ['', '', '', '']
        }
        this.idiomPinyin = idiomPinyin

        for (let idx = 0; idx < this.idiom.length; idx++) {
            const key = this.idiom[idx]
            if (config.keys.includes(key)) {
                this.board.push({
                    letter: '',
                    pinyin: "",
                    state: LetterState.INITIAL,
                    canDelete: true
                })
                this.input_indexes.push(idx)
            } else {
                this.board.push({
                    letter: key,
                    pinyin: getPinyinOne(key, this.config.pinyin) ?? "",
                    state: LetterState.INITIAL,
                    canDelete: true,
                })
            }
        }

    }

    applyWrongLetter() {
        const candidates = this.keys.filter((item) => (item.state === LetterState.INITIAL && !this.idiom.includes(item.letter)))
        if (candidates.length === 0)
            return {
                ok: false,
                error: "所有不存在的字都已经被标注了，就是那些底色是灰色的字"
            }
        const index = Math.floor(Math.random() * candidates.length)
        const letter = candidates[index]
        letter.state = LetterState.ABSENT
        return {
            ok: true,
            message: `成语中没有 “${letter.letter}” 字。`
        }
    }

    applyCorrectLetter() {
        const candidates = this.keys.filter((item) => (item.state === LetterState.INITIAL && this.idiom.includes(item.letter)))
        if (candidates.length === 0)
            return {
                ok: false,
                error: "所有存在的字都已经被标注了，就是那些底色是橙色、绿色的字"
            }
        const index = Math.floor(Math.random() * candidates.length)
        const letter = candidates[index]
        const letter_index = this.idiom.indexOf(letter.letter) + 1
        letter.state = LetterState.CORRECT
        return {
            ok: true,
            message: `成语的第 ${letter_index} 个字是 “${letter.letter}”`
        }
    }

    applyComplete() {
        for (const idx of this.input_indexes) {
            this.board[idx] = {
                pinyin: this.idiomPinyin[idx],
                letter: this.idiom[idx],
                state: LetterState.INITIAL,
                canDelete: true
            }
        }
        this.handleEnter()
        return {
            ok: true,
            message: ""
        }
    }

    applyFail() {
        this.won = false
        this.lost = true
        this.notify_cb()
        return {
            ok: true,
            message: ""
        }
    }

    apply(func_name: string) {
        if(this.won || this.lost){
            return {
                ok: false,
                error: "游戏已经结束了！"
            }
        }
        const name = func_name.replace('_', '-')
        if (name === "wrong-letter") {
            return this.applyWrongLetter()
        } else if (name === "correct-letter") {
            return this.applyCorrectLetter()
        } else if (name === "correct-all") {
            return this.applyCorrectLetter()
        } else if (name === "complete") {
            return this.applyComplete()
        } else if (name === "fail") {
            return this.applyFail()
        } else {
            return {
                ok: false,
                error: "wrong func_name " + func_name
            }
        }
    }

    canApply(func_name: string): ConditionResponse{
        if(this.won || this.lost){
            return {
                ok: false,
                message: "游戏已经结束了!"
            }
        }
        const name = func_name.replace('_', '-')
        if (name === "wrong-letter") {
            const candidates = this.keys.filter((item) => (item.state === LetterState.INITIAL && !this.idiom.includes(item.letter)))
            if (candidates.length === 0){
                return {
                    ok: false,
                    message: "没有字需要排除了"
                }
            } else {
                return { ok: true}
            }
        } else if (name === "correct-letter") {
            const candidates = this.keys.filter((item) => (item.state === LetterState.INITIAL && this.idiom.includes(item.letter)))
            if(candidates.length > 0){
                return { ok: true}
            } else {
                return {
                    ok: false,
                    message: "所有正确的字都已经提示了"
                }
            }
        } else if (name === "correct-all") {
            return { ok: true}
        } else if (name === "complete") {
            return { ok: true}
        } else if (name === "fail") {
            return { ok: true}
        } else {
            return {
                ok: false,
                message: "无法支持该操作"
            }
        }
    }

    handleKeyInput(key: string) {
        this.show_error = false
        for (let idx = 0; idx < this.idiom.length; idx++) {
            const letter = this.board[idx];
            if (letter.letter === '') {
                letter.letter = key
                letter.pinyin = getPinyinOne(letter.letter, this.config.pinyin)
                this.entered_indexes.push(idx)
                break
            }
        }

        this.handleEnter()
    }

    handleEnter() {
        const items = this.board.filter((item) => (item.letter === ''))
        if (items.length == 0) {
            this.show_error = false
            this.won = false
            this.lost = false
            const idiom: string = Array.from(
                this.board.map((letter) => (letter.letter))
            ).join('')
            if (idiom === this.idiom) {
                for (const key of this.board) {
                    key.state = LetterState.CORRECT
                }
                for (const key of this.keys) {
                    if (this.idiom.includes(key.letter)) {
                        key.state = LetterState.CORRECT
                    }
                }
                this.won = true
            } else {
                for (const key of this.keys) {
                    if (!this.idiom.includes(key.letter)) {
                        key.state = LetterState.ABSENT
                    }
                }
                this.show_error = true
                this.lost = true
            }
            this.notify_cb()
        }
    }

    handleBackspace() {
        if(this.won || this.lost){
            return
        }
        this.show_error = false
        const idx = this.entered_indexes.pop();
        if (idx === undefined) return
        const letter = this.board[idx]
        letter.letter = ''
        letter.pinyin = ''
    }

}

export const WordFigureOut = defineComponent({
    name: 'WordFigureOut',
    props: {
        config: { type: Object as PropType<WordFigureOutSceneConfig>, required: true },
        level: { type: Object as PropType<LevelInfo>, required: true }
    },
    data() {
        return {
            scene: new WordFigureOutScene(this.$props.config, this.handle_level_event),
            report_played: true
        }
    },
    emits: {
        succeed: (played: PlayableResult) => { return true },
        failed: (played: PlayableResult) => { return true },
        played: () => { return true },
        showModal: (content_render: Function) => { return true}
    },
    computed: {
        status(): string {
            if (this.$data.scene.won) {
                return 'won'
            } else if (this.$data.scene.lost) {
                return 'lost'
            }
            return 'unknown'
        }
    },
    watch: {
        config(newConfig, oldConfig) {
            this.$data.scene = new WordFigureOutScene(this.$props.config, this.handle_level_event)
            this.$data.report_played = true
        }
    },
    methods: {
        handle_level_event() {
            const idiom = this.scene.idiom
            const detail = this.scene.config.detail
            if(this.$data.report_played){
                this.$emit('played')
                this.$data.report_played = false
            }
            if (this.scene.won) {
                setTimeout(() => {
                    this.$emit('succeed', {
                        succeed: true,
                        archievement: { rating: 3 },
                        items: [{ type: "item", name: "word_figureout.chengyu", idiom: idiom,  detail: detail }],
                        level: this.level
                    })
                }, 500)

            } else if (this.scene.lost) {
                setTimeout(() => {
                    this.$emit('failed', {
                        succeed: false,
                        archievement: { rating: 3 },
                        items: [{ type: "item", name: "word_figureout.chengyu", idiom: idiom, detail: detail }],
                        level: this.level
                    })
                }, 500)
            }
        },

        apply(func_name: string): ApplyResponse {
            return this.scene.apply(func_name)
        },

        canApply(name: string): ConditionResponse{
            return this.scene.canApply(name)
        },

        reset() {
            this.scene = new WordFigureOutScene(this.$props.config, this.handle_level_event)
            this.report_played = true
        },

        renderBoard(): VNode {
            const rows: VNode[] = []
            const row = this.scene.board
            const tiles: VNode[] = []
            const rowState: string[] = []
            for (let j = 0; j < row.length; j++) {
                tiles.push(h(Tile, { letter: row[j] }))
                rowState.push(row[j].state)
            }
            const rowClass = [styles["row"], this.scene.won ? styles["correctrow"] : "",
            this.scene.show_error ? styles["error"] : "",
                "current"]
            rows.push(h('div', { "class": rowClass }, tiles))

            const boardClass = [this.scene.won ? styles["won"] : ""]
            return h('div', { 'id': styles["board"], 'class': boardClass }, rows)
        }
    },

    render(): VNode {
        return h('div', { class: styles["word-figureout-root"] }, [
            this.renderBoard(),
            h(KeyBoard, {
                letters: this.scene.keys,
                showEnter: false,
                onLetterTouched: (key: string) => {
                    this.scene.handleKeyInput(key);
                },
                onBackspace: () => { this.scene.handleBackspace() },
                onHowto: () => {
                    this.$emit("showModal", () => {
                        return h('div', {}, [
                            h('p', '选择正确的字，补充完整成语。'),
                            h('p', '四个字都是绿色时，就选对了～～～'),
                            h('p', '选对了，就有会有金币奖励的，有时还会有道具物品，要注意收集呦！')
                        ])
                    })
                }
            })
        ])
    }
});

export default WordFigureOut;
