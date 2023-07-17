import * as Phaser from 'phaser';
import { defineComponent, h, PropType } from 'vue'
import { ApplyResponse, ConditionResponse, LevelInfo, PlayableResult } from './defines';

const scaleRatio = window.devicePixelRatio
const assetRatio = 4
const assetScale = scaleRatio / assetRatio
const canvasHeight = 540
const canvasHalfHeight = 270

const fontFamily = '"Droid Sans", "PingFangSC-Regular", "Microsoft YaHei", sans-serif'

export interface RotateRightConfig {
    image_url: string,
    image_detail?: {
        author: string,
        title: string,
        description: string,
    }
}

interface TileItem {
    item: Phaser.GameObjects.Image,
    animating: boolean
}

export class PreloadScene extends Phaser.Scene {
    public preload(): void {
        this.load.image("loader", "/assets/common/loader.png")
    }

    public create(data: any): void {
        this.scene.start("RotateRightScene")
    }

}

export class RotateRightScene extends Phaser.Scene {
    config: RotateRightConfig
    img!: Phaser.GameObjects.Image
    level_info: LevelInfo
    won: boolean
    lost: boolean
    tiles: Array<TileItem>
    notify_cb: Function
    report_played: boolean
    emitter_cb: Function
    asset_scale: number

    constructor(config: RotateRightConfig, level: LevelInfo, callback:Function, emitter:Function) {
        super('RotateRightScene');
        this.config = config
        this.level_info = level
        this.won = false
        this.lost = false
        this.tiles = []
        this.asset_scale = 1
        this.notify_cb =  callback ?? (() => {})
        this.report_played = true
        this.emitter_cb = emitter ?? (() => {})
    }

    public preload(): void {
        const loader = this.add.sprite(180*scaleRatio, canvasHalfHeight*scaleRatio, "loader")
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

        this.load.image("image", this.config.image_url)
    }

    public create(data: any): void {
        const image_texture = this.textures.get('image')
        const f = image_texture.get(0)
        const tile_width = Math.round(f.width/4)
        const scale = (90*scaleRatio)/tile_width
        this.asset_scale = scale

        this.showImageStart().then(()=>{
            this.img.setVisible(false)
            this.showTileImages().then(() => {
                this.createRotatedTileImages()
            })
        })
    }

    async createRotatedTileImages() {
        await new Promise<void>((resolve, reject) => {
            for(const tile of this.tiles){
                const rotated = Math.floor(Math.random() * 3) + 1
                const item = tile.item
                this.tweens.add({
                    targets:[item],
                    duration: rotated*180,
                    props: {
                        angle: rotated*90,
                        scale: this.asset_scale*0.98
                    },
                    ease: "Sine.easeOut",
                    onComplete: () => {
                        tile.item.setInteractive()
                            .on("pointerdown", () => {
                                // img.setAngle(img.angle + 90)
                                this.rotateRight(tile).then(() => {
                                    this.checkState()
                                })
                                if(this.report_played){
                                    this.emitter_cb('played', {})
                                    this.report_played = false
                                }
                            })
                        resolve()
                    }
                })
            }
        })
    }

    async showTileImages(){
        const image_texture = this.textures.get('image')
        const f = image_texture.get(0)
        const tile_width = Math.round(f.width/4)
        const row_count = Math.round(f.height/tile_width)
        const top_offset = (canvasHeight-row_count*90)/2

        for(let i=0; i<row_count; i++){
            for(let j=0; j<4; j++){
                image_texture.add(`tile_${j}_${i}`, 0, j*tile_width, i*tile_width, tile_width, tile_width)
                const img = this.add.image((j*90 + 45)*scaleRatio, (i*90 + 45 + top_offset)*scaleRatio, "image", `tile_${j}_${i}`)
                img.setScale(this.asset_scale)
                const ti  = {
                    item: img,
                    animating: false
                }
                this.tiles.push(ti)
            }
        }
        await new Promise<void>((resolve, reject) => {
            const tile_images = this.tiles.map((tile) => (tile.item))
            this.tweens.add({
                targets: tile_images,
                duration: 300,
                props: {
                    scale: this.asset_scale*0.9
                },
                onComplete: () => {
                    resolve()
                }
            })
        })
    }

    async showImageStart(){
        this.img = this.add.image(180*scaleRatio, canvasHalfHeight*scaleRatio, 'image')
        this.img.setScale(this.asset_scale*1.3)
        await new Promise<void>((resolve, reject) => {
            this.tweens.add({
                targets:[this.img],
                duration: 1200,
                props: {
                    scale: this.asset_scale * 1
                },
                ease: "Sine.easeIn",
                onComplete: () => {
                    resolve()
                }
            })
        })
    }

    async rotateRight(ti: TileItem){
        if(ti.animating == true){
            return
        }
        ti.animating = true
        const current_angle = ti.item.angle
        await new Promise<void>((resolve, reject) => {
            const timeline = this.tweens.timeline({
                onComplete: () => {
                    ti.animating = false
                    resolve()
                }
            })

            timeline.add({
                targets: [ti.item],
                duration: 80,
                props: {
                    scale: this.asset_scale * 0.90
                },
                ease: 'Sine.easeIn'
            })

            timeline.add({
                targets: [ti.item],
                duration: 200,
                props: {
                    angle:  current_angle + 90
                },
                ease: 'Power0'
            })

            timeline.add({
                targets: [ti.item],
                duration: 80,
                props: {
                    scale: this.asset_scale * 0.98
                },
                ease: 'Sine.Out'
            })

            timeline.play()
        })
    }

    async showWon(){
        const items = this.tiles.map((tile) => (tile.item))
        await new Promise<void>((resolve, reject) => {
            const timeline = this.tweens.timeline({
                onComplete: () => {
                    resolve()
                }
            })
            timeline.add({
                targets: items,
                duration: 240,
                props: {
                    scale: this.asset_scale
                },
                ease: "Sine.easeInOut",
                onComplete: () => {
                    this.img.setVisible(true)
                    for(const item of items){
                        item.setVisible(false)
                    }
                }
            })
            timeline.add({
                targets: this.img,
                duration: 3000,
                props: {
                    scale: this.asset_scale*0.9
                },
                ease: "Sine.easeInOut",
            })
            timeline.play()
        })
    }

    checkState() {
        const won = this.tiles.every((tile) => (tile.animating === false && tile.item.angle % 360 == 0))
        if(won === true){
            this.won = won
            for(const tile of this.tiles){
                tile.item.disableInteractive()
                // tile.item.setScale(this.asset_scale)
            }
            this.showWon().then(() => {
                const ret:PlayableResult = {
                    succeed: true,
                    archievement: {
                        rating: 3
                    },
                    level: this.level_info
                }
                if(this.config.image_detail !== undefined){
                    ret.items = []
                    ret.items.push({
                        type: "item",
                        name: "rotate_right.painting",
                        href: this.config.image_url,
                        title: this.config.image_detail.title,
                        author: this.config.image_detail.author,
                        description: this.config.image_detail.description
                    })
                }
                this.notify_cb(ret)
            })
        }
    }


    async rotateOneTile() {
        const filtered = this.tiles.filter((tile) => (tile.item.angle % 360 != 0))
        if(filtered.length == 0){
            return
        }

        const tile_idx = Math.floor(Math.random()*filtered.length)
        const tile = filtered[tile_idx]
        let count = (tile.item.angle % 360) / 90
        if(count < 0){
            count = Math.abs(count)
        } else {
            count = 4 - count
        }

        tile.item.disableInteractive()
        for(let i = 0; i<count; i++){
            await this.rotateRight(tile)
        }
        tile.item.setInteractive()
        this.checkState()
    }

    apply(name: string) {
        if(this.won || this.lost){
            return {
                ok: false,
                message: `游戏已经结束了。`
            }
        }
        if (name === 'correct_one') {
            this.rotateOneTile()
            return {
                ok: true,
                message: "已经提示一步了"
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
        if (name === 'correct_one') {
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
    height: canvasHeight * scaleRatio,
    canvasStyle: `width: ${360}px;height:${canvasHeight}px`,
    parent: 'playable-container',
    backgroundColor: '#ffffff',
    disableContextMenu: true,
    transparent: true
};

export const RotateRightPlayable = defineComponent({
    name: "RotateRightPlayable",
    props: {
        config: { type: Object as PropType<RotateRightConfig>, required: true },
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
            const scene = this.$options.game.scene.getScene("RotateRightScene") as RotateRightScene
            return scene.apply(name)
        },

        canApply(name: string){
            const scene = this.$options.game.scene.getScene("RotateRightScene") as RotateRightScene
            return scene.canApply(name)
        },

        createGame() {
            const game = new Phaser.Game({...this.gameConfig})
            this.$options.game = game
            game.scene.add('RotateRightScene', new RotateRightScene(this.config, this.level, (played: PlayableResult)=>{
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
        return h('div', { "id": "playable-container"})
    }
})

export default RotateRightPlayable;
