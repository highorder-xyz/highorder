import * as Phaser from 'phaser';
import { defineComponent, h, PropType} from 'vue'
import { ApplyResponse, ConditionResponse, LevelInfo, PlayableResult } from './defines';

var scaleRatio = window.devicePixelRatio
const assetRatio = 4
const assetScale = scaleRatio / assetRatio

const fontFamily = '"Droid Sans", "PingFangSC-Regular", "Microsoft YaHei", sans-serif'


export interface BlankLetter {
    blank: boolean,
    letter: string
}

export interface ChengyuLine {
    start: [number, number],
    direction: number,
    letters: Array<string | BlankLetter>
}

export interface ChengYuDetail {
    derivation: string,
    example: string,
    explanation: string,
    pinyin: string,
    word: string,
    abbreviation: string
}

export interface ChengyuCrossConfig {
    lines: Array<ChengyuLine>
    details?: Array<ChengYuDetail>
}

export interface TextItem {
    text: Phaser.GameObjects.Text,
    letter: string,
    x: number,
    y: number,
    slot_id: string,
    animating: boolean,
    prev_slot_id: string | undefined
}

export interface TextSlot {
    slot_id: string,
    item: TextItem | undefined,
    movable: boolean,
    back: Phaser.GameObjects.Shape | undefined,
    input_hint: Phaser.GameObjects.Shape | undefined,
    x: number,
    y: number
}

interface TextWordLine{
    slots: Array<string>
    letters: Array<string>
    matched: boolean
}

function arrayEqual(array1: any[], array2: any[]):boolean{
    return array1.length === array2.length && array1.every(function(value, index) { return value === array2[index]})
}

function shuffle(array: any[]) {
    let currentIndex = array.length, randomIndex;

    // While there remain elements to shuffle.
    while (currentIndex != 0) {
        // Pick a remaining element.
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;
        // And swap it with the current element.
        [array[currentIndex], array[randomIndex]] = [
            array[randomIndex], array[currentIndex]];
    }

    return array;
}

export function randomString(n: number, charset?: string): string {
    let res = '';
    let chars =
        charset || 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let charLen = chars.length;

    for (var i = 0; i < n; i++) {
        res += chars.charAt(Math.floor(Math.random() * charLen));
    }

    return res;
}

function randomSlotId(): string {
    return randomString(6, "abcdefghijklmnopqrstuvwxyz")
}

export class ChengyuCrossScene extends Phaser.Scene {
    config: ChengyuCrossConfig
    level_info: LevelInfo

    notify_cb: Function
    report_played: boolean
    emitter_cb: Function
    won: boolean
    lost: boolean

    x_offset: number
    y_offset: number
    slots: Array<TextSlot>
    slots_pos: Record<string, TextSlot>
    candidate_slots: Array<TextSlot>
    chengyu_lines: Array<TextWordLine>
    current: TextSlot | undefined

    constructor(config: ChengyuCrossConfig, level: LevelInfo, callback:Function, emitter:Function){
        super("ChengyuCrossScene")
        this.config = config
        this.level_info = level
        this.notify_cb = callback ?? (() => {})
        this.emitter_cb = emitter ?? (() => {})
        this.x_offset = 0
        this.y_offset = 0
        this.slots = []
        this.slots_pos = {}
        this.candidate_slots = []
        this.chengyu_lines = []
        this.current = undefined
        this.report_played = true
        this.won = false
        this.lost = false
    }

    public preload() {

    }


    getCrossPosition(pos: [number, number]){
        const start_x = this.x_offset
        const start_y = this.y_offset

        return {
            x: (pos[0]*40 + start_x)*scaleRatio,
            y: (pos[1]*40 + start_y)*scaleRatio
        }
    }

    createCross() {
        const candidates: Record<string, string>  = {}
        for(const line of this.config.lines){
            const slots = []
            const letters = []
            for(const [idx, letter] of line.letters.entries()){
                let pos = line.start
                if(line.direction === 0){
                    pos = [line.start[0] + idx, line.start[1]]
                } else {
                    pos = [line.start[0], line.start[1] + idx]
                }
                let slot_id = randomSlotId()
                const pos_str = `${pos[0]},${pos[1]}`

                let letter_str = ""
                if(typeof letter === "string"){
                    letter_str = letter
                } else if (typeof letter === "object" && letter !== null){
                    letter_str = letter.letter
                    if(!(pos_str in candidates)){
                        candidates[pos_str] = letter_str
                    }
                }

                let create_slot = !(pos_str in this.slots_pos)

                if(create_slot){
                    const pos_xy = this.getCrossPosition(pos)
                    const r = this.add.rectangle(pos_xy.x, pos_xy.y, 36*scaleRatio, 36*scaleRatio)
                    if(typeof letter === "string"){
                        r.setStrokeStyle(1*scaleRatio, 0x000000, 0)
                    } else {
                        r.setStrokeStyle(1*scaleRatio, 0x000000, 0.3)
                    }
                    r.setOrigin(0.5, 0.5)

                    const h = this.add.rectangle(pos_xy.x, pos_xy.y + 13*scaleRatio, 26*scaleRatio, 3*scaleRatio)
                    h.setFillStyle(0xaaaaaa, 0)
                    h.setOrigin(0.5, 0.5)

                    let item = undefined
                    let movable = true
                    if(typeof letter === "string"){
                        const text = this.add.text(pos_xy.x, pos_xy.y, letter,
                            {
                                fontSize: `${28*scaleRatio}px`,
                                fontStyle: "normal",
                                fontFamily: fontFamily,
                                color: "#000000"
                            })
                        text.setOrigin(0.5, 0.5)
                        item = {
                            text: text,
                            letter: letter,
                            animating: false,
                            x: pos_xy.x,
                            y: pos_xy.y,
                            slot_id: slot_id,
                            prev_slot_id: undefined
                        }
                        movable = false
                    }

                    const slot:TextSlot = {
                        item: item,
                        back: r,
                        input_hint: h,
                        slot_id: slot_id,
                        movable: movable,
                        x: pos_xy.x,
                        y: pos_xy.y
                    }
                    if(movable === true){
                        r.setInteractive(new Phaser.Geom.Rectangle(0*scaleRatio, 0*scaleRatio,
                                36*scaleRatio, 36*scaleRatio), Phaser.Geom.Rectangle.Contains)
                        r.on("pointerdown", () => {
                            this.setCurrent(slot)
                        })
                    }

                    this.slots.push(slot)
                    this.slots_pos[pos_str] = slot

                } else {
                    const exits_slot = this.slots_pos[pos_str]
                    slot_id = exits_slot.slot_id
                }
                slots.push(slot_id)
                letters.push(letter_str)
            }
            this.chengyu_lines.push({
                slots: slots,
                letters: letters,
                matched: false
            })
        }

        const candidate_values = Object.values(candidates)
        return shuffle(candidate_values)

    }

    createCandidates(candidates: string[]) {
        let line_count = candidates.length
        if(candidates.length > 5){
            line_count = Math.ceil(candidates.length/2)
        }
        const space = (360 - 36*line_count - 4*(line_count - 1))/2
        const bg = this.add.rectangle(180*scaleRatio, 420*scaleRatio, 360*scaleRatio, 120*scaleRatio)
        bg.setFillStyle(0xf0f0f0, 1)
        const bgtop = this.add.rectangle(180*scaleRatio, 360*scaleRatio, 360*scaleRatio, 1*scaleRatio)
        bgtop.setFillStyle(0xcccccc, 1)
        for(const [idx, letter] of candidates.entries()){
            const line_idx = idx % line_count
            const line_num = Math.floor(idx/line_count)
            const even_tile = ((line_idx + line_num) % 2 === 1)
            const item_x = (space + line_idx*40 + 18)*scaleRatio
            const item_y = (400 + line_num*40)*scaleRatio
            const r = this.add.rectangle(item_x, item_y, 36*scaleRatio, 36*scaleRatio)
            r.setStrokeStyle(1*scaleRatio, 0x000000, 0.3)
            if(even_tile){
                r.setFillStyle(0xcccccc)
            }
            r.setOrigin(0.5, 0.5)
            const text = this.add.text(item_x, item_y, letter,
                {
                    fontSize: `${ 28*scaleRatio}px`,
                    fontStyle: "normal",
                    fontFamily: fontFamily,
                    color: "#000000"
                })
            text.setOrigin(0.5, 0.5)
            text.setInteractive(new Phaser.Geom.Rectangle(-2*scaleRatio, -2*scaleRatio,
                36*scaleRatio, 36*scaleRatio), Phaser.Geom.Rectangle.Contains)
            const slot_id = randomSlotId()
            const item = {
                text: text,
                letter: letter,
                animating: false,
                x: item_x,
                y: item_y,
                slot_id: slot_id,
                prev_slot_id: undefined
            }
            this.candidate_slots.push({
                slot_id: slot_id,
                item: item,
                movable:true,
                back: r,
                input_hint: undefined,
                x: item_x,
                y: item_y
            })
            text.on("pointerdown", () => {
                if(item.slot_id != ""){
                    this.itemClicked(item)
                }
            })
        }
    }

    getCandidateSlot(slot_id:string){
        const slots = this.candidate_slots.filter((slot) => (slot.slot_id === slot_id))
        if (slots.length > 0) {
            return slots[0]
        }
        return undefined
    }

    getCandidateSlotByLetter(letter: string){
        const slots = this.candidate_slots.filter((slot) => (slot.item && slot.item?.letter === letter))
        if (slots.length > 0) {
            return slots[0]
        }
        return undefined
    }

    getSlot(slot_id: string){
        const slots = this.slots.filter((slot) => (slot.slot_id === slot_id))
        if (slots.length > 0) {
            return slots[0]
        }
        return undefined
    }

    getSlotByLetter(letter: string){
        const slots = this.slots.filter((slot) => (slot.item && slot.item?.letter === letter))
        if (slots.length > 0) {
            return slots[0]
        }
        return undefined
    }

    getSlotList(slot_ids: Array<string>){
        const slot_list:Array<TextSlot> = []

        for(const slot_id of slot_ids){
            const slots = this.slots.filter((slot) => (slot.slot_id === slot_id))
            if (slots.length > 0) {
                slot_list.push(slots[0])
            }else {
                throw(`slot with id ${slot_id} not found.`)
            }
        }
        return slot_list
    }



    getSlotLetters(slot_list: Array<TextSlot> ){
        const letters: Array<string> = []
        for(const slot of slot_list){
            if(slot.item === undefined){
                letters.push("")
                continue
            }
            if(slot.slot_id !== slot.item?.slot_id){
                letters.push("")
                continue
            }
            letters.push(slot.item.letter)
        }
        return letters
    }

    async checkState(last_slot: TextSlot){
        const related_wordlines = this.chengyu_lines.filter((it) => (
            it.matched === false && it.slots.includes(last_slot.slot_id)
        ))
        const shakes_slot_id = new Set()
        for(const wordline of related_wordlines){
            const slot_list = this.getSlotList(wordline.slots)
            const letters = this.getSlotLetters(slot_list)


            if(arrayEqual(letters, wordline.letters)){
                const bounces = []
                wordline.matched = true
                for(const [idx, slot] of slot_list.entries()){
                    slot.movable = false
                    slot.back?.setStrokeStyle(1, 0x000000, 0.4)
                    slot.back?.setFillStyle(0x008000)
                    slot.item?.text.setFill('#ffffff')
                    const item = slot.item
                    if(!item){
                        continue
                    }

                    const exist_tweens = this.tweens.getTweensOf([slot.back, slot.item?.text])
                    for(const tween of exist_tweens){
                        tween.stop()
                        tween.remove()
                    }
                    item.animating = true
                    slot.back?.setPosition(slot.x, slot.y)
                    item.text.setPosition(item.x, item.y)
                    bounces.push(new Promise<void>((resolve, reject) => {
                        this.tweens.add({
                            targets: [slot.back, slot.item?.text],
                            duration: 160,
                            props: {
                                y: slot.y - 8*scaleRatio
                            },
                            delay: idx * 80,
                            yoyo: true,
                            ease: "Sine.easeOut",
                            onComplete: () => {
                                item.animating = false
                                resolve()
                            }
                        })
                    }))
                }
                await Promise.all(bounces)
            } else if ( wordline.slots.length === letters.join('').length){
                const shakes = []
                const flyback_slots = []
                let current_slot = undefined
                for(const [idx, slot] of slot_list.entries()){
                    const text = slot.item?.text
                    const back = (slot.movable)
                    const item = slot.item

                    if(text && item && slot.item?.slot_id === slot.slot_id){
                        if(back && current_slot === undefined){
                            current_slot = slot
                        }
                        if(back && slot.item){
                            flyback_slots.push(slot)
                        }
                        if (!shakes_slot_id.has(slot.slot_id)){
                            shakes_slot_id.add(slot.slot_id)
                            const shake_x = slot.x + 4*scaleRatio
                            if(item.animating == false){
                                item.animating = true
                                shakes.push(new Promise<void>((resolve, reject) => {
                                    this.tweens.add({
                                        targets: [item.text],
                                        duration: 50,
                                        props: {
                                            x: shake_x
                                        },
                                        yoyo: true,
                                        repeat: 6,
                                        onComplete: () => {
                                            // text.setX(slot.x)
                                            item.animating = false
                                            resolve()
                                        }
                                    })
                                }))
                            }

                        }

                    }
                }
                await Promise.all(shakes)
                const flybacks = []
                for(const slot of flyback_slots){
                    if(slot.item){
                        flybacks.push(this.flyBack(slot.item, slot))
                    }
                }
                await Promise.all(flybacks)
                if(this.current === undefined){
                    this.moveNext()
                }
            }

        }
        if(this.chengyu_lines.every((value, index) => (value.matched === true)) && this.won !== true){
            this.won = true
            this.notify_cb({
                succeed: true,
                archievement: {
                    rating: 3
                },
                items: this.config.details ?? [],
                level: this.level_info
            })
        }
    }

    async flyBack(item:TextItem, slot:TextSlot){
        if( item.prev_slot_id === undefined){
            throw(`no previous slot id ${item.prev_slot_id}`)
        }
        const target = this.getCandidateSlot(item.prev_slot_id)
        if(!target){
            throw(`error while get candidate slot with id ${item.prev_slot_id}`)
        }
        if(target.item !== undefined){
            console.log(target, target.item)
            throw('error while fly to target.')
        }
        // console.log(item)
        if(item.slot_id === ""){
            return
        }
        if(!slot.movable){
            return
        }
        if(slot.item !== item || item.slot_id !== slot.slot_id){
            return
        }
        // console.log('flyback', item, target.x, target.y)
        slot.item = undefined
        target.item = item
        item.x = target.x
        item.y = target.y
        item.prev_slot_id = undefined
        item.slot_id = ""
        await new Promise<void>((resolve, reject) => {
                this.add.tween({
                targets:[item.text],
                duration: 300,
                props: {
                    x: target.x,
                    y: target.y,
                },
                ease: "Sine.easyInOut",
                onComplete: () => {
                    item.slot_id = target.slot_id
                    resolve()
                }
            })
        })

    }

    async flyToBoard(item:TextItem, slot:TextSlot, target:TextSlot){
        if (slot.item !== item || item.slot_id === ""){
            return
        }
        target.item = item
        slot.item = undefined
        item.x = target.x
        item.y = target.y
        item.prev_slot_id = slot.slot_id
        item.slot_id = ""
        await new Promise<void>((resolve, reject) => {
            this.add.tween({
                targets:[item.text],
                duration: 300,
                props: {
                    x: target.x,
                    y: target.y,
                },
                ease: "Sine.easyInOut",
                onComplete: () => {
                    item.slot_id = target.slot_id
                    resolve()
                }
            })
        })
    }

    itemClicked(item:TextItem){
        console.log("itemClicked", item)
        if(this.current === undefined){
            return
        }
        if(this.report_played){
            this.emitter_cb('played', {})
            this.report_played = false
        }
        if(item.prev_slot_id === undefined){
            const target = this.current
            if(!target || target.item !== undefined){
                return
            }
            const slot = this.getCandidateSlot(item.slot_id)
            if(!slot){
                throw(`error while get candidate slot with id ${item.slot_id}`)
            }
            this.flyToBoard(item, slot, target).then(() => {
                this.checkState(target)
            })
            this.moveNext()

        } else {
            const slot = this.getSlot(item.slot_id)
            if(item.slot_id === ""){
                return
            }
            if(!slot){
                throw(`error while get slot with id ${item.slot_id}`)
            }
            if(!slot.movable){
                return
            }
            this.flyBack(item, slot).then(()=> {
            })
            this.setCurrent(slot)
        }


    }

    public checkConfig(){
        const letter_map:Record<string, string> = {}
        for(const line of this.config.lines){
            for(const [idx, letter] of line.letters.entries()){
                let pos = line.start
                let letter_str = ""
                if(typeof letter === "string"){
                    letter_str = letter
                } else if (typeof letter === "object" && letter !== null){
                    letter_str = letter.letter
                }
                if(line.direction === 0){
                    pos = [line.start[0] + idx, line.start[1]]
                } else {
                    pos = [line.start[0], line.start[1] + idx]
                }
                const pos_str = `${pos[0]},${pos[1]}`
                if(pos_str in letter_map){
                    if(letter_map[pos_str] !== letter_str){
                        throw(`config error, expected letter ${letter_str} in position (${pos_str}), exits ${letter_map[pos_str]}`)
                    }
                } else {
                    letter_map[pos_str] = letter_str
                }
            }

        }
    }

    public calcOffset(){
        let max_x = 0
        let max_y = 0
        for(const line of this.config.lines){
            for(const [idx, letter] of line.letters.entries()){
                let x = 0
                let y = 0
                if(line.direction === 0){
                    x = line.start[0] + idx
                    y = line.start[1]
                } else {
                    x = line.start[0]
                    y = line.start[1] + idx
                }
                if (x > max_x){
                    max_x = x
                }

                if (y > max_y){
                    max_y = y
                }
            }
        }
        const width = max_x * 40
        const height = max_y * 40
        this.x_offset = (360 - width)/2
        this.y_offset = (360 - height)/2
    }

    public moveNext() {
        const current = this.current
        let next_slot = undefined
        if(current){
            const idx = this.slots.indexOf(current)
            const slots_left = this.slots.slice(idx+1).filter((slot) => (slot.movable === true && slot.item === undefined))
            if(slots_left.length > 0){
                next_slot = slots_left[0]
            } else {
                const slots_left = this.slots.slice(0, idx).filter((slot) => (slot.movable === true && slot.item === undefined))
                if(slots_left.length > 0){
                    next_slot = slots_left[0]
                }
            }
        } else {
            const slots_left = this.slots.filter((slot) => (slot.movable === true && slot.item === undefined))
            if(slots_left.length > 0){
                next_slot = slots_left[0]
            }
        }

        if(next_slot !== undefined){
            this.setCurrent(next_slot)
        } else {
            this.clearCurrentTweens()
            this.current = undefined
        }

    }

    public clearCurrentTweens() {
        if(this.current !== undefined && this.current.back && this.current.input_hint){
            const tweens = this.tweens.getTweensOf([this.current.back, this.current.input_hint], true)
            for(const task of tweens){
                task.stop()
                task.remove()
            }
        }
    }

    public setCurrent(slot: TextSlot) {
        if(this.current && this.current.slot_id === slot.slot_id){
            return
        }
        if(slot.item !== undefined){
            return
        }
        if(slot.input_hint){
            this.clearCurrentTweens()
            this.current = slot
            this.add.tween({
                targets:[slot.input_hint, slot.back],
                duration: 800,
                props:{
                    strokeAlpha: 1,
                    lineWidth: 2*scaleRatio,
                    fillAlpha: 1,
                },
                ease: "Sine.easeInOut",
                repeat: -1,
                yoyo:true,
                onStop: () => {
                    if(slot.input_hint){
                        slot.input_hint.setFillStyle(0xaaaaaa, 0)
                    }
                    if(slot.back){
                        slot.back.setStrokeStyle(1*scaleRatio, 0x000000, 0.3)
                    }
                }
            })
        }

    }

    public create(data:any){
        this.checkConfig()
        this.calcOffset()
        const candidates = this.createCross()
        this.createCandidates(candidates)
        this.moveNext()
    }

    async inputCorrectOne() {
        if(this.current === undefined){
            return
        }
        const slot_id = this.current.slot_id
        const related_wordlines = this.chengyu_lines.filter((it) => (
            it.matched === false && it.slots.includes(slot_id)
        ))
        const wordline = related_wordlines[0]
        const slot_list = this.getSlotList(wordline.slots)
        let last_slot = undefined
        for(const [index, slot] of slot_list.entries()){
            if(slot.movable === false){
                continue
            }
            const letter = wordline.letters[index]
            last_slot = slot
            if(slot.item && slot.item.letter != letter){
                await this.flyBack(slot.item, slot)
            }

            let some_slot = this.getSlotByLetter(letter)
            if(some_slot !== undefined && some_slot.item !== undefined){
                await this.flyBack(some_slot.item, some_slot)
            }

            some_slot = this.getCandidateSlotByLetter(letter)
            if(some_slot !== undefined && some_slot.item !== undefined){
                await this.flyToBoard(some_slot.item, some_slot, slot)
            }
            this.moveNext()
        }
        if(last_slot){
            await this.checkState(last_slot)
        }

    }

    apply(name: string) {
        if(this.won || this.lost){
            return {
                ok: false,
                message: `游戏已经结束了。`
            }
        }
        if (name === 'correct_one') {
            this.inputCorrectOne()
            return {
                ok: true,
                message: "已经填写了一个成语"
            }
        }
        return {
            ok: false,
            message: "这个功能暂时还支持不了"
        }
    }

    canApply(name: string): ConditionResponse{
        if(this.won || this.lost){
            return {
                ok: false,
                message: "游戏已经结束了"
            }
        }
        let can = false
        if (name === 'correct_one') {
            if(this.current){
                const slot_id = this.current.slot_id
                const related_wordlines = this.chengyu_lines.filter((it) => (
                    it.matched === false && it.slots.includes(slot_id)
                ))
                if(related_wordlines.length > 0){
                    can = true
                }
            }

            if(can){
                return {
                    ok:true
                }
            } else {
                return {
                    ok: false,
                    message: "没有需要填写的成语"
                }
            }
        }

        return {
            ok: false,
            message: "这个功能暂时还支持不了"
        }
    }

}


export const gameConfig = {
    type: Phaser.AUTO,
    width: 360 * scaleRatio,
    height: 480 * scaleRatio,
    canvasStyle: `width: 360px;height:480px`,
    parent: 'playable-container',
    disableContextMenu: true,
    transparent: true,

};


export const ChengyuCrossPlayable = defineComponent({
    name: "ChengyuCrossPlayable",
    props: {
        config: { type: Object as PropType<ChengyuCrossConfig>, required: true },
        level: { type: Object as PropType<LevelInfo>, required: true }
    },
    emits: {
        succeed: (played: PlayableResult) => { return true },
        failed: (played: PlayableResult) => { return true },
        played: (args: any) => { return true}
    },
    data() {
        return {
            gameConfig: gameConfig
        }
    },
    methods: {
        apply(name: string) {
            const scene = this.$options.game.scene.getScene("ChengyuCrossScene") as ChengyuCrossScene
            return scene.apply(name)
        },

        canApply(name: string){
            const scene = this.$options.game.scene.getScene("ChengyuCrossScene") as ChengyuCrossScene
            return scene.canApply(name)
        },

        createGame() {
            const game = new Phaser.Game({...this.gameConfig})
            this.$options.game = game
            game.scene.add('ChengyuCrossScene', new ChengyuCrossScene(this.config, this.level, (played: PlayableResult)=>{
                if(played.succeed){
                    this.$emit("succeed", played)
                }else {
                    this.$emit("failed", played)
                }
            }, (name:string, args:any) => {
                if(name === 'played'){
                    this.$emit("played", args)
                }
            }), true);
        },

        destoryGame() {
            if (this.$options.game) {
                this.$options.game.destroy(true)
                this.$options.game = undefined
            }
        }
    },
    watch: {
        config(newConfig, oldConfig) {
            this.destoryGame()
            this.createGame()
        }
    },
    mounted() {
        this.destoryGame()
        this.createGame()
    },
    beforeUnmount() {
        this.destoryGame()
    },
    render() {
        return h('div', { "id": "playable-container" })
    }
})

export default ChengyuCrossPlayable;