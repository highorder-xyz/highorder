import * as Phaser from 'phaser';
import { defineComponent, h, PropType } from 'vue'
import { ApplyResponse, ConditionResponse, LevelInfo, PlayableResult } from './defines';

const scaleRatio = window.devicePixelRatio;
const assetRatio = 4
const assetScale = scaleRatio / assetRatio

export interface ShiciLetter {
    blank: boolean,
    letter: string
}

export interface ShiciBlankConfig {
    line1: Array<string | ShiciLetter>
    line2: Array<string | ShiciLetter>
    candidates: Array<String>,
    author?: string,
    title?: string,
    description?: string
}

export interface TextItem {
    text: Phaser.GameObjects.Text
    letter: string,
    x: number,
    y: number,
    slot_id: string,
    prev_slot_id: string | undefined
}

export interface TextBlank {
    letter: string,
}

export interface TextSlot {
    slot_id: string,
    item: TextItem | undefined
    movable: boolean,
    blank: TextBlank | undefined,
    back: Phaser.GameObjects.Shape | undefined,
    input_hint: Phaser.GameObjects.Shape | undefined,
    x: number,
    y: number
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


function randomSlotId(): string {
    return randomString(6, "abcdefghijklmnopqrstuvwxyz")
}

const fontFamily = '"Droid Sans", "PingFangSC-Regular", "Microsoft YaHei", sans-serif'

export class ShiciBlankScene extends Phaser.Scene {
    config: ShiciBlankConfig
    line1: Array<TextSlot>
    line2: Array<TextSlot>
    lines: Array<TextSlot>
    candidates: Array<TextSlot>
    current: TextSlot | undefined
    won: boolean
    lost: boolean
    level_info: LevelInfo
    notify_cb: Function
    report_played: boolean
    emitter_cb: Function
    shici_item: object

    constructor(config: ShiciBlankConfig, level:LevelInfo, callback: Function, emitter:Function) {
        super('ShiciBlankScene');
        this.config = config;
        this.line1 = new Array();
        this.line2 = new Array();
        this.lines = new Array();
        this.candidates = new Array();
        this.current = undefined
        this.won = false
        this.lost = false
        this.level_info = level
        this.notify_cb = callback
        this.report_played = true
        this.emitter_cb = emitter ?? (() => {})

        const lines: string[] = []
        for(const line of [config.line1, config.line2]){
            lines.push(
                line.map((it) => {
                    if (typeof it === 'object' && it !== null) {
                        const obj = it as ShiciLetter;
                        return obj.letter
                    } else {
                        return it as string;
                    }
                }).join('')
            )
        }

        this.shici_item = {
            type: "item",
            name: "shici_blank.shici",
            title: config.title ?? "",
            author: config.author ?? "",
            description: config.description ?? "",
            lines: lines
        }
    }

    public preload(): void {
    }

    public createLine(config_line: Array<string | ShiciLetter>, text_line: Array<TextSlot>,
        start_x: number, start_y: number) {
        for (const [idx, item] of config_line.entries()) {
            let letter: string = ""
            let blank_letter: string = ""
            if (typeof item === 'object' && item !== null) {
                const obj = item as ShiciLetter;
                if (!obj.blank) {
                    letter = obj.letter
                } else {
                    blank_letter = obj.letter
                }
            } else {
                letter = item as string;
            }
            const slot_id = randomSlotId()
            const item_x = (start_x + idx * 44 + 20)*scaleRatio
            const item_y = start_y * scaleRatio
            if (letter.length === 0) {
                const r = this.add.rectangle(item_x, item_y, 40*scaleRatio, 40*scaleRatio)
                r.setStrokeStyle(1*scaleRatio, 0x000000, 0.4)
                r.setOrigin(0.5, 0.5)

                const h = this.add.rectangle(item_x, item_y + 14*scaleRatio, 28*scaleRatio, 3*scaleRatio)
                h.setFillStyle(0xaaaaaa, 0)
                h.setOrigin(0.5, 0.5)

                const slot = {
                    slot_id: slot_id,
                    item: undefined,
                    movable: true,
                    blank: {
                        letter: blank_letter
                    },
                    back: r,
                    input_hint: h,
                    x: item_x,
                    y: item_y
                }
                text_line.push(slot)
                r.setInteractive(new Phaser.Geom.Rectangle(0*scaleRatio, 0*scaleRatio,
                        40*scaleRatio, 40*scaleRatio), Phaser.Geom.Rectangle.Contains)
                r.on("pointerdown", () => {
                    this.setCurrent(slot)
                })

            } else {
                const text = this.add.text(item_x, item_y, letter,
                    {
                        fontSize: `${32*scaleRatio}px`,
                        fontStyle: "normal",
                        fontFamily: fontFamily,
                        color: "#000000"
                    })
                text.setOrigin(0.5, 0.5)
                text_line.push({
                    slot_id: slot_id,
                    item: {
                        text: text,
                        letter: letter,
                        x: item_x,
                        y: item_y,
                        slot_id: slot_id,
                        prev_slot_id: undefined
                    },
                    movable: false,
                    blank: undefined,
                    back: undefined,
                    input_hint: undefined,
                    x: item_x,
                    y: item_y
                })
            }

        }
    }

    public create(data: any): void {
        const line1_count = this.config.line1.length;
        const line1_length = line1_count * 40 + (line1_count - 1) * 4
        const start_x1 = (360 - line1_length) / 2
        this.createLine(this.config.line1, this.lines, start_x1, 90)
        const line2_count = this.config.line2.length;
        const line2_length = line2_count * 40 + (line2_count - 1) * 4
        const start_x2 = (360 - line2_length) / 2
        this.createLine(this.config.line2, this.lines, start_x2, 150)

        const lines = [...this.config.line1, ...this.config.line2]
        const candidate_letters = [...this.config.candidates]

        for(const item of lines){
            if (typeof item === 'object' && item !== null) {
                const obj = item as ShiciLetter;
                if (obj.blank) {
                    const letter = obj.letter
                    candidate_letters.push(letter)
                }
            }
        }

        shuffle(candidate_letters)

        const row_count = Math.ceil(candidate_letters.length / 4)


        const bg = this.add.rectangle(180*scaleRatio, 360*scaleRatio, 360*scaleRatio, 240*scaleRatio)
        bg.setFillStyle(0xf0f0f0, 1)

        const bgtop = this.add.rectangle(180*scaleRatio, 240*scaleRatio, 360*scaleRatio, 1*scaleRatio)
        bgtop.setFillStyle(0xcccccc, 1)

        for (const [idx, item] of candidate_letters.entries()) {
            let letter: string = item as string;
            const row = Math.floor(idx / 4)
            const row_idx = idx % 4
            const even_tile = ((row + row_idx) % 2 === 1)
            const h = (240 - row_count*40 - (row_count-1)*4)/2
            const start_y = 240 + row * 44 + 20 + h
            const start_x = (360 - 4 * 40 - 3 * 4) / 2
            const slot_id = randomSlotId()

            const item_x = (start_x + row_idx * 44 + 20)*scaleRatio
            const item_y = start_y * scaleRatio
            const r = this.add.rectangle(item_x, item_y, 40*scaleRatio, 40*scaleRatio)
            r.setStrokeStyle(1*scaleRatio, 0x000000, 0.4);
            if(even_tile){
                r.setFillStyle(0xcccccc)
            }
            r.setOrigin(0.5, 0.5)

            const text = this.add.text(item_x, item_y, letter,
                {
                    fontSize: `${32*scaleRatio}px`,
                    fontStyle: "normal",
                    fontFamily: fontFamily,
                    color: "#000000"
                })
            text.setOrigin(0.5, 0.5)

            text.setInteractive(new Phaser.Geom.Rectangle(-4*scaleRatio, -4*scaleRatio, 40*scaleRatio, 40*scaleRatio), Phaser.Geom.Rectangle.Contains)

            const text_item = {
                text: text,
                letter: letter,
                x: item_x,
                y: item_y,
                slot_id: slot_id,
                prev_slot_id: undefined
            }

            text.on('pointerdown', (_: any) => {
                this.itemClicked(text_item)
            })

            this.candidates.push({
                slot_id: slot_id,
                item: text_item,
                movable: true,
                blank: undefined,
                back: r,
                input_hint: undefined,
                x: item_x,
                y: item_y
            })

        }
        this.moveNext()
    }

    firstBlankSlot() {
        const blank_slots = this.lines.filter((slot) => (slot.item === undefined))
        if (blank_slots.length > 0) {
            return blank_slots[0]
        }
        return undefined
    }

    getLineSlot(slot_id: string) {
        const slots = this.lines.filter((slot) => (slot.slot_id === slot_id))
        if (slots.length > 0) {
            return slots[0]
        }
        return undefined
    }

    getCandidateSlot(slot_id: string) {
        const slots = this.candidates.filter((slot) => (slot.slot_id === slot_id))
        if (slots.length > 0) {
            return slots[0]
        }
        return undefined
    }

    getCandidateSlotByLetter(letter: string){
        const slots = this.candidates.filter((slot) => (slot.item?.letter === letter))
        if (slots.length > 0) {
            return slots[0]
        }
        return undefined
    }

    public moveNext() {
        const current = this.current
        let next_slot = undefined
        if(current){
            const idx = this.lines.indexOf(current)
            const slots_left = this.lines.slice(idx+1).filter((slot) => (slot.movable === true && slot.item === undefined))
            if(slots_left.length > 0){
                next_slot = slots_left[0]
            } else {
                const slots_left = this.lines.slice(0, idx).filter((slot) => (slot.movable === true && slot.item === undefined))
                if(slots_left.length > 0){
                    next_slot = slots_left[0]
                }
            }
        } else {
            next_slot = this.firstBlankSlot()
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

    async moveItem(item: TextItem): Promise<void> {
        //item.text.setPosition(item.x, item.y)
        const move = new Promise<void>((resolve, reject) => {
            this.tweens.add({
                targets: [item.text],
                duration: 300,
                props: {
                    x: item.x,
                    y: item.y
                },
                ease: "Sine.easeOut",
                onComplete: () => {
                    resolve()
                }
            })
        })
        await move;
    }

    async showWon(): Promise<void> {
        const blank_slots = this.lines.filter((slot) => (slot.blank !== undefined))
        const animations = []
        for (const [idx, slot] of blank_slots.entries()) {
            slot.back?.setStrokeStyle(1, 0x000000, 0.4)
            slot.back?.setFillStyle(0x008000)
            slot.item?.text.setFill('#ffffff')
            animations.push(new Promise<void>((resolve, reject) => {
                this.tweens.add({
                    targets: [slot.back, slot.item?.text],
                    duration: 160,
                    props: {
                        y: `-= ${8*scaleRatio}`
                    },
                    delay: idx * 80,
                    yoyo: true,
                    ease: "Sine.easeOut",
                    onComplete: () => {
                        resolve()
                    }
                })
            }))
        }
        await Promise.all(animations)
        this.notify_cb({
            succeed: true,
            archievement: {
                rating:3
            },
            items: [
                this.shici_item
            ],
            level: this.level_info
        })
    }

    async showLost(): Promise<void> {
        const blank_slots = this.lines.filter((slot) => (slot.blank !== undefined))
        const shakes = []
        for (const slot of blank_slots) {
            const item = slot.item
            const text = slot.item?.text
            if (!item || !text) {
                continue
            }
            text.setX(slot.x - 4*scaleRatio)
            shakes.push(new Promise<void>((resolve, reject) => {
                this.tweens.add({
                    targets: [text],
                    duration: 50,
                    props: {
                        x: slot.x + 4*scaleRatio
                    },
                    yoyo: true,
                    repeat: 6,
                    onComplete: () => {
                        text.setX(slot.x)
                        slot.back?.setStrokeStyle(1*scaleRatio, 0x000000, 0.4)
                        slot.back?.setFillStyle(0x00, 0.6)
                        slot.item?.text.setFill('#ffffff')
                        resolve()
                    }
                })
            }))
        }
        await Promise.all(shakes)
        this.notify_cb({
            succeed: false,
            archievement: {
                rating:0
            },
            items: [
                this.shici_item
            ],
            level: this.level_info
        })
    }

    validateState() {
        const b_slot = this.firstBlankSlot()
        if (b_slot) {
            return
        }
        const blank_slots = this.lines.filter((slot) => (slot.blank !== undefined))
        const blank_item_slots = this.lines.filter((slot) => (slot.blank !== undefined && slot.item?.slot_id === slot.slot_id))

        if (blank_item_slots.length != blank_slots.length) {
            return
        }
        for (const slot of blank_slots) {
            if (slot.item === undefined || slot.blank === undefined) {
                return
            }
            if (slot.slot_id !== slot.item.slot_id) {
                return
            }
            if (slot.item.letter !== slot.blank.letter) {
                this.lost = true
                this.showLost()
                return
            }
        }
        this.won = true
        this.showWon()

    }

    async flyBack(item:TextItem){
        if(!item.prev_slot_id){
            return
        }
        const target_slot = this.getCandidateSlot(item.prev_slot_id)
        if (!target_slot) {
            return
        }
        const slot = this.getLineSlot(item.slot_id)
        if (!slot) {
            return
        }
        if (!slot.movable) {
            return
        }
        slot.item = undefined
        target_slot.item = item
        item.x = target_slot.x
        item.y = target_slot.y
        item.prev_slot_id = undefined
        item.slot_id = ""
        await new Promise<void>((resolve, reject) => {
            this.moveItem(item).then(() => {
                item.slot_id = target_slot.slot_id
                resolve()
            })
        })
    }

    async flyToBlank(slot: TextSlot, target_slot: TextSlot){
        if(!slot.item){
            return
        }
        const item = slot.item!
        slot.item = undefined
        target_slot.item = item
        item.x = target_slot.x
        item.y = target_slot.y
        item.prev_slot_id = item.slot_id
        item.slot_id = ""
        await this.moveItem(item)
        item.slot_id = target_slot.slot_id
    }

    itemClicked(item: TextItem) {
        if (this.won || this.lost) {
            return
        }
        if(this.report_played){
            this.emitter_cb('played', {})
            this.report_played = false
        }
        if (item.prev_slot_id) {
            //move back to candidates
            const slot = this.getLineSlot(item.slot_id)
            if (!slot) {
                return
            }
            this.flyBack(item)
            this.setCurrent(slot)
        } else {
            const target_slot = this.current
            if (!target_slot) {
                return
            }
            const slot = this.getCandidateSlot(item.slot_id)
            if (!slot) {
                return
            }
            if (!slot.movable) {
                return
            }
            this.flyToBlank(slot, target_slot).then(() => {
                this.validateState()
            })
            this.moveNext()
        }

    }

    async inputCorrect() {
        this.clearCurrentTweens()
        this.current = undefined
        const blank_slots = this.lines.filter((slot) => (slot.blank !== undefined))
        for (const slot of blank_slots) {
            const item = slot.item
            const letter = slot.blank!.letter
            if(item && item.letter !== letter){
                await this.flyBack(item)
            }
        }
        for (const slot of blank_slots) {
            const letter = slot.blank!.letter
            if(slot.item === undefined){
                const right_slot = this.getCandidateSlotByLetter(letter)
                if(right_slot){
                    await this.flyToBlank(right_slot, slot)
                }
            }
        }
        this.validateState()
    }

    apply(name: string) {
        if(this.won || this.lost){
            return {
                ok: false,
                message: `游戏已经结束了。`
            }
        }
        if (name === 'correct') {
            this.inputCorrect()
            return {
                ok: true,
                message: "已经重新打乱了"
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
        if (name === 'correct') {
            return { ok:true }
        }
        return {
            ok: false,
            message: "无法支持该动作"
        }
    }
}


export const gameConfig = {
    type: Phaser.AUTO,
    width: 360 * scaleRatio,
    height: 480 * scaleRatio,
    canvasStyle: `width: 360px;height:480px`,
    parent: 'playable-container',
    transparent: true,
    backgroundColor: '#ffffff',
    disableContextMenu: true
};


export const ShiciBlankPlayable = defineComponent({
    name: "ShiciBlankPlayable",
    props: {
        config: { type: Object as PropType<ShiciBlankConfig>, required: true },
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
            const scene = this.$options.game.scene.getScene("ShiciBlankScene") as ShiciBlankScene
            return scene.apply(name)

        },

        canApply(name: string){
            const scene = this.$options.game.scene.getScene("ShiciBlankScene") as ShiciBlankScene
            return scene.canApply(name)
        },

        createGame() {
            const game = new Phaser.Game({...this.gameConfig})
            this.$options.game = game
            game.scene.add('ShiciBlankScene', new ShiciBlankScene(this.config, this.level, (played: PlayableResult)=>{
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

export default ShiciBlankPlayable;
