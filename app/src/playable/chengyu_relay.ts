import * as Phaser from 'phaser';
import { defineComponent, h, PropType } from 'vue'
import { ApplyResponse, ConditionResponse, LevelInfo, PlayableResult } from './defines';

var scaleRatio = window.devicePixelRatio
const assetRatio = 4
const assetScale = scaleRatio / assetRatio

const fontFamily = '"Droid Sans", "PingFangSC-Regular", "Microsoft YaHei", sans-serif'


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

export interface ChengyuRelayConfig {
    start_letter?: string
}

function randomSlotId(): string {
    return randomString(6, "abcdefghijklmnopqrstuvwxyz")
}

interface ChengyuItem {
    texts: Array<Phaser.GameObjects.Text | undefined>
    backs: Array<Phaser.GameObjects.Shape | undefined>
    chengyu: string
}

export interface TextItem {
    text: Phaser.GameObjects.Text
    letter: string,
    x: number,
    y: number,
    slot_id: string,
    prev_slot_id: string | undefined
}

export interface TextSlot {
    slot_id: string,
    item: TextItem | undefined
    movable: boolean,
    back: Phaser.GameObjects.Shape | undefined,
    input_hint: Phaser.GameObjects.Shape | undefined,
    x: number,
    y: number
}

export class PreloadScene extends Phaser.Scene {
    public preload(): void {
        this.load.image("loader", "/assets/common/loader.png")
    }

    public create(data: any): void {
        this.scene.start("ChengyuRelayScene")
    }

}

export class ChengyuRelayScene extends Phaser.Scene {
    config: ChengyuRelayConfig
    level_info: LevelInfo
    chengyu_list: string[]
    won: boolean
    notify_cb: Function
    report_played: boolean
    emitter_cb: Function
    start_letters: string[]
    chengyu_dict: Record<string, string[]>

    current_start: string
    current_chengyu: string[]
    hint_group: Phaser.GameObjects.Group | undefined
    current: TextSlot | undefined
    candidate_slots: Array<TextSlot>
    slots: Array<TextSlot>
    relayed_items: Array<ChengyuItem>

    constructor(config: ChengyuRelayConfig, level: LevelInfo, callback: Function, emitter: Function) {
        super('ChengyuRelayScene');
        this.config = config;
        this.chengyu_list = new Array();
        this.chengyu_dict = {}
        this.start_letters = []
        this.won = false
        this.level_info = level
        this.notify_cb = callback ?? (() => {})
        this.report_played = true
        this.emitter_cb = emitter ?? (() => {})
        this.current_start = ""
        if(this.config.start_letter){
            this.current_start = this.config.start_letter
        }
        this.current_chengyu = []
        this.candidate_slots = []
        this.slots = []
        this.relayed_items = []
        this.current = undefined
        this.hint_group = undefined
    }

    public preload() {
        const loader = this.add.sprite(180*scaleRatio, 240*scaleRatio, "loader")
        loader.setScale(assetScale)
        this.tweens.add({
            targets:[loader],
            duration: 1200,
            props: {
                angle: "+=360"
            },
            repeat:-1
        })

        this.load.on('complete', function () {
            loader.destroy();
        });

        this.load.json('chengyu', 'assets/chengyu_relay/chengyu.json')
        this.load.image('dragon_scales', 'assets/chengyu_relay/dragon_scales_160_black.jpg')
    }

    chengyuList() {
        return this.cache.json.get('chengyu')['chengyu-all']
    }

    randomLetters(start: string){
        let start_letter = start
        if(!start_letter){
            start_letter = this.start_letters[Math.floor(Math.random()*this.start_letters.length)]
        }

        if(!(start_letter in this.chengyu_dict)){
            return {start: start_letter, chengyu: [], candidates:[]}
        }

        const candidate_chengyu = shuffle([...this.chengyu_dict[start_letter]]).slice(0, 6)
        const candidate_chengyu_others = []
        const chengyu_list: string[] = []
        const candidate_letters:string[] = []

        if(candidate_chengyu.length < 6){
            const n =  6 - candidate_chengyu.length
            for(let j = 0; j< n;){
                const idx = Math.floor(Math.random()*4000)
                const chengyu_selected = this.chengyu_list[idx]
                if(!candidate_chengyu.includes(chengyu_selected)){
                    candidate_chengyu_others.push(chengyu_selected)
                    j += 1
                }
            }
        }
        for(const chengyu of candidate_chengyu){
            chengyu_list.push(chengyu)
            for(let j = 0; j<3; j++){
                candidate_letters.push(chengyu[j+1])
            }
        }
        for(const chengyu of candidate_chengyu_others){
            for(let j = 0; j<3; j++){
                candidate_letters.push(chengyu[j+1])
            }
        }

        shuffle(candidate_letters)
        // console.log(chengyu_list)
        return {start: start_letter, chengyu: chengyu_list, candidates:candidate_letters}
    }

    initChengyuLetters(){
        const letter_freq: Record<string, number> = {}
        this.chengyu_list = this.chengyuList().slice(0, 8000)
        for(const chengyu of this.chengyu_list){
            const letter  = chengyu[0]
            if(letter in letter_freq){
                letter_freq[letter] += 1
            } else {
                letter_freq[letter] = 1
            }
            if(!(letter in this.chengyu_dict)){
                this.chengyu_dict[letter] = []
            }
            this.chengyu_dict[letter].push(chengyu)
        }

        const letters = Object.entries(letter_freq)
            .filter((value:[string, number]) => (value[1] >= 7))
            .sort((first:[string, number], second:[string, number]) => ( second[1] - first[1]))

        this.start_letters = letters.map((value:[string, number]) => (value[0]))
    }

    createRelayed(){
        const dragon_scales_texture = this.textures.get('dragon_scales')
        const texture_width = dragon_scales_texture.get().width * assetScale

        for(const item_y of [60*scaleRatio, 120*scaleRatio]){
            const n = Math.ceil(360*scaleRatio/texture_width)

            for(let i = 0; i< n; i++){
                const x = texture_width/2 + i * texture_width;
                const dragon_scale = this.add.image(x, item_y,'dragon_scales')
                dragon_scale.setScale(assetScale)
                dragon_scale.setAlpha(0.3)
            }
        }


        for(const item_y of [40*scaleRatio, 80*scaleRatio, 100*scaleRatio, 140*scaleRatio]){
            const l1 = this.add.rectangle(180*scaleRatio, item_y, 360*scaleRatio, 1*scaleRatio)
            l1.setFillStyle(0x000000, 0.5)
        }

    }

    createMain(start: string){
        const start_x = (360- 3*72)/2
        for(let i=0; i<4; i++){
            const item_x = (start_x + i*72)*scaleRatio
            const item_y = 220*scaleRatio
            const r = this.add.rectangle(item_x, item_y, 64*scaleRatio, 64*scaleRatio)
            r.setStrokeStyle(2*scaleRatio, 0x000000, 0.3)
            r.setOrigin(0.5, 0.5)

            const h = this.add.rectangle(item_x, item_y + 25*scaleRatio, 50*scaleRatio, 4*scaleRatio)
            h.setFillStyle(0xaaaaaa, 0)
            h.setOrigin(0.5, 0.5)

            const slot_id = randomSlotId()
            let item  = undefined
            let movable = true
            if(i == 0){
                const text = this.add.text(item_x, item_y, start,
                    {
                        fontSize: `${48*scaleRatio}px`,
                        fontStyle: "normal",
                        fontFamily: fontFamily,
                        color: "#000000"
                    })
                text.setOrigin(0.5, 0.5)
                item = {
                    text: text,
                    letter: start,
                    x: item_x,
                    y: item_y,
                    slot_id: slot_id,
                    prev_slot_id: undefined
                }
                movable = false
            }

            const slot = {
                slot_id: slot_id,
                item: item,
                movable: movable,
                back: r,
                input_hint: h,
                x: item_x,
                y: item_y,
            }

            if(movable){
                r.setInteractive(new Phaser.Geom.Rectangle(0*scaleRatio, 0*scaleRatio,
                    64*scaleRatio, 64*scaleRatio), Phaser.Geom.Rectangle.Contains)
                r.on("pointerdown", () => {
                    this.setCurrent(slot)
                })
            }
            this.slots.push(slot)
        }
    }

    createCandidates(candidates: string[]) {
        const start_x = (360-(5*44) - 40)/2 + 20
        const bg = this.add.rectangle(180*scaleRatio, 390*scaleRatio, 360*scaleRatio, 180*scaleRatio)
        bg.setFillStyle(0xf0f0f0, 1)
        const bgtop = this.add.rectangle(180*scaleRatio, 300*scaleRatio, 360*scaleRatio, 1*scaleRatio)
        bgtop.setFillStyle(0xcccccc, 1)
        const columns = Math.ceil(candidates.length/3)
        const y_space = (180-40*3-4*2)/2
        for(let i=0; i<3; i++){
            for(let j = 0; j<columns; j++){
                const item_x = (start_x + j*44)*scaleRatio
                const item_y = (300 + y_space + 22 + 44*i)*scaleRatio
                const r = this.add.rectangle(item_x, item_y, 40*scaleRatio, 40*scaleRatio)
                const idx = columns*i+j
                const even_tile = ((j+i) % 2 === 1)
                const letter = candidates[idx]
                r.setStrokeStyle(1*scaleRatio, 0x000000, 0.5)
                if(even_tile){
                    r.setFillStyle(0xcccccc)
                }
                r.setOrigin(0.5, 0.5)
                const text = this.add.text(item_x, item_y, letter,
                    {
                        fontSize: `${48*scaleRatio}px`,
                        fontStyle: "normal",
                        fontFamily: fontFamily,
                        color: "#000000"
                    })
                text.setOrigin(0.5, 0.5)
                text.setScale(0.65)
                text.setInteractive(new Phaser.Geom.Rectangle(-6*scaleRatio, -6*scaleRatio,
                    60*scaleRatio, 60*scaleRatio), Phaser.Geom.Rectangle.Contains)

                const slot_id = randomSlotId()
                const item = {
                    text: text,
                    letter: letter,
                    x: item_x,
                    y: item_y,
                    slot_id: slot_id,
                    prev_slot_id: undefined
                }
                this.candidate_slots.push({
                    slot_id: slot_id,
                    item: item,
                    movable: true,
                    back: r,
                    input_hint: undefined,
                    x: item_x,
                    y: item_y,

                })

                text.on("pointerdown",  (_: any) => {
                    this.itemClicked(item)
                })
            }
        }
    }

    async closeHintGroup() {
        if(this.hint_group === undefined){
            return
        }
        await new Promise<void>((resolve, reject) => {
            if(this.hint_group){
                this.tweens.add({
                    targets: [...this.hint_group?.getChildren()],
                    duration: 300,
                    props: {
                        alpha: 0
                    },
                    onComplete: () => {
                        this.hint_group?.destroy(true, true)
                        this.hint_group = undefined
                        resolve()
                    }
                })
            } else {
                resolve()
            }

        })
    }

    createHintGroup() {
        const hint_group = this.add.group()
        const bg = this.add.rectangle(180*scaleRatio, 390*scaleRatio, 360*scaleRatio, 180*scaleRatio)
        bg.setFillStyle(0xf0f0f0, 1)
        const bgtop = this.add.rectangle(180*scaleRatio, 300*scaleRatio, 360*scaleRatio, 1*scaleRatio)
        bgtop.setFillStyle(0xcccccc, 1)

        hint_group.add(bg)
        hint_group.add(bgtop)

        let x_offset = 180*scaleRatio
        let columns = 1
        const column_width = 144
        const column_space = (360 - column_width*2) / 3
        const row_space = (180-40*3-4*2)/2

        if(this.current_chengyu.length > 1){
            x_offset = ( column_space + column_width/2)*scaleRatio
            columns = 2
        }


        for(const [idx, chengyu] of this.current_chengyu.entries()){
            const row = Math.floor(idx/columns)
            const cloumn = idx % columns
            const item_x = x_offset + cloumn * (column_width + column_space)*scaleRatio
            const item_y = (300 + row_space + 22 + 44*row)*scaleRatio
            const r = this.add.rectangle(item_x, item_y, 144*scaleRatio, 36*scaleRatio)
            r.setStrokeStyle(1*scaleRatio, 0x000000, 0.8)
            const t = this.add.text(item_x, item_y, chengyu, {
                fontSize: `${24*scaleRatio}px`,
                fontStyle: "normal",
                fontFamily: fontFamily,
                color: "#000000"
            })
            r.setInteractive(new Phaser.Geom.Rectangle(0*scaleRatio, 0*scaleRatio,
                144*scaleRatio, 36*scaleRatio), Phaser.Geom.Rectangle.Contains)
             .on("pointerdown", ()=>{
                this.closeHintGroup().then(() => {
                    this.inputCorrectChengyu(chengyu)
                })

            })
            t.setOrigin(0.5, 0.5)
            hint_group.add(r)
            hint_group.add(t)
        }

        this.hint_group = hint_group
    }

    public create(data:any){
        this.initChengyuLetters()
        const letters = this.randomLetters(this.current_start)
        this.current_start = letters.start
        this.current_chengyu = letters.chengyu

        this.createRelayed()
        this.createMain(letters.start)
        this.createCandidates(letters.candidates)

        const slot = this.firstMainBlankSlot()

        if(slot){
            this.setCurrent(slot)
        }

    }

    firstMainBlankSlot() {
        const blank_slots = this.slots.filter((slot) => (slot.item === undefined))
        if (blank_slots.length > 0) {
            return blank_slots[0]
        }
        return undefined
    }

    getMainSlot(slot_id: string) {
        const slots = this.slots.filter((slot) => (slot.slot_id === slot_id))
        if (slots.length > 0) {
            return slots[0]
        }
        return undefined
    }

    getCandidateSlot(slot_id: string) {
        const slots = this.candidate_slots.filter((slot) => (slot.slot_id === slot_id))
        if (slots.length > 0) {
            return slots[0]
        }
        return undefined
    }

    getCandidateSlotByLetter(letter: string) {
        const slots = this.candidate_slots.filter((slot) => (slot.item && slot.item.letter === letter))
        if (slots.length > 0) {
            return slots[0]
        }
        return undefined
    }

    public setCurrent(slot: TextSlot) {
        if(this.current?.slot_id === slot.slot_id){
            return
        }
        if(this.current !== undefined && this.current.input_hint){
            const tweens = this.tweens.getTweensOf(this.current.input_hint, true)
            for(const task of tweens){
                task.stop()
                task.remove()
            }
        }
        if(slot.item !== undefined){
            return
        }
        if(slot.input_hint){
            this.current = slot
            this.add.tween({
                targets:[slot.input_hint],
                duration: 1000,
                props:{
                    fillAlpha: 1,
                },
                ease: "Sine.easeInOut",
                repeat: -1,
                yoyo:true,
                onStop: () => {
                    if(slot.input_hint){
                        slot.input_hint.setFillStyle(0xaaaaaa, 0)
                    }
                }
            })
        }

    }

    public clearCurrent() {
        if(this.current !== undefined && this.current.input_hint){
            const tweens = this.tweens.getTweensOf(this.current.input_hint, true)
            for(const task of tweens){
                task.stop()
                task.remove()
            }
            this.current = undefined
        }
    }

    clearMain() {
        for(const slot of this.slots){
            slot.item?.text.destroy()
            slot.item = undefined
            slot.back?.destroy()
            slot.back = undefined
        }
        this.slots.splice(0, this.slots.length)
    }

    clearCandidates() {
        for(const slot of this.candidate_slots){
            slot.item?.text.destroy()
            slot.item = undefined
            slot.back?.destroy()
            slot.back = undefined
        }
        this.candidate_slots.splice(0, this.candidate_slots.length)
    }

    moveCurrent() {
        let slot = undefined
        const current = this.current
        if(current){
            let index = this.slots.indexOf(current)
            if(index < 0){
                index = 0
            }
            let slots = this.slots.slice(index+1)
            if(slots.length > 0){
                slot = slots[0]
            } else {
                slot = this.firstMainBlankSlot()
            }
        } else {
            slot = this.firstMainBlankSlot()
        }

        if(slot){
            this.setCurrent(slot)
        } else {
            this.clearCurrent()
        }
    }

    async next(chengyu:string) {
        const start = chengyu[chengyu.length - 1]
        const letters = this.randomLetters(start)

        this.clearCandidates()
        const texts = []
        const backs = []
        for(const slot of this.slots){
            if(slot.item){
                slot.item.text.disableInteractive()
                texts.push(slot.item.text)
                backs.push(slot.back)
                slot.back?.setStrokeStyle(1, 0x000000, 0.4)
                slot.back?.setFillStyle(0x008000)
                slot.item.text.setFill('#ffffff')
            }
            slot.item = undefined
        }
        this.relayed_items.push({
            texts: texts,
            backs: backs,
            chengyu: chengyu
        })
        this.slots.splice(0, this.slots.length)
        await this.renderRelayed()

        if(letters.chengyu.length == 0){
            this.gameOver()
            return
        }
        this.current_start = letters.start
        this.current_chengyu  = letters.chengyu
        this.createMain(letters.start)
        this.createCandidates(letters.candidates)
        this.moveCurrent()
    }

    async renderRelayed() {
        let rerendered_items = this.relayed_items
        if( rerendered_items.length > 7){
            rerendered_items = this.relayed_items.slice(this.relayed_items.length - 7)
        }
        const total_n = rerendered_items.length

        const moves = []

        for(const [idx, item] of rerendered_items.entries()){
            const revert_idx = total_n - idx
            const row = 0
            let row_idx = 3 - revert_idx
            if(revert_idx > 3){
                row_idx = 3 - (revert_idx - 3)
            }
            const space = (360-3*107)/4
            let item_x = ((space + 107)*row_idx + space + 13)*scaleRatio
            let item_y = 120*scaleRatio
            if(revert_idx >= 4){
                item_y = 60*scaleRatio
            }
            for(const [idx2, text] of item.texts.entries()){
                if(text){
                    const back = item.backs[idx2]
                    moves.push(new Promise<void>((resolve, reject) => {
                        this.add.tween({
                            targets:[text, back],
                            duration: 300,
                            delay: idx*30,
                            props:{
                                x: item_x + 27*idx2*scaleRatio,
                                y: item_y,
                                scale: 0.4
                            },
                            ease: "Sine.easeInOut",
                            onComplete: () => {
                                resolve()
                            }
                        })
                    }))
                }
            }
        }

        await Promise.all(moves)
    }

    async showWrong(): Promise<void> {
        // const filled_slots = this.slots.filter((slot) => (slot.movable === true))
        const shakes = []
        for (const slot of this.slots) {
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
                        resolve()
                    }
                })
            }))
        }
        await Promise.all(shakes)
    }

    getRelayedChengyu() {
        const chengyu_list = []
        for(const item of this.relayed_items){
            chengyu_list.push({
                "type": "item",
                "name": "chengyu_relay.chengyu_simple",
                "idiom": item.chengyu
            })
        }
        return chengyu_list
    }

    async gameOver(): Promise<void> {
        this.won = true
        this.current_start = ""
        this.current_chengyu = []
        this.notify_cb({
            succeed: true,
            archievement: {
                rating: 3
            },
            level: this.level_info,
            items: this.getRelayedChengyu()
        })
    }

    validateState() {
        const filled_slots = this.slots.filter((slot) => ( slot.item !== undefined && slot.item.slot_id === slot.slot_id))
        if (filled_slots.length != this.slots.length) {
            return
        }
        const letters = this.slots.map((slot) => (slot.item?.letter))

        const chengyu = letters.join('')

        if(this.chengyu_list.includes(chengyu)){
            this.next(chengyu)
        } else {
            this.showWrong()
        }
    }

    async moveItem(item: TextItem, scale: number): Promise<void> {
        //item.text.setPosition(item.x, item.y)
        const move = new Promise<void>((resolve, reject) => {
            this.tweens.add({
                targets: [item.text],
                duration: 300,
                props: {
                    x: item.x,
                    y: item.y,
                    scale: scale
                },
                ease: "Sine.easeOut",
                onComplete: () => {
                    resolve()
                }
            })
        })
        await move;
    }

    async flyBack(item:TextItem){
        if(!item.prev_slot_id){
            return
        }
        const target_slot = this.getCandidateSlot(item.prev_slot_id)
        if (!target_slot) {
            return
        }
        const slot = this.getMainSlot(item.slot_id)
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
            this.moveItem(item, 0.65).then(() => {
                item.slot_id = target_slot.slot_id
                resolve()
            })
        })
    }

    async flyToMain(item:TextItem){
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
        slot.item = undefined
        target_slot.item = item
        item.x = target_slot.x
        item.y = target_slot.y
        item.prev_slot_id = item.slot_id
        item.slot_id = ""
        await new Promise<void>((resolve, reject) => {
            this.moveItem(item, 1).then(() => {
                item.slot_id = target_slot.slot_id
                resolve()
            })
        })
    }

    itemClicked(item: TextItem) {
        // console.log('itemClicked', item)
        if (this.won) {
            return
        }
        if(this.report_played){
            this.emitter_cb('played', {})
            this.report_played = false
        }
        if (item.prev_slot_id) {
            //move back to candidates
            const slot = this.getMainSlot(item.slot_id)
            if (!slot) {
                return
            }
            this.flyBack(item)
            this.setCurrent(slot)
        } else {
            this.flyToMain(item).then(() => {
                this.validateState()
            })
            this.moveCurrent()
        }

    }

    async inputCorrectChengyu(chengyu: string){
        for(const [idx, slot] of this.slots.entries()){
            if(slot.movable === false || slot.item === undefined){
                continue
            }

            if(slot.item.letter !== chengyu[idx]){
                await this.flyBack(slot.item)
            }
        }
        this.moveCurrent()
        for(const [idx, slot] of this.slots.entries()){
            if(slot.movable === false || slot.item !== undefined){
                continue
            }

            const letter = chengyu[idx]
            const right_slot = this.getCandidateSlotByLetter(letter)
            if(right_slot && right_slot.item){
                this.setCurrent(slot)
                await this.flyToMain(right_slot.item)

            }
        }
        this.moveCurrent()
        this.validateState()
    }

    async inputCorrect() {
        this.createHintGroup()
    }

    async rollBack() {
        if(this.won){
            this.won = false
        }
        const last_item = this.relayed_items.pop()
        if(!last_item){
            return
        }


        this.clearCandidates()
        this.clearMain()

        const move_backs = []
        const start_x = (360- 3*72)/2
        for(const [idx, back] of last_item.backs.entries()){
            const item_x = (start_x + idx*72)*scaleRatio
            const item_y = 220*scaleRatio
            const text = last_item.texts[idx]
            back?.setStrokeStyle(1, 0x000000, 0.4)
            back?.setFillStyle(0xffffff)
            text?.setFill('#000000')
            move_backs.push(new Promise<void>((resolve, reject) => {
                this.tweens.add({
                    targets: [back, text],
                    duration: 300,
                    ease: "Sine.easeInOut",
                    props: {
                        x: item_x,
                        y: item_y,
                        scale: 1,
                    },
                    onComplete: () => {
                        resolve()
                    }
                })
            }))
        }

        await Promise.all(move_backs)

        await this.renderRelayed()

        await new Promise<void>((resolve, reject) => {
            this.tweens.add({
                targets: [...last_item.backs.slice(1), ...last_item.texts.splice(1)],
                duration: 300,
                ease: "Sine.easeInOut",
                props: {
                    alpha: 0
                },
                onComplete: () => {
                    for(const back of last_item.backs){
                        back?.destroy()
                    }
                    for(const text of last_item.texts){
                        text?.destroy()
                    }
                    last_item.backs = []
                    last_item.texts = []
                    resolve()
                }
            })
        })

        const start = last_item?.chengyu[0]
        const letters = this.randomLetters(start)

        if(letters.chengyu.length == 0){
            this.gameOver()
            return
        }
        this.current_start = letters.start
        this.current_chengyu  = letters.chengyu
        this.createMain(letters.start)
        this.createCandidates(letters.candidates)
        this.moveCurrent()
    }

    apply(name: string) {
        if (name === 'correct_one') {
            if (this.chengyu_list.length === 0) {
                return {
                    ok: false,
                    message: "没有需要填写的成语"
                }
            }

            this.inputCorrect()

            return {
                ok:true,
                message: "已经提示了"
            }
        } else if (name === 'roll_back'){
            if (this.relayed_items.length === 0){
                return {
                    ok: false,
                    message: "不能再回退了"
                }
            }

            this.rollBack()
            this.won = false

            return {
                ok:true,
                message: "已经回退了"
            }
        }

        return {
            ok: false,
            message: "这个功能暂时还支持不了"
        }
    }

    canApply(name: string): ConditionResponse{
        let can = false
        if (name === 'correct_one') {
            if(this.won){
                return {
                    ok: false,
                    message: "没有效果"
                }
            }
            return { ok:true }
        } else if (name === 'roll_back'){
            can = (this.relayed_items.length > 0)
            if(can){
                return {
                    ok:true,
                }
            } else {
                return {
                    ok: false,
                    message: "不能再回退了"
                }
            }
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
    disableContextMenu: true,
    transparent: true,

};


export const ChengyuRelayPlayable = defineComponent({
    name: "ChengyuRelayPlayable",
    props: {
        config: { type: Object as PropType<ChengyuRelayConfig>, required: true },
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
            const scene = this.$options.game.scene.getScene("ChengyuRelayScene") as ChengyuRelayScene
            return scene.apply(name)
        },

        canApply(name: string){
            const scene = this.$options.game.scene.getScene("ChengyuRelayScene") as ChengyuRelayScene
            return scene.canApply(name)
        },

        createGame() {
            const game = new Phaser.Game({...this.gameConfig})
            this.$options.game = game

            game.scene.add('ChengyuRelayScene', new ChengyuRelayScene(this.config, this.level, (played: PlayableResult)=>{
                if(played.succeed){
                    this.$emit("succeed", played)
                }else {
                    this.$emit("failed", played)
                }
            }, (name:string, args:any) => {
                if(name === 'played'){
                    this.$emit("played", args)
                }
            }), false);
            game.scene.add('PreloadScene', new PreloadScene("PreloadScene"), true)
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

export default ChengyuRelayPlayable;
