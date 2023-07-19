import { h, defineComponent, VNode, PropType } from 'vue';
import styles from './chengyu_wordle.module.css'
import chengyu_all from './chengyu_wordle.data.json'
import { ApplyResponse, ConditionResponse, LevelInfo, PlayableResult } from './defines';

export function range(start: number, end: number) {
    const ans: Array<number> = [];
    if (start >= end) {
        return ans
    }
    for (let i = start; i < end; i++) {
        ans.push(i);
    }
    return ans;
}


export interface ChengYuDetail {
    derivation: string,
    example: string,
    explanation: string,
    pinyin: string,
    word: string,
    abbreviation: string
}

export interface ChengYuWordleSceneConfig {
    idiom: string,
    text?: string,
    image_href?: string,
    keys: string[],
    pinyin: { [letter: string]: string | string[] },
    detail: {
        derivation: string,
        example: string,
        explanation: string,
        pinyin: string,
        word: string,
        abbreviation: string
    }

}

const ALL_IDIOMS: Set<string> = new Set(chengyu_all['chengyu-all'])

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

function getPinyinMulti(letter: string, pinyindb: object) {
    const letterPinyins = new Set()
    for (const [key, value] of Object.entries(pinyindb)) {
        if (letter === key) {
            letterPinyins.add(value)
        } else if (key.includes(letter)) {
            const idx = key.indexOf(letter)
            letterPinyins.add((value as string[])[idx])
        }
    }
    return Array.from(letterPinyins)
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
    hint?: string,
    state: LetterState
}

export const CloseIcon = defineComponent({
    name: 'CloseIcon',
    render() {
        return h('svg', { viewBox: "0 0 24 24", width: 24, height: 24, ...this.$props }, [
            h('title', '✖️'),
            h('path', { fill: "currentColor", d: "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" })
        ])
    }
});


export const Tile = defineComponent({
    name: 'LetterTile',
    props: {
        letter: { type: Object as PropType<Letter>, required: true },
        current: { type: Boolean, default: false }
    },
    methods:{
        renderLetter() {
            if(this.letter.letter){
                return this.letter.letter
            } else if(this.letter.hint){
                return h('div', {"class":styles["letter-hint"]}, this.letter.hint)
            } else {
                return h('span', { "style": { opacity: 0 } })
            }
        }
    },
    render(){
        const props = this.$props
        const tileClass = [styles["letter"], props.letter.letter ? styles["lettered"] : "",
        props.letter.state === LetterState.INITIAL ? styles['initial'] : styles[props.letter.state],
        props.letter.state === LetterState.INITIAL ? '' : styles['letter-anim'],
        props.current ? styles["current_tile"] : ''
        ]
        const rubyClass = [props.letter.state === LetterState.INITIAL ? '' : styles["letter_flip_back"]]
        return h('div', { "class": tileClass },
            h('ruby', { "class": rubyClass }, [
                this.renderLetter() ,
                h('rp', "("),
                h('rt', props.letter.pinyin || " "),
                h('rp', ")")
            ])
        )
    }
});


export const KeyBoard = defineComponent({
    name: 'KeyBoard',
    props: {
        letters: { type: Array as PropType<Array<Letter>>, required: true },
        showEnter: { Type: Boolean, default: true },
        showBackspace: { Type: Boolean, default: true }
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
            } else {
                controls.push(h('div', { 'class': styles['blank-button'] }))
            }

            if (this.$props.showBackspace) {
                controls.push(h('button', { onClick: () => { this.$emit("backspace") } }, this.renderBackspace()))
            } else {
                controls.push(h('div', { 'class': styles['blank-button'] }))
            }
            return controls;
        }
    },
    emits: {
        letterTouched: (letter: string) => { return true },
        enter: null,
        backspace: null
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

export interface WonFeature {
    one_shot: boolean,
    two_shot: boolean,
    step_over: boolean
}

class ChengYuWordleScene {
    max_letters = 4
    max_steps = 5
    config: ChengYuWordleSceneConfig
    idiom: string
    idiomPinyin: string[]
    keys: Letter[]
    board: Letter[][]
    entering_step = 0
    entering_idx = 0
    show_error = false
    correct_step = -1
    won = false
    lost = false
    rating = 1
    won_feature: WonFeature = {
        one_shot: false,
        two_shot: false,
        step_over: false
    }

    correct_hint: Array<Letter | undefined> = [undefined, undefined, undefined, undefined]
    options = {
        'disable_letter_when_absent': false,
        'correct_hint_inline': true,
    }
    notify_cb: Function

    constructor(config: ChengYuWordleSceneConfig, callback:Function) {
        this.idiom = config.idiom
        this.keys = []
        this.board = []
        this.config = config
        this.entering_step = 0
        this.entering_idx = 0
        if (this.config.text || this.config.image_href) {
            this.max_steps = 3
        }
        this.notify_cb = callback

        let idiomPinyin = getIdiomPinyin(this.idiom, this.config.pinyin)
        if (idiomPinyin === undefined) {
            idiomPinyin = ['', '', '', '']
        }
        this.idiomPinyin = idiomPinyin

        const gameKeys = this.config.keys
        gameKeys.forEach((letter) => {
            const arrPinyin = getPinyinMulti(letter, this.config.pinyin)
            this.keys.push({
                letter: letter,
                pinyin: arrPinyin.join(' '),
                state: LetterState.INITIAL
            })
        })

        for (let i = 0; i < this.max_steps; i++) {
            const row: Letter[] = []
            for (let j = 0; j < this.max_letters; j++) {
                row.push({
                    letter: '',
                    pinyin: '',
                    state: LetterState.INITIAL
                })
            }
            this.board.push(row)
        }
    }

    applyWrongLetter() {
        const candidates = this.keys.filter((item) => (item.state === LetterState.INITIAL && !this.idiom.includes(item.letter)))
        if (candidates.length === 0)
            return {
                ok: false,
                error: "所有不存在的字都已经被标注了，就是那些底色是灰色的字"
            }
        const wrong_letters: Array<string> = []
        for (let i = 0; i < 2; i++) {
            const index = Math.floor(Math.random() * candidates.length)
            const letter = candidates[index]
            if (this.options.disable_letter_when_absent) {
                letter.state = LetterState.DISABLED
            } else {
                letter.state = LetterState.ABSENT
            }
            if (!wrong_letters.includes(letter.letter)) {
                wrong_letters.push(letter.letter)
            }
        }

        const wrong_letters_text = wrong_letters.join('“，”')

        return {
            ok: true,
            message: `成语中没有 “${wrong_letters_text}” 字。`
        }
    }

    applyCorrectLetter() {
        const corrects =
            this.keys.filter(
                (item) => (item.state === LetterState.CORRECT)
            ).map((item) => {
                return item.letter
            })
        const candidates: Array<number> = []
        for (let i = 0; i < 4; i++) {
            const letter = this.idiom[i]
            if (this.correct_hint[i] === undefined && !corrects.includes(letter)) {
                candidates.push(i)
            }
        }
        if (candidates.length === 0)
            return {
                ok: false,
                error: "所有存在的字都已经被标注了。"
            }
        const index = Math.floor(Math.random() * candidates.length)
        const letter_index = candidates[index]
        const letter_letter = this.idiom[letter_index]
        const letter_hint = {
            pinyin: this.idiomPinyin[letter_index],
            letter: letter_letter,
            state: LetterState.CORRECT,
            canDelete: false
        }
        this.keys.filter((item) => (item.letter === letter_letter))
            .map((letter) => { letter.state = LetterState.CORRECT })

        this.correct_hint[letter_index] = letter_hint
        this.board[this.entering_step][letter_index].hint = letter_hint.letter
        this.refreshEnteringIdx()
        return {
            ok: true,
            message: `成语的第 ${letter_index + 1} 个字是 “${letter_letter}”`
        }
    }

    refreshEnteringIdx() {
        let entering_idx = 0
        for (const idx of range(0, 4)) {
            const entering_letter = this.board[this.entering_step][idx]
            if (entering_letter.letter === '') {
                entering_idx = idx
                break
            } else {
                entering_idx = idx + 1
            }
        }
        this.entering_idx = entering_idx
    }

    applyCorrectAll() {
        const candidates = this.keys.filter((item) => (item.state === LetterState.INITIAL && this.idiom.includes(item.letter)))
        for (const letter of candidates) {
            letter.state = LetterState.CORRECT
        }
        for (let idx = 0; idx < 4; idx++) {
            this.board[this.entering_step][idx] = {
                pinyin: this.idiomPinyin[idx],
                letter: this.idiom[idx],
                state: LetterState.CORRECT
            }
        }
        this.entering_idx = 4
        this.handleEnter()
        return {
            ok: true,
            message: `成语是 “${this.idiom}”`
        }
    }

    applyComplete() {
        for (let idx = 0; idx < 4; idx++) {
            this.board[this.entering_step][idx] = {
                pinyin: this.idiomPinyin[idx],
                letter: this.idiom[idx],
                state: LetterState.INITIAL
            }
        }
        this.entering_idx = 4
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
            return this.applyCorrectAll()
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
            const hintable = this.correct_hint.filter((item) => (item === undefined))
            if(hintable.length > 0){
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
        const idx: number = this.entering_idx
        const partIdiom = []
        if (idx < 4) {
            const letterInit = this.board[this.entering_step][idx]
            this.board[this.entering_step][idx] = {
                letter: key,
                pinyin: getPinyinOne(key, this.config.pinyin),
                state: LetterState.INITIAL,
                hint: letterInit.hint
            }
        }
        this.refreshEnteringIdx()
        for (let i = 0; i <= idx; i++) {
            partIdiom.push(this.board[this.entering_step][i])
        }
        const idiomPinyin = getIdiomPinyin(partIdiom.join(''), this.config.pinyin)
        if (idiomPinyin != undefined) {
            for (const pyidx in idiomPinyin) {
                const newPinyin = idiomPinyin[pyidx]
                const letter = this.board[this.entering_step][pyidx]
                if (newPinyin !== letter.pinyin) {
                    letter.pinyin = newPinyin
                }
            }
        }
        if(this.entering_idx >= 4){
            this.handleEnter()
        }
    }

    updateKeyboard(letter: Letter) {
        const matched = this.keys.find((element) => element.letter === letter.letter)
        if (!matched)
            return;
        if (matched.state === LetterState.INITIAL
            || letter.state === LetterState.CORRECT
            || (matched.state === LetterState.ABSENT && letter.state === LetterState.PRESENT)) {
            matched.state = letter.state
        }
    }

    handleEnter() {
        this.show_error = false
        this.won = false
        this.lost = false
        this.won_feature = {
            one_shot: false,
            two_shot: false,
            step_over: false
        }
        const idiom: string = Array.from(
            this.board[this.entering_step].map((letter) => (letter.letter))
        ).join('')
        if (!ALL_IDIOMS.has(idiom)) {
            this.show_error = true
            return;
        }
        if (idiom === this.idiom) {
            this.correct_step = this.entering_step
            this.won = true
            if (this.entering_step === 0) {
                this.won_feature.one_shot = true
                this.rating = 3
            } else if (this.entering_step === 1) {
                this.won_feature.two_shot = true
                this.rating = 3
            } else if (this.entering_step === 2 || this.entering_step === 3) {
                this.rating = 2
            } else {
                this.rating = 1
            }
        }
        const idiomArr = this.idiom.split('')
        const entering = this.board[this.entering_step]
        const presented = this.keys.filter((item) =>
            (item.state === LetterState.CORRECT || item.state === LetterState.PRESENT))
            .map((item) => { return item.letter })
        const entered = entering.map((item) => { return item.letter })

        if (this.entering_step === 0) {
            this.won_feature.step_over = true
        } else if (this.entering_step > 0 && this.won_feature.step_over === true) {
            for (const letter of presented) {
                if (!entered.includes(letter)) {
                    this.won_feature.step_over = false
                    break;
                }
            }
        }

        if (this.won === true && this.won_feature.step_over === true && this.rating < 3) {
            this.rating += 1
        }

        for (let i = 0; i < idiomArr.length; i++) {
            const letter = entering[i]
            if (!idiomArr.includes(letter.letter)) {
                if (this.options.disable_letter_when_absent) {
                    letter.state = LetterState.DISABLED
                } else {
                    letter.state = LetterState.ABSENT
                }
            } else if (letter.letter === idiomArr[i]) {
                letter.state = LetterState.CORRECT
            } else {
                letter.state = LetterState.PRESENT
            }
            this.updateKeyboard(letter)
        }

        if (this.entering_step >= ( this.max_steps - 1) && !this.won) {
            this.lost = true
        }

        if (this.won === false && this.lost === false) {
            this.entering_step += 1
            // let entering_idx: number | undefined = undefined
            for (const [idx, letter_hint] of this.correct_hint.entries()) {
                if (letter_hint) {
                    this.board[this.entering_step][idx].hint = letter_hint.letter
                }
            }
            this.entering_idx = 0
            this.notify_cb()
        } else {
            this.notify_cb()
        }
    }

    handleBackspace() {
        if(this.won || this.lost){
            return
        }
        this.show_error = false
        for (const idx of range(0, this.entering_idx).reverse()) {
            const letter = this.board[this.entering_step][idx]
            letter.letter = ''
            letter.state = LetterState.INITIAL
            letter.pinyin = ''
            break
        }
        this.refreshEnteringIdx()
    }

}

export const ChengYuWordle = defineComponent({
    name: 'ChengYuWordle',
    props: {
        config: { type: Object as PropType<ChengYuWordleSceneConfig>, required: true },
        level: { type: Object as PropType<LevelInfo>, required: true }
    },
    emits: {
        succeed: (played: PlayableResult) => { return true },
        failed: (played: PlayableResult) => { return true },
        played: () => { return true }
    },
    data() {
        return {
            scene: new ChengYuWordleScene(this.$props.config, this.handle_level_event),
            report_played: true
        }
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
            this.$data.scene = new ChengYuWordleScene(this.$props.config, this.handle_level_event)
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
                        archievement:
                            {
                                rating: this.scene.rating,
                                features: this.scene.won_feature
                            },
                        items: [
                            {
                                type: "item",
                                name: "chengyu_wordle.chengyu",
                                idiom: idiom,
                                detail: detail
                            }
                        ],
                        level: this.level
                    })
                }, 500)
            } else if (this.scene.lost) {
                setTimeout(() => {
                    this.$emit('failed',{
                        succeed: false,
                        archievement:
                            {
                                rating: this.scene.rating,
                                features: this.scene.won_feature
                            },
                        items: [
                            {
                                type: "item",
                                name: "chengyu_wordle.chengyu",
                                idiom: idiom, detail: detail
                            }
                        ],
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
            this.scene = new ChengYuWordleScene(this.$props.config, this.handle_level_event)
            this.report_played = true
        },


        renderTitle(): VNode {
            if (this.config.text) {
                return h('div', { "id": styles["text-title"] },
                    h('div', { "class": styles["keys"] }, this.config.text))
            } else if (this.config.image_href) {
                return h('div', { "id": styles["image-title"] },
                    h('img', { "src": `${this.config.image_href}`, "alt": "IMAGE" }))
            } else {
                return h('div')
            }
        },

        renderBoard(): VNode {
            const rows: VNode[] = []
            for (let i = 0; i < this.scene.board.length; i++) {
                const row = this.scene.board[i]
                const tiles: VNode[] = []
                const rowState: string[] = []
                for (let j = 0; j < row.length; j++) {
                    const current = (i === this.scene.entering_step) && (j === this.scene.entering_idx)
                    tiles.push(h(Tile, { letter: row[j], current: current }))
                    rowState.push(row[j].state)
                }
                const rowClass = [styles["row"], i === this.scene.correct_step ? styles["correctrow"] : "",
                i === this.scene.entering_step && this.scene.show_error ? styles["error"] : "",
                i === this.scene.entering_step ? styles["current"] : ""]
                rows.push(h('div', { "class": rowClass }, tiles))
            }
            const boardClass = [this.scene.won ? styles["won"] : ""]
            return h('div', { 'id': styles["board"], 'class': boardClass }, rows)
        }
    },

    render(): VNode[] {
        return [
            this.renderTitle(),
            this.renderBoard(),
            h(KeyBoard, {
                letters: this.scene.keys,
                showEnter: false,
                onLetterTouched: (key: string) => { this.scene.handleKeyInput(key) },
                onEnter: () => {
                    this.scene.handleEnter();
                },
                onBackspace: () => { this.scene.handleBackspace() }
            })
        ]
    }
});

export default ChengYuWordle;