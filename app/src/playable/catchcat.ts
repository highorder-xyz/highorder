import * as Phaser from 'phaser';
import { defineComponent, h, PropType } from 'vue'
import { ApplyResponse, ConditionResponse, LevelInfo, PlayableResult } from './defines';

const scaleRatio = window.devicePixelRatio;
const assetRatio = 4
const assetScale = scaleRatio / assetRatio
const fontFamily = '"Droid Sans", "PingFangSC-Regular", "Microsoft YaHei", sans-serif'

export const data = {
    scene: {
        w: 7,
        h: 11,
        r: 20
    },
    textures: {
        "bottom_left_1": "assets/catchcat/images/bottom_left/1.svg",
        "bottom_left_2": "assets/catchcat/images/bottom_left/2.svg",
        "bottom_left_3": "assets/catchcat/images/bottom_left/3.svg",
        "bottom_left_4": "assets/catchcat/images/bottom_left/4.svg",
        "bottom_left_5": "assets/catchcat/images/bottom_left/5.svg",
        "left_1": "assets/catchcat/images/left/1.svg",
        "left_2": "assets/catchcat/images/left/2.svg",
        "left_3": "assets/catchcat/images/left/3.svg",
        "left_4": "assets/catchcat/images/left/4.svg",
        "left_5": "assets/catchcat/images/left/5.svg",
        "top_left_1": "assets/catchcat/images/top_left/1.svg",
        "top_left_2": "assets/catchcat/images/top_left/2.svg",
        "top_left_3": "assets/catchcat/images/top_left/3.svg",
        "top_left_4": "assets/catchcat/images/top_left/4.svg",
        "top_left_5": "assets/catchcat/images/top_left/5.svg",
    },
    animations: [
        {
            name: "left_step",
            textures: [
                "left_1",
                "left_2",
                "left_3",
                "left_4",
                "left_5",
            ],
            repeat: 0,
        },
        {
            name: "top_left_step",
            textures: [
                "top_left_1",
                "top_left_2",
                "top_left_3",
                "top_left_4",
                "top_left_5",
            ],
            repeat: 0,
        },
        {
            name: "bottom_left_step",
            textures: [
                "bottom_left_1",
                "bottom_left_2",
                "bottom_left_3",
                "bottom_left_4",
                "bottom_left_5",
            ],
            repeat: 0,
        },
        {
            name: "left_run",
            textures: [
                "left_2",
                "left_3",
                "left_4",
                "left_5",
            ],
            repeat: 3,
        },
        {
            name: "top_left_run",
            textures: [
                "top_left_2",
                "top_left_3",
                "top_left_4",
                "top_left_5",
            ],
            repeat: 3,
        },
        {
            name: "bottom_left_run",
            textures: [
                "bottom_left_2",
                "bottom_left_3",
                "bottom_left_4",
                "bottom_left_5",
            ],
            repeat: 3,
        },
    ],
    origins: {
        left: { x: 0.75, y: 0.75 },
        top_left: { x: 0.63, y: 0.83 },
        bottom_left: { x: 0.65, y: 0.5 },
    },
    stopTextures: {
        left: "left_1",
        top_left: "top_left_1",
        bottom_left: "bottom_left_1",
    },
    cannotEscapeTextures: {
        left: "left_2",
        top_left: "top_left_2",
        bottom_left: "bottom_left_2",
    },
    directions: [
        {
            scaleX: 1,
            name: "left",
        },
        {
            scaleX: 1,
            name: "top_left",
        },
        {
            scaleX: -1,
            name: "top_left",
        },
        {
            scaleX: -1,
            name: "left",
        },
        {
            scaleX: -1,
            name: "bottom_left",
        },
        {
            scaleX: 1,
            name: "bottom_left",
        },
    ],
    catDefaultDirection: 5,
    catStepLength: 20,
    frameRate: 15,
    translations: {},
};

export interface CatchCatConfig{
    init_wall_count: number
    cat_clever: number
}

function _(text: string) {
    return text
}

declare type BlockData = {
    i: number,
    j: number,
    isWall: boolean;
    isEdge: boolean;
    isOut: boolean;
    distance: number;
    routes: number;
}

declare type Position = {
    x: number,
    y: number
}

declare type RecordCoord = {
    cat: { i: number, j: number }[],
    wall: { i: number, j: number }[],
}

enum GameState {
    PLAYING = "playing",
    WIN = "win",
    LOSE = "lose",
}

export class CatchCatScene extends Phaser.Scene {
    public readonly w: number;
    public readonly h: number;
    public readonly r: number;
    public readonly dx: number;
    public readonly dy: number;
    private recordCoord!: RecordCoord;
    x_offset: number
    y_offset: number
    status_text!: Phaser.GameObjects.Text
    notify_cb: Function
    report_played: boolean
    emitter_cb: Function
    config: CatchCatConfig
    level_info: LevelInfo

    constructor(config: CatchCatConfig, level: LevelInfo, callback: Function, emitter:Function) {
        super("CatchCatScene");
        this.config = {
            ...{init_wall_count: 12, cat_clever: 10},
            ...config},
        this.level_info = level
        this.notify_cb = callback
        this.report_played = true
        this.emitter_cb = emitter ?? (() => {})

        const w = data["scene"].w
        const h = data["scene"].h
        const r = data["scene"].r
        this.w = w;
        this.h = h;
        this.r = r * scaleRatio;
        this.dx = this.r * 2;
        this.dy = this.r * Math.sqrt(3);

        let canvasWidth = Math.ceil((3 + 2 * w) * r);
        let canvasHeight = Math.ceil((3 + Math.sqrt(3) * h) * r);
        this.x_offset = (360 - canvasWidth)*scaleRatio/2
        this.y_offset = (480 - 38 - canvasHeight)*scaleRatio/2 + 38*scaleRatio
    }

    get blocks(): Block[][] {
        return this.data.get("blocks");
    }

    set blocks(value: Block[][]) {
        this.data.set("blocks", value);
    }

    get blocksData(): boolean[][] {
        let result: boolean[][] = [];
        this.blocks.forEach((column, i) => {
            result[i] = [];
            column.forEach((block, j) => {
                result[i][j] = block.isWall;
            });
        });
        return result;
    }

    get cat(): Cat {
        return this.data.get("cat");
    }

    set cat(value: Cat) {
        this.data.set("cat", value);
    }

    get state(): GameState {
        return this.data.get("state");
    }

    set state(value: GameState) {
        const oldValue = this.data.get('state')
        switch (value) {
            case GameState.PLAYING:
                break;
            case GameState.LOSE:
                this.setStatusText(_("猫已经跑了！"));
                break;
            case GameState.WIN:
                this.setStatusText(_("猫无路可走了！"));
                break;
            default:
                return;
        }
        this.data.set("state", value);
        if(oldValue === GameState.PLAYING && value !== GameState.PLAYING){
            this.notify()
        }
    }



    preload(): void {
        let textureScale = this.r / data.catStepLength;
        for (const [key, texture] of Object.entries(data.textures)) {
            this.load.svg(key, texture)
        }
    }

    create(): void {
        this.status_text = this.add.text(180*scaleRatio, 30*scaleRatio, "", {
            fontSize: `${20*scaleRatio}px`,
            fontStyle: "normal",
            fontFamily: fontFamily,
            color: "#000000"
        })
        this.status_text.setOrigin(0.5, 0.5)
        this.createAnimations();
        this.createBlocks();
        this.createCat();
        this.reset();
    }

    getPosition(i: number, j: number): Position {
        return {
            x: this.r * 1 + ((j & 1) === 0 ? this.r + this.x_offset: this.dx + this.x_offset) + i * this.dx,
            y: this.r * 1 + this.r + j * this.dy + this.y_offset,
        };
    }

    getBlock(i: number, j: number): Block | null {
        if (!(i >= 0 && i < this.w && j >= 0 && j < this.h)) {
            return null;
        }
        return this.blocks[i][j];
    }

    playerClick(i: number, j: number): boolean {
        if (this.cat.anims.isPlaying) {
            this.cat.anims.stop();
        }
        if (this.state !== GameState.PLAYING) {
            this.setStatusText(_("游戏已经结束"));
            this.reset();
            return false;
        }
        if(this.report_played){
            this.emitter_cb('played', {})
            this.report_played = false
        }
        let block = this.getBlock(i, j);
        if (!block) {
            console.log(_("代码错误，当前位置不存在"));
            return false;
        }
        if (block.isWall) {
            console.log(_("点击位置已经是墙了，禁止点击"));
            return false;
        }
        if (this.cat.i === i && this.cat.j === j) {
            console.log(_("点击位置是猫当前位置，禁止点击"));
            return false;
        }
        block.isWall = true;
        if (this.cat.isCaught()) {
            this.setStatusText(_("猫被抓住了！"));
            this.state = GameState.WIN;
            return false;
        }

        this.recordCoord.cat.push({ i: this.cat.i, j: this.cat.j });
        this.recordCoord.wall.push({ i, j });

        let result = this.cat.step();
        if (!result) {
            this.setStatusText(_("猫被抓住了！"));
            this.state = GameState.WIN;
        }
        return true;
    }

    notify(){
        if(this.state === GameState.WIN){
            this.notify_cb({
                succeed: true,
                archievement: {
                    rating:3
                },
                level: this.level_info
            })
        }else if(this.state === GameState.LOSE){
            this.notify_cb({
                succeed: false,
                archievement: {
                    rating:0
                },
                level: this.level_info
            })
        }
    }

    reset() {
        this.cat.reset();
        this.resetBlocks();
        this.randomWall();

        this.recordCoord = {
            cat: [],
            wall: []
        };
        this.state = GameState.PLAYING;
        this.setStatusText(_("点击小圆点，围住小猫"));
    }

    undo() {
        if (this.recordCoord.cat.length) {
            if (this.state !== GameState.PLAYING) {
                this.setStatusText(_("游戏已经结束"));
                this.reset();
            } else {
                const catCoord = this.recordCoord.cat.pop();
                const wall = this.recordCoord.wall.pop();
                if (wall && catCoord) {
                    this.cat.undo(catCoord.i, catCoord.j);
                    const wallBlock = this.getBlock(wall.i, wall.j)
                    if (wallBlock) {
                        wallBlock.isWall = false;
                    }
                }
            }
        } else {
            this.setStatusText(_("无路可退！"));
        }
    }
    private setStatusText(message: string) {
        this.status_text.setText(message)
        this.status_text.setAlpha(1)
        for(const tween of this.tweens.getTweensOf(this.status_text, true)){
            tween.stop()
            tween.remove()
        }
        this.add.tween({
            targets:[this.status_text],
            duration: 600,
            delay: 3000,
            props: {
                alpha: 0
            },
            onComplete: () => {
                this.status_text.setText("")
            }
        })
    }

    private createAnimations(): void {
        data.animations.forEach(animation => {
            let frames: Phaser.Types.Animations.AnimationFrame[] = [];
            animation.textures.forEach(texture => {
                frames.push({
                    key: texture,
                    frame: 0,
                });
            });
            this.anims.create({
                key: animation.name,
                frames: frames,
                frameRate: data.frameRate,
                repeat: animation.repeat,
            });
        });
    }

    private createBlocks(): void {
        let blocks: Block[][] = [];
        for (let i = 0; i < this.w; i++) {
            blocks[i] = [];
            for (let j = 0; j < this.h; j++) {
                let block = new Block(this, i, j, this.r * 0.9);
                blocks[i][j] = block;
                this.add.existing(block);
                block.on("player_click", this.playerClick.bind(this));
            }
        }
        this.blocks = blocks;
    }

    private createCat(): void {
        let cat = new Cat(this, this.config.cat_clever);
        cat.on("escaped", () => {
            this.state = GameState.LOSE;
        });
        cat.on("win", () => {
            this.state = GameState.WIN;
        });
        this.cat = cat;
        this.add.existing(cat);
    }

    private resetBlocks() {
        this.blocks.forEach(blocks => {
            blocks.forEach(block => {
                block.isWall = false;
            });
        });
    }

    private randomWall() {
        for (let k = 0; k < this.config.init_wall_count; k++) {
            let i = Math.floor(this.w * Math.random());
            let j = Math.floor(this.h * Math.random());
            if (i !== this.cat.i || j !== this.cat.j) {
                const block = this.getBlock(i, j)
                if (block) {
                    block.isWall = true;
                }
            }
        }
    }

    public apply(name: string) {
        if(this.state != GameState.PLAYING){
            return {
                ok: false,
                message: `游戏已经结束了。`
            }
        }
        return {
            ok: false,
            message: "这个功能暂时还支持不了"
        }
    }

    public canApply(name: string): ConditionResponse{
        if(this.state != GameState.PLAYING){
            return {
                ok: false,
                message: "游戏已经结束了"
            }
        }
        return {
            ok: false,
            message: "无法支持该动作"
        }
    }
}



class CommonSolver {
    readonly w: number;
    readonly h: number;
    blocks: BlockData[][];
    i: number;
    j: number;

    constructor(blocksIsWall: boolean[][], i: number, j: number) {
        this.w = blocksIsWall.length;
        if (this.w <= 0) {
            throw new Error("empty blocks");
        }
        this.h = blocksIsWall[0].length;
        this.i = i;
        this.j = j;
        this.blocks = blocksIsWall.map((col, i) => {
            return col.map((block, j) => {
                return {
                    i:i, j:j,
                    isWall: blocksIsWall[i][j],
                    isEdge: (i == 0) || (j == 0) || (j == this.h - 1) || (i == this.w - 1),
                    isOut: false,
                    distance: Infinity,
                    routes: -1
                };
            });
        });
    }

    getNeighbours(): BlockData[] {
        return this.getNeighboursOfBlock(this.i, this.j)
    }

    getNeighboursOfBlock(i: number, j:number): BlockData[] {
        let left = this.getBlock(i - 1, j);
        let right = this.getBlock(i + 1, j);
        let top_left;
        let top_right;
        let bottom_left;
        let bottom_right;
        if ((j & 1) === 0) {
            top_left = this.getBlock(i - 1, j - 1);
            top_right = this.getBlock(i, j - 1);
            bottom_left = this.getBlock(i - 1, j + 1 );
            bottom_right = this.getBlock(i, j + 1);
        } else {
            top_left = this.getBlock(i, j - 1);
            top_right = this.getBlock(i + 1, j - 1);
            bottom_left = this.getBlock(i, j + 1);
            bottom_right = this.getBlock(i + 1, j + 1);
        }
        let neighbours = [];
        neighbours[0] = left;
        neighbours[1] = top_left;
        neighbours[2] = top_right;
        neighbours[3] = right;
        neighbours[4] = bottom_right;
        neighbours[5] = bottom_left;
        return neighbours;
    }

    getBlock(i: number, j: number): BlockData {
        if (!(i >= 0 && i < this.w && j >= 0 && j < this.h)) {
            return {
                i: i,
                j: j,
                isEdge: false,
                isWall: false,
                isOut: true,
                routes: -1,
                distance: Infinity
            }
        }
        return this.blocks[i][j];
    }
}

class NearestSolver extends CommonSolver {

    calcAllDistances() {
        let queue: BlockData[] = [];
        this.blocks.forEach(col => {
            col.forEach(block => {
                if (block.isEdge && !block.isWall) {
                    block.distance = 0;
                    queue.push(block);
                }
            });
        });
        while (queue.length > 0) {
            let block = queue.shift();
            if (!block) {
                break
            }
            const neighbours = this.getNeighboursOfBlock(block.i, block.j)
            neighbours.forEach(neighbour => {
                if (!neighbour.isOut && !neighbour.isEdge && !neighbour.isWall) {
                    if (block && neighbour.distance > block.distance + 1) {
                        neighbour.distance = block.distance + 1;
                        if (queue.filter((item) => (item.i == neighbour.i && item.j == neighbour.j)).length <= 0) {
                            queue.push(neighbour);
                        }
                    }
                }
            });
        }
    };

    calcRoutes(block:BlockData){
        if (block.routes === -1) {
            if (block.isEdge) {
                block.routes = 1;
            } else {
                let routesCount = 0;
                const neighbours = this.getNeighboursOfBlock(block.i, block.j)
                neighbours.forEach(neighbour => {
                    if (!neighbour.isOut && !neighbour.isWall) {
                        if (neighbour.distance < block.distance) {
                            routesCount += this.calcRoutes(neighbour);
                        }
                    }
                });
                block.routes = routesCount;
            }
        }
        return block.routes
    }


    solve(): number[] {
        this.calcAllDistances()
        const neighbours = this.getNeighbours()
        const block = this.getBlock(this.i, this.j)
        const neighbours_sorted:[BlockData, number, number][] = []
        for(const [index, n] of neighbours.entries()){
            if(!n.isOut && !block.isOut && n.distance < Infinity && n.distance < block.distance){
                const routes = this.calcRoutes(n)
                neighbours_sorted.push([n, index, routes])
            }
        }
        neighbours_sorted.sort((a, b) => { return b[0].routes - a[0].routes })
        return neighbours_sorted.map((item) => {return item[1]})
    }
}

export class Block extends Phaser.GameObjects.Arc {
    public readonly i: number;
    public readonly j: number;
    public readonly r: number;
    private _isWall: boolean;

    constructor(scene: CatchCatScene, i: number, j: number, r: number) {
        let position = scene.getPosition(i, j);
        super(scene, position.x, position.y, r, 0, 360, false, 0, 1);
        this.i = i;
        this.j = j;
        this.r = r;
        this._isWall = false;
        let shape = new Phaser.Geom.Circle(this.r, this.r, this.r);
        this.setInteractive(shape, Phaser.Geom.Circle.Contains);
        this.on("pointerdown", () => {
            this.emit("player_click", this.i, this.j);
        });
    }


    get isWall(): boolean {
        return this._isWall;
    }

    set isWall(value: boolean) {
        this._isWall = value;
        if (value) {
            this.fillColor = 0x003366;
        } else {
            this.fillColor = 0xb3d9ff;
        }
    }
}

export class Cat extends Phaser.GameObjects.Sprite {
    clever: number
    clever_ratio: number

    constructor(scene: CatchCatScene, clever: number) {
        super(scene, 0, 0, "__DEFAULT");
        this.clever = clever
        if(this.clever > 10){
            this.clever = 0
        }
        if(this.clever < 1){
            this.clever = 1
        }
        this.clever_ratio = (10-clever)/10
        this.on("animationrepeat", () => {
            this.moveForward();
        });
        this.direction = data.catDefaultDirection;
        this.setScale(scaleRatio)
        this.reset();
    }

    get i(): number {
        return this.getData("i");
    }

    set i(value: number) {
        this.setData("i", value);
    }

    get j(): number {
        return this.getData("j");
    }

    set j(value: number) {
        this.setData("j", value);
    }

    get direction(): number {
        return this.getData("direction");
    }

    set direction(value: number) {
        this.setData("direction", value);
        this.resetTextureToStop();
        this.resetOriginAndScale();
    }

    reset() {
        this.anims.stop();
        this.direction = data.catDefaultDirection;
        this.resetIJ();
    }

    undo(i: number, j: number) {
        this.anims.stop();
        this.setIJ(i, j)
    }

    nearestDirection(blocksIsWall: boolean[][], i: number, j: number): number {
        const blocks = new NearestSolver(blocksIsWall, i, j);
        const directions = blocks.solve();
        if (directions.length > 0) {
            return directions[0];
        } else {
            return -1;
        }
    }


    randomDirection(blocksIsWall: boolean[][], i: number, j: number): number {
        let solver = new CommonSolver(blocksIsWall, i, j)
        let neighbours = solver.getNeighbours()
        let directions: number[] = [];
        neighbours.forEach((neighbour, direction) => {
            if (!neighbour.isOut && !neighbour.isWall) {
                directions.push(direction);
            }
        });
        return directions[Math.floor(directions.length * Math.random())];
    }

    trySolve(blocksIsWall: boolean[][], i: number, j: number) {
        const v = Math.random()
        if(v >= this.clever_ratio){
            return this.nearestDirection(blocksIsWall, i, j)
        } else {
            const direction = this.nearestDirection(blocksIsWall, i, j)
            if(direction === -1){
                return direction
            } else {
                return this.randomDirection(blocksIsWall, i, j)
            }
        }
    }

    step(): boolean {
        let direction = this.trySolve((this.scene as CatchCatScene).blocksData, this.i, this.j);
        if (direction < 0 || direction > 6) {
            this.caught();
            return false;
        }
        let result = this.stepDirection(direction);
        if (!result) {
            this.caught();
            return false;
        }
        return true;
    }

    isCaught() {
        return !this.getCurrentNeighbours()
            .some((neighbour, direction: number) => {
                return !neighbour.isOut && !neighbour.isWall;
            });
    }

    private caught() {
        this.setTexture((data.cannotEscapeTextures as Record<string, any>)[data.directions[this.direction].name]);
    }

    private escape() {
        if (this.j === 0 || this.j === (this.scene as CatchCatScene).h - 1) {
            this.runForward();
        } else if (this.i === 0) {
            this.runDirection(0);
        } else if (this.i === (this.scene as CatchCatScene).w - 1) {
            this.runDirection(3);
        }
    }

    private setIJ(i: number, j: number): this {
        this.i = i;
        this.j = j;
        let position = (this.scene as CatchCatScene).getPosition(i, j);
        return this.setPosition(position.x, position.y);
    }

    private resetIJ() {
        this.setIJ(Math.floor((this.scene as CatchCatScene).w / 2), Math.floor((this.scene as CatchCatScene).h / 2));
    }

    private isEscaped() {
        return this.i <= 0 || this.i >= (this.scene as CatchCatScene).w - 1
            || this.j <= 0 || this.j >= (this.scene as CatchCatScene).h - 1;
    }

    private checkState() {
        if (this.isEscaped()) {
            this.escape();
            this.emit("escaped");
        } else if (this.isCaught()) {
            this.caught();
            this.emit("win");
        }
    }

    private getCurrentNeighbours() {
        const solver = new CommonSolver((this.scene as CatchCatScene).blocksData, this.i, this.j)
        return solver.getNeighbours();
    }

    private resetTextureToStop() {
        this.setTexture((data.stopTextures as Record<string, any>)[data.directions[this.direction].name]);
    }

    private resetOriginAndScale() {
        let directionData = data.directions[this.direction];
        let origin = (data.origins as Record<string, any>)[directionData.name];
        this.setOrigin(origin.x, origin.y);
        this.scaleX = directionData.scaleX * scaleRatio;
    }

    private moveForward() {
        let neighbour = this.getCurrentNeighbours()[this.direction];
        this.setIJ(neighbour.i, neighbour.j);
        this.checkState();
    }

    private stepForward(): boolean {
        let block = this.getCurrentNeighbours()[this.direction];
        if (block.isOut) {
            return false;
        }
        if (block.isWall) {
            return false;
        }
        this.play(data.directions[this.direction].name + "_step");
        this.once("animationcomplete", () => {
            this.moveForward();
            this.resetTextureToStop();
        });
        return true;
    }

    private stepDirection(direction: number): boolean {
        this.direction = direction;
        return this.stepForward();
    }

    private runForward() {
        this.play(data.directions[this.direction].name + "_run");
    }

    private runDirection(direction: number) {
        this.direction = direction;
        this.runForward();
    }
}

export const gameConfig = {
    type: Phaser.AUTO,
    width: 360 * scaleRatio,
    height: 480 * scaleRatio,
    canvasStyle: `width: 360px;height:480px`,
    parent: 'playable-container',
    backgroundColor: 0xeeeeee,
    disableContextMenu: true,
    transparent: true
};

export const CatchCatPlayable = defineComponent({
    name: "CatchCatPlayable",
    props: {
        config: { type: Object as PropType<CatchCatConfig>, required: true },
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
            const scene = this.$options.game.scene.getScene("CatchCatScene") as CatchCatScene
            return scene.apply(name)
        },

        canApply(name: string){
            const scene = this.$options.game.scene.getScene("CatchCatScene") as CatchCatScene
            return scene.canApply(name)
        },

        createGame() {
            const game = new Phaser.Game({...this.gameConfig})
            this.$options.game = game
            game.scene.add('CatchCatScene', new CatchCatScene(this.config, this.level, (played: PlayableResult)=>{
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
        return h('div', { "id": "playable-container"})
    }
})

export default CatchCatPlayable;
