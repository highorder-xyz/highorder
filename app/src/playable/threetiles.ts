import * as Phaser from 'phaser';
import { defineComponent, h, PropType } from 'vue'
import { ApplyResponse, ConditionResponse, LevelInfo, PlayableResult } from './defines';

const scaleRatio = window.devicePixelRatio
const assetRatio = 4
const assetScale = scaleRatio / assetRatio

const fontFamily = '"Droid Sans", "PingFangSC-Regular", "Microsoft YaHei", sans-serif'

export interface ThreeTilesConfig {
    tile_count: number,
    item_image_hrefs: string[],
    secret_image?: string,
    secret_message?: string,
    extra?: Record<string, any>,
    details?: Array<object>
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

class TileItem {
    name: string
    state: string
    tile_type: number
    xpos: number
    ypos: number
    x: number
    y: number
    depth: number
    scene: ThreeTilesScene
    group: Phaser.GameObjects.Group | undefined
    cover_indexes: number[] = []
    points: string[]
    sprite_scale: number = 1
    back_sprite!: Phaser.GameObjects.Sprite
    sprite!: Phaser.GameObjects.Sprite
    cover_sprite!: Phaser.GameObjects.Sprite
    in_slot: boolean
    tobe_remove: boolean

    constructor(tile_type: number, depth: number, state: string, scene: ThreeTilesScene, xpos: number, ypos: number) {
        this.depth = depth
        this.tile_type = tile_type
        this.name = `tile_${tile_type}`
        this.state = state ?? "active"
        this.scene = scene
        this.xpos = xpos
        this.ypos = ypos
        this.in_slot = false
        this.tobe_remove = false
        this.points = [`${xpos},${ypos}`, `${xpos + 1},${ypos}`, `${xpos},${ypos + 1}`, `${xpos + 1},${ypos + 1}`]
        this.x = (xpos * 30 + 45) * scaleRatio
        this.y = (ypos * 30 + 45) * scaleRatio

    }

    creatSprite() {
        if (this.group) {
            this.group.destroy(true)
            this.group = undefined
        }
        const init_x = 180*scaleRatio
        const init_y = 240*scaleRatio
        this.group = this.scene.add.group()
        const back = this.scene.add.sprite(init_x, init_y, "tile_back")
        back.setScale(assetScale)
        this.back_sprite = back
        this.group.add(back)

        const sprite_texture = this.scene.textures.get(this.name).get()
        let scale = 0.5
        if (sprite_texture.height > sprite_texture.width) {
            scale = 56 * scaleRatio / sprite_texture.height
        } else {
            scale = 56 * scaleRatio / sprite_texture.width
        }
        this.sprite_scale = scale


        const sprite = this.scene.make.sprite({
            x: init_x,
            y: init_y,
            key: this.name,
            scale : {
               x: scale,
               y: scale
            },
            add: true
        })
        this.sprite = sprite

        this.group.add(sprite)

        let cover_name = "tile_cover"
        if (this.state === 'unactive') {
            cover_name = "tile_cover_unactive"
        }

        const cover_sprite = this.scene.add.sprite(init_x, init_y, cover_name)
        cover_sprite.setScale(assetScale)
        this.cover_sprite = cover_sprite
        this.group.add(cover_sprite)

        this.group.setDepth(this.depth)
        // await new Promise<void>((resolve, reject) => {
            this.scene.tweens.add({
                targets: [this.back_sprite, this.sprite, this.cover_sprite],
                duration: 600,
                props:{
                    x: this.x,
                    y: this.y
                },
                ease: "Sine.easeInOut"
            })
        // })
        return this.group
    }

    setActive() {
        this.state = 'active'
        if (this.cover_sprite) {
            let cover_name = "tile_cover"
            this.cover_sprite.setTexture(cover_name)
        }
        this.back_sprite.setInteractive().on('pointerdown', (_: any) => {
            if (this.state === 'active') {
                this.scene.handleClick(this)
            }
        })

    }

    setUnActive() {
        if(this.state === 'active'){
            this.state = 'unactive'
            if (this.cover_sprite) {
                let cover_name = "tile_cover_unactive"
                this.cover_sprite.setTexture(cover_name)
            }
            this.back_sprite.disableInteractive()
        }
    }

    setPosition(xpos:number, ypos:number){
        this.xpos = xpos
        this.ypos = ypos
        this.points = [`${xpos},${ypos}`, `${xpos + 1},${ypos}`, `${xpos},${ypos + 1}`, `${xpos + 1},${ypos + 1}`]
        const x = (xpos * 30 + 45) * scaleRatio
        const y = (ypos * 30 + 45) * scaleRatio
        this.x = x
        this.y = y
    }

    async destroy(annimate:boolean = false): Promise<void> {
        if (this.group) {
            if(annimate){
                const group = this.group
                await new Promise<void>((resolve, reject) => {
                    this.scene.tweens.add({
                        targets: [this.back_sprite, this.sprite, this.cover_sprite],
                        duration: 180,
                        props:{
                            alpha: 0.2,
                            scale: "*=0.2"
                        },
                        ease: "Sine.easeInOut",
                        onComplete: () => {
                            group.destroy(true)
                            this.group = undefined
                            resolve()
                        }

                    })
                })
            } else {
                this.group.destroy(true)
                this.group = undefined
            }

        }
    }

    async moveToCenter(): Promise<void> {
        const init_x = 180*scaleRatio
        const init_y = 240*scaleRatio
        await new Promise<void>((resolve, reject) => {
            this.scene.tweens.add({
                targets: [this.back_sprite, this.sprite, this.cover_sprite],
                duration: 300,
                props:{
                    x: init_x,
                    y: init_y,
                },
                ease: "Sine.easeInOut",
                onComplete: () => {
                    resolve()
                }

            })
        })
    }

    async move(){
        await new Promise<void>((resolve, reject) => {
            this.scene.tweens.add({
                targets: [this.back_sprite, this.sprite, this.cover_sprite],
                duration: 600,
                props:{
                    x: this.x,
                    y: this.y,
                },
                ease: "Sine.easeInOut",
                onComplete: () => {
                    resolve()
                }

            })
        })
    }

    async moveBack(depth:number, animate: boolean = false): Promise<void>{
        this.tobe_remove = false
        const x = (this.xpos * 30 + 45) * scaleRatio
        const y = (this.ypos * 30 + 45) * scaleRatio
        this.in_slot = false
        if(animate && this.group){
            await new Promise<void>((resolve, reject) => {
                this.scene.tweens.add({
                    targets: [this.back_sprite, this.sprite, this.cover_sprite],
                    duration: 300,
                    props:{
                        x: x,
                        y: y,
                        scale: "/= 0.7"
                    },
                    ease: "Sine.easeInOut",
                    onComplete: () => {
                        this.x = x,
                        this.y = y
                        this.setDepth(depth)
                        this.back_sprite.setInteractive()
                        resolve()
                    }
                })
            })
        } else {
            this.x = x
            this.y = y
            this.setDepth(depth)
            this.group?.setXY(x, y)
        }

    }

    async moveToSlot(x: number, y: number, animate: boolean = false): Promise<void> {
        this.back_sprite.disableInteractive()
        if(this.x === x && this.y === y){
            return
        }
        if (animate && this.group){
            let scale: string = "*= 1"
            if(!this.in_slot){
                scale = "*= 0.7"
            }
            this.in_slot = true
            await new Promise<void>((resolve, reject) => {
                this.scene.tweens.add({
                    targets: [this.back_sprite, this.sprite, this.cover_sprite],
                    duration: 300,
                    props:{
                        x: x,
                        y: y,
                        scale: scale
                    },
                    ease: "Sine.easeInOut",
                    onComplete: () => {
                        this.x = x,
                        this.y = y
                        resolve()
                    }

                })
            })

        } else {
            this.x = x
            this.y = y
            this.in_slot = true
            this.group?.setXY(x, y)
        }

    }

    async moveInSlot(x: number, y: number, animate: boolean = false): Promise<void> {
        if(this.x === x && this.y === y){
            return
        }
        if (animate && this.group){
            await new Promise<void>((resolve, reject) => {
                this.scene.tweens.add({
                    targets: [this.back_sprite, this.sprite, this.cover_sprite],
                    duration: 300,
                    props:{
                        x: x,
                        y: y
                    },
                    ease: "Sine.easeInOut",
                    onComplete: () => {
                        this.x = x,
                        this.y = y
                        resolve()
                    }

                })
            })

        } else {
            this.x = x
            this.y = y
            this.group?.setXY(x, y)
        }

    }

    setDepth(depth: number){
        this.depth = depth
        this.group?.setDepth(depth)
    }
}

export class PreloadScene extends Phaser.Scene {
    public preload(): void {
        this.load.image("loader", "/assets/common/loader.png")
    }

    public create(data: any): void {
        this.scene.start("ThreeTilesScene")
    }

}

export class ThreeTilesScene extends Phaser.Scene {
    row_count: number
    column_count: number
    item_type_count: number
    item_image_hrefs: string[]
    items: (TileItem | undefined)[]
    item_details: Array<object>
    min_tile_count: number
    points_tiles: Record<string, number[]>
    secret_href: string | undefined
    secret_message: string | undefined | string[]
    secret_sprite: Phaser.GameObjects.Sprite | undefined
    secret_cover: Phaser.GameObjects.Sprite | undefined
    secret_text: Phaser.GameObjects.Text | undefined
    has_secret: boolean
    slots: TileItem[]
    slot_sprite!: Phaser.GameObjects.Sprite
    slots_capcity: number
    slots_last_item: TileItem | undefined
    level_info: any
    won: boolean
    lost: boolean
    report_played: boolean
    notify_cb: Function
    emitter_cb: Function

    constructor(config: any, level: LevelInfo, callback:Function, emitter:Function) {
        super('ThreeTilesScene');
        this.row_count = 10
        this.column_count = 14
        this.level_info = level
        this.level_info.extra = config.extra ?? {}
        this.item_image_hrefs = config.item_image_hrefs ?? []
        this.item_type_count =  this.item_image_hrefs.length
        this.min_tile_count = config.tile_count ?? 0
        this.secret_href = config.secret_image ??  undefined
        this.secret_message = this.wrapText(config.secret_message) ?? undefined
        this.has_secret = (config.secret_image !== undefined || config.secret_message !== undefined)
        this.report_played = true
        const remainder = this.min_tile_count % 3
        if( remainder != 0){
            this.min_tile_count += (3 - remainder)
        }
        this.items = []
        this.item_details = []
        if(config.details){
            for(const detail of config.details){
                this.item_details.push({
                    type: "item",
                    name: "threetiles.item_detail",
                    ...detail
                })
            }
        }
        this.points_tiles = {}
        this.slots = []
        this.slots_capcity = 7
        this.slots_last_item = undefined
        this.won = false
        this.lost = false
        this.notify_cb =  callback ?? (() => {})
        this.emitter_cb = emitter ?? (() => {})
    }

    splitEvery(text:string, num:number) {
        var result = [];
        for (var i = 0; i < text.length; i += num) {
            result.push(text.slice(i, i+num));
        }
        return result;
    }

    wrapText(text: string | undefined){
        if(text === undefined){
            return text;
        }
        const texts = text.trim().split('\n')
        const wrapped = []
        for(const line of texts){
            const line2 = line.trim()
            if(line2.length < 10){
                wrapped.push(line2)
            } else {
                for(const part of this.splitEvery(line2, 10)){
                    wrapped.push(part)
                }

            }
        }
        if(wrapped.length > 4){
            return wrapped.slice(0, 4)
        }
        return wrapped
    }

    public preload(): void {
        const loader = this.add.sprite(180*scaleRatio, 270*scaleRatio, "loader")
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

        this.load.image("tile_back", "assets/threetiles/tile_back.jpg")
        this.load.image("tile_cover", "assets/threetiles/tile_cover.png")
        this.load.image("tile_cover_unactive", "assets/threetiles/tile_cover_unactive.png")
        this.load.image("slot_cover", "assets/threetiles/slot_cover.png")
        this.load.image("slot_cover8", "assets/threetiles/slot_cover8.png")
        this.load.image("secret_cover", "assets/threetiles/secret_cover.jpg")
        if (this.secret_href){
            this.load.image("secret_image", this.secret_href)
        }
        for (let i = 0; i < this.item_type_count; i++) {
            const name = `tile_${i+1}`;
            const href = this.item_image_hrefs[i]
            const ext  = href.split('.').pop()?.toLowerCase()
            if(ext && ['jpg', 'png', 'jpeg'].includes(ext)){
                this.load.image(name, href)
            } else if (ext === 'svg') {
                this.load.svg(name, href)
            } else {
                console.error(`No loader plugin for ${href}`)
            }

        }

    }

    public create(data: any): void {
        this.createBoard()
        const blocks = this.initBlocks()
        this.initItems(blocks)
        this.initSlot()
    }

    createBoard() {
        if(this.secret_href){
            const sprite_texture = this.textures.get("secret_image").get()
            let scale = 1
            if(sprite_texture.width > sprite_texture.height){
                scale = (360*scaleRatio)*0.8/sprite_texture.width
            } else {
                scale = (360*scaleRatio)*0.8/sprite_texture.height
            }
            this.secret_sprite = this.add.sprite(180*scaleRatio, 240*scaleRatio, "secret_image")
            this.secret_sprite.setScale(scale*0.5)

            const cover_texture = this.textures.get("secret_cover").get()

            const ratio = sprite_texture.width/sprite_texture.height
            let w = cover_texture.width
            let h = cover_texture.height
            let cover_scale = 1
            let dx = 0
            let dy = 0
            if(ratio >= 1){
                dy = (h - h/ratio)/2
                h = h/ratio
                cover_scale = (360*scaleRatio)*0.9/w
            } else {
                dx = (w-w*ratio)/2
                w = w*ratio
                cover_scale = (360*scaleRatio)*0.9/h
            }
            this.secret_cover = this.add.sprite(180*scaleRatio, 240*scaleRatio, "secret_cover")
            this.secret_cover.setCrop(dx, dy, w, h)
            this.secret_cover.setScale(cover_scale*0.5)
        } else if (this.secret_message) {
            let scale = 1
            this.secret_text = this.add.text(180*scaleRatio, 240*scaleRatio, this.secret_message, {
                fontSize: `${28*scaleRatio}px`,
                fontStyle: "normal",
                fontFamily: fontFamily,
                color: "#000000"
            })
            this.secret_text.setOrigin(0.5, 0.5)
            this.secret_text.setScale(scale*0.5)

            const cover_texture = this.textures.get("secret_cover").get()

            const ratio = 320/240.0
            let w = cover_texture.width
            let h = cover_texture.height
            let cover_scale = 1
            let dx = 0
            let dy = 0
            if(ratio >= 1){
                dy = (h - h/ratio)/2
                h = h/ratio
                cover_scale = (360*scaleRatio)*0.9/w
            } else {
                dx = (w-w*ratio)/2
                w = w*ratio
                cover_scale = (360*scaleRatio)*0.9/h
            }
            this.secret_cover = this.add.sprite(180*scaleRatio, 240*scaleRatio, "secret_cover")
            this.secret_cover.setCrop(dx, dy, w, h)
            this.secret_cover.setScale(cover_scale*0.5)
        }

    }

    initBlocks() {
        const tile_count = this.min_tile_count
        const blocks: number[] = []
        for (let i = 0; i < tile_count; i++) {
            const tile_idx = Math.floor(i/3)
            blocks[i] = (tile_idx % this.item_type_count) + 1
        }
        return blocks
    }

    initTilePoints(){
        for (let i = 0; i < this.row_count + 1; i++) {
            for (let j = 0; j < this.column_count + 1; j++) {
                const point = `${i},${j}`
                this.points_tiles[point] = []
            }
        }
    }

    initItems(blocks: number[]) {
        this.initTilePoints()
        for (let i = 0; i < blocks.length;) {
            const xpos: number = Math.floor(Math.random() * this.row_count)
            const ypos: number = Math.floor(Math.random() * this.column_count)
            const t = blocks[i]
            const item = new TileItem(t, i, 'unactive', this, xpos, ypos)
            item.setDepth(i)
            const under_items: Set<number> = new Set()
            for (const point of item.points) {
                const under_index_array = this.points_tiles[point].slice(-1)
                if (under_index_array.length > 0) {
                    under_items.add(under_index_array[0])
                }
            }

            if (under_items.size === 1) {
                // console.log('same pos has item, ignore.')
            } else {
                this.items.push(item)
                for (const point of item.points) {
                    this.points_tiles[point].push(i)
                }
                i += 1
            }
        }

        for (const item of this.items) {
            item?.creatSprite();
        }
        this.activeItems()

    }

    async showSecret(): Promise<void>{
        if(this.secret_cover){
            const shows = []
            shows.push(new Promise<void>((resolve, reject) => {
                this.tweens.add({
                    targets: [this.secret_cover, this.secret_sprite, this.secret_text],
                    duration: 1000,
                    props:{
                        scale: "*=2"
                    },
                    ease: "Sine.easeOut",
                    onComplete: () => {
                        resolve()
                    }
                })
            }))

            shows.push(new Promise<void>((resolve, reject) => {
                this.tweens.add({
                    targets: [this.secret_cover],
                    duration: 1000,
                    props:{
                        alpha: 0
                    },
                    ease: "Sine.easeOut",
                    onComplete: () => {
                        this.secret_cover?.destroy()
                        this.secret_cover = undefined
                        resolve()
                    }
                })
            }))

            await Promise.all(shows)
        }
    }

    unActiveItems(points: string[]){
        const item_idx: Set<number> = new Set()
        for(const point of points){
            for(const idx of this.points_tiles[point]){
                item_idx.add(idx)
            }
        }
        for(const idx of item_idx){
            const item = this.items[idx]
            if(item){
                item.setUnActive()
            }
        }
    }

    activeItems() {
        const top_set: Record<string, number> = {}
        for (const [_, value] of Object.entries(this.points_tiles)) {
            if (value.length > 0) {
                const last_value = String(value[value.length - 1])
                if (last_value in top_set) {
                    top_set[last_value] += 1
                } else {
                    top_set[last_value] = 1
                }
            }

        }
        for (const [idx, count] of Object.entries(top_set)) {
            if (count == 4) {
                // console.log('active index: ', idx, this.items[parseInt(idx)])
                const item = this.items[parseInt(idx)]
                if (item) {
                    item.setActive()
                }
            }
        }

    }

    initSlot() {
        const image_texture = this.textures.get('slot_cover')
        const f = image_texture.get(0)
        const width = f.width * assetScale
        const height = f.height * assetScale
        const r = this.add.rectangle(180*scaleRatio, 510*scaleRatio, width, height)
        r.setFillStyle(0xcccccc)
        r.setOrigin(0.5, 0.5)
        this.slot_sprite = this.add.sprite(180 * scaleRatio, 510 * scaleRatio, "slot_cover")
        this.slot_sprite.setScale(assetScale)
    }

    async handleClick(item: TileItem) {
        if (this.won || this.lost) {
            return
        }
        if (this.slots.length >= this.slots_capcity) {
            return
        }
        if(this.report_played === true){
            this.emitter_cb('played', {})
            this.report_played = false
        }
        const index = this.items.indexOf(item)
        if (item && index >= 0) {
            const points = item.points
            this.items[index] = undefined
            for (const point of points) {
                this.points_tiles[point].pop()
            }
            await this.moveItemToSlot(item)
            await this.checkStatus()
        }

    }

   async checkStatus(){
        const items_count = this.items.reduce((accumulator, currValue) => {
            if(currValue === undefined){
                return accumulator
            } else {
                return accumulator + 1
            }
        }, 0)
        if(this.slots.length === 0 &&  items_count === 0){
            await this.showSecret()
            this.won = true
            this.notify_cb({
                succeed: true,
                archievement: {
                    rating: 3
                },
                items: this.item_details,
                level: this.level_info
            })
            return
        } else if (this.slots.length >= this.slots_capcity){
            const left_slots = this.slots.filter((item)=>(item.tobe_remove === false))
            if(left_slots.length >= this.slots_capcity){
                this.lost = true
                this.notify_cb({
                    succeed: false,
                    archievement: {
                        rating: 0
                    },
                    items: this.item_details,
                    level: this.level_info
                })
                return
            }
        }
    }

    async moveItemToSlot(item: TileItem) {
        let to_remove: TileItem[] = []
        item.setDepth(1000)
        item.tobe_remove = false
        const exists = this.slots.filter((it) => (item.name === it.name))
        if (exists.length > 0) {
            const last_same_item = exists[exists.length - 1]
            const arr_idx = this.slots.indexOf(last_same_item)
            if(arr_idx + 1 < this.slots.length){
                this.slots.splice(arr_idx+1, 0, item)
            } else {
                this.slots.push(item)
            }

            this.slots_last_item = item
            if (exists.length == 2) {
                to_remove = [...exists, item]
                for(const it of to_remove){
                    it.tobe_remove = true
                }
                this.slots_last_item = undefined
            }
        } else {
            this.slots.push(item)
            this.slots_last_item = item
        }

        setTimeout(() => {
            this.activeItems()
        }, 200);

        await this.renderItemToSlot(item)

        if (to_remove.length > 0) {
            const idx = this.slots.indexOf(item)
            const next_item = this.slots[idx+1]
            await this.removeSlotItems(to_remove)
            if(next_item){
                await this.renderSlot()
            }
        }
    }

    async undo() {
        if(this.slots_last_item){
            const item = this.slots_last_item
            if(item){
                this.slots_last_item = undefined
                const item_index = this.slots.indexOf(item)
                this.slots.splice(item_index, 1)
                const new_depth = this.items.length
                this.items.push(item)
                // item.setDepth(new_depth)
                for (const point of item.points) {
                    this.points_tiles[point].push(new_depth)
                }
                await item.moveBack(new_depth, true)
                this.unActiveItems(item.points)
            }
            this.activeItems()
            await this.renderSlot()
        }
    }

    async removeTileItems(indexes: number[]) {
        for (const idx of indexes) {
            const item = this.items[idx]
            if (item === undefined) {
                continue
            }
            for (const point of item.points) {
                this.points_tiles[point] = this.points_tiles[point].filter((it) => (it != idx))
            }
            this.items[idx] = undefined
            item?.destroy(true)
        }
    }

    async shuffleTileItems() {
        let moving = []
        for(const item of this.items){
            if(item){
                moving.push(item?.moveToCenter())
            }
        }

        await Promise.all(moving)

        this.points_tiles = {}
        this.initTilePoints()
        const items = this.items
        this.items = []
        shuffle(items)

        for(const [idx, item] of items.entries()){
            if(item === undefined){
                this.items.push(item)
                continue
            }

            while(true){
                const xpos: number = Math.floor(Math.random() * this.row_count)
                const ypos: number = Math.floor(Math.random() * this.column_count)
                const under_items: Set<number> = new Set()
                item.setPosition(xpos, ypos)
                for (const point of item.points) {
                    const under_index_array = this.points_tiles[point].slice(-1)
                    if (under_index_array.length > 0) {
                        under_items.add(under_index_array[0])
                    }
                }

                if (under_items.size === 1) {
                    // console.log('same pos when shuffle.')
                    continue
                } else {
                    this.items.push(item)
                    item.setUnActive()
                    item.setDepth(idx)
                    for (const point of item.points) {
                        this.points_tiles[point].push(idx)
                    }
                    break
                }
            }

        }

        for(const item of this.items){
            if(item){
                moving.push(item?.move())
            }
        }

        await Promise.all(moving)


        this.activeItems()
    }

    async removeSlotItems(to_remove: TileItem[]) {
        this.slots = this.slots.filter((it) => (!to_remove.includes(it)))
        const destroys = []
        for (const item of to_remove) {
            if(item === this.slots_last_item ){
                this.slots_last_item = undefined
            }
            destroys.push(item.destroy(true))
        }
        await Promise.all(destroys)
    }

    getPosInSlot(idx: number){
        const startx = 180 * scaleRatio - this.slot_sprite.displayWidth / 2
        return {
            x: startx + 4 * scaleRatio + idx * (44) * scaleRatio + 21 * scaleRatio,
            y: 510 * scaleRatio
        }
    }

    async renderItemToSlot(item:TileItem){
        const index = this.slots.indexOf(item)
        const moving = []
        for(let i = index; i<this.slots.length; i++){
            const pos = this.getPosInSlot(i)
            const it = this.slots[i]
            moving.push(it.moveToSlot(pos.x, pos.y, true))
        }
        await Promise.all(moving)
    }

    async renderSlot() {
        const moving = []
        for (const [idx, item] of this.slots.entries()) {
            const startx = 180 * scaleRatio - this.slot_sprite.displayWidth / 2
            const y = 510 * scaleRatio
            const x = startx + 4 * scaleRatio + idx * (44) * scaleRatio + 21 * scaleRatio
            moving.push(item.moveInSlot(x, y, true))
        }
        await Promise.all(moving)
    }

    async randomClearOne() {
        const slot_len = this.slots.length
        const random_idx = Math.floor(Math.random() * slot_len)
        const item = this.slots[random_idx]
        if (item === undefined) {
            return
        }
        const selected_items: TileItem[] = [item]
        const selected_name = item.name

        if (random_idx + 1 < slot_len) {
            if (this.slots[random_idx + 1].name === item.name) {
                selected_items.push(this.slots[random_idx + 1])
            }
        }

        if (selected_items.length === 1 && random_idx > 0) {
            if (this.slots[random_idx - 1].name === item.name) {
                selected_items.unshift(this.slots[random_idx - 1])
            }
        }

        let to_clear_count = 3 - selected_items.length
        const to_clear_indexes: number[] = []

        for (let i = 0; i < this.items.length; i++) {
            const item = this.items[i]
            if (item !== undefined && item.name === selected_name) {
                to_clear_indexes.unshift(i)
                to_clear_count -= 1
                if (to_clear_count <= 0) {
                    break;
                }
            }
        }


        this.removeTileItems(to_clear_indexes)
        this.removeSlotItems(selected_items)
        this.renderSlot()
        this.activeItems()
        await this.checkStatus()

    }

    apply(name: string) {
        if (name === 'shuffle') {
            this.shuffleTileItems()
            if(this.won || this.lost){
                return {
                    ok: false,
                    message: "没有效果，请使用其他方式"
                }
            }
            return {
                ok: true,
                message: "已经重新打乱了"
            }
        } else if (name === 'undo') {
            if(this.slots_last_item === undefined){
                return {
                    ok: false,
                    message: "只能撤销一次"
                }
            }
            this.undo()
            this.won = false
            this.lost = false
            return {
                ok: true,
                message: "已经撤销了"
            }
        } else if (name === 'clear_one') {
            this.randomClearOne()
            this.won = false
            this.lost = false
            return {
                ok: true,
                message: "已经删除了三种卡片"
            }
        } else if (name === 'extend_slot') {
            if (this.slots_capcity === 7) {
                this.slots_capcity = 8
                this.slot_sprite.setTexture('slot_cover8')
                this.renderSlot()
                this.won = false
                this.lost = false
                return {
                    ok: true,
                    message: "工作区已经增加到了8个"
                }
            }
            return {
                ok: false,
                message: "已经增加过了，不能再增加了"
            }

        }
        return {
            ok: false,
            message: "这个功能暂时还支持不了"
        }
    }

    canApply(name: string): ConditionResponse{
        if (name === 'shuffle') {
            if(this.won || this.lost){
                return {
                    ok: false,
                    message: "没有效果"
                }
            }
            return { ok:true }
        } else if (name === 'undo') {
            if(this.slots_last_item !== undefined){
                return {ok: true}
            }
            return {
                ok: false,
                message: "无法继续撤销了"
            }
        } else if (name === 'clear_one') {
            if(this.slots.length > 0){
                return {ok: true}
            }
            return {
                ok: false,
                message: "没有需要清除的"
            }
        } else if (name === 'extend_slot') {
            if (this.slots_capcity === 7) {
                return {ok: true}
            }
            return {
                ok: false,
                message: "暂存位已经扩展到最大了"
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
    height: 540 * scaleRatio,
    canvasStyle: `width: 360px;height:540px`,
    parent: 'playable-container',
    backgroundColor: '#ffffff',
    disableContextMenu: true,
    transparent: true
};

export const ThreeTilesPlayable = defineComponent({
    name: "ThreeTilesPlayable",
    props: {
        config: { type: Object as PropType<ThreeTilesConfig>, required: true },
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
            const scene = this.$options.game.scene.getScene("ThreeTilesScene") as ThreeTilesScene
            return scene.apply(name)
        },

        canApply(name: string){
            const scene = this.$options.game.scene.getScene("ThreeTilesScene") as ThreeTilesScene
            return scene.canApply(name)
        },

        createGame() {
            const game = new Phaser.Game({...this.gameConfig})
            this.$options.game = game
            game.scene.add('ThreeTilesScene', new ThreeTilesScene(this.config, this.level, (played: PlayableResult)=>{
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
        return h('div', { "id": "playable-container", ref:"playable_container"})
    }
})

export default ThreeTilesPlayable;
