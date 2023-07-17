import Phaser from "phaser"
import { defineComponent, h, PropType } from 'vue'
import { ApplyResponse, ConditionResponse, LevelInfo, PlayableResult } from './defines';

const scaleRatio = window.devicePixelRatio
const assetRatio = 4
const assetScale = scaleRatio / assetRatio

// 计算延长线,p2往p1延长
export function calcParallel(p1: Phaser.Geom.Point, p2: Phaser.Geom.Point, L: number) {
    var p = new Phaser.Geom.Point();
    if (p1.x == p2.x) {
        if (p1.y - p2.y > 0) {
            p.x = p1.x;
            p.y = p1.y + L;
        } else {
            p.x = p1.x;
            p.y = p1.y - L;
        }
    } else {
        var k = (p2.y - p1.y) / (p2.x - p1.x);
        if (p2.x - p1.x < 0) {
            p.x = p1.x + L / Math.sqrt(1 + k * k);
            p.y = p1.y + L * k / Math.sqrt(1 + k * k);
        } else {
            p.x = p1.x - L / Math.sqrt(1 + k * k);
            p.y = p1.y - L * k / Math.sqrt(1 + k * k);
        }
    }
    p.x = Math.round(p.x);
    p.y = Math.round(p.y);
    return new Phaser.Geom.Point(p.x, p.y);
}

// 计算垂直线,p2点开始垂直
export function calcVertical(p1: Phaser.Geom.Point, p2: Phaser.Geom.Point, L: number, isLeft: boolean) {
    var p = new Phaser.Geom.Point();
    if (p1.y == p2.y) {
        p.x = p2.x;
        if (isLeft) {
            if (p2.x - p1.x > 0) {
                p.y = p2.y - L;
            } else {
                p.y = p2.y + L;
            }
        } else {
            if (p2.x - p1.x > 0) {
                p.y = p2.y + L;
            } else {
                p.y = p2.y - L;
            }
        }
    } else {
        var k = -(p2.x - p1.x) / (p2.y - p1.y);
        if (isLeft) {
            if (p2.y - p1.y > 0) {
                p.x = p2.x + L / Math.sqrt(1 + k * k);
                p.y = p2.y + L * k / Math.sqrt(1 + k * k);
            } else {
                p.x = p2.x - L / Math.sqrt(1 + k * k);
                p.y = p2.y - L * k / Math.sqrt(1 + k * k);
            }
        } else {
            if (p2.y - p1.y > 0) {
                p.x = p2.x - L / Math.sqrt(1 + k * k);
                p.y = p2.y - L * k / Math.sqrt(1 + k * k);
            } else {
                p.x = p2.x + L / Math.sqrt(1 + k * k);
                p.y = p2.y + L * k / Math.sqrt(1 + k * k);
            }
        }
    }
    p.x = Math.round(p.x);
    p.y = Math.round(p.y);
    return new Phaser.Geom.Point(p.x, p.y);
}

export function randomMinMax(min: number, max: number) {
    return Math.random() * (max - min) + min;
}

export function randomPosX(width: number) {
    return randomMinMax(-100 * scaleRatio, width + 100 * scaleRatio);
}

export function randomPosY(height: number) {
    return randomMinMax(10 * scaleRatio, 110 * scaleRatio) + height;
}

export function randomVelocityX(posX: number, width: number) {
    if (posX < 0) {
        return randomMinMax(56 * scaleRatio, 280 * scaleRatio);
    } else if (posX >= 0 && posX < width / 2) {
        return randomMinMax(0, 280 * scaleRatio);
    } else if (posX >= width / 2 && posX < width) {
        return randomMinMax(-280 * scaleRatio, 0);
    } else {
        return randomMinMax(-280 * scaleRatio, -56 * scaleRatio);
    }
}

export function randomVelocityY() {
    return randomMinMax(-900 * scaleRatio, -800 * scaleRatio);
}

export function degCos(deg: number) {
    return Math.cos(deg * Math.PI / 180);
}

export function degSin(deg: number) {
    return Math.sin(deg * Math.PI / 180);
}

export function shuffle(o: Array<any>) {
    for (var j, x, i = o.length; i; j = Math.random() * i, x = o[--i], o[i] = o[j], o[j] = x);
    return o;
}

interface TimedPoint {
    point: Phaser.Geom.Point
    time: number
}

class Blade {
    scene: Phaser.Scene
    blade: Phaser.Geom.Polygon
    graphics: Phaser.GameObjects.Graphics
    points: TimedPoint[]
    POINTLIFETIME = 200;
    allowBlade = false;
    lastPoint: TimedPoint | undefined;

    constructor(scene: Phaser.Scene) {
        this.scene = scene;
        this.blade = new Phaser.Geom.Polygon()
        this.graphics = this.scene.add.graphics({ x: 0, y: 0 })
        this.points = []
    }

    generateBlade(points: Array<TimedPoint>) {
        let res: Array<Phaser.Geom.Point> = [];
        if (points.length <= 0) {
            return res;
        } else if (points.length == 1) {
            var oneLength = 3 * scaleRatio;
            res.push(new Phaser.Geom.Point(points[0].point.x - oneLength, points[0].point.y));
            res.push(new Phaser.Geom.Point(points[0].point.x, points[0].point.y - oneLength));
            res.push(new Phaser.Geom.Point(points[0].point.x + oneLength, points[0].point.y));
            res.push(new Phaser.Geom.Point(points[0].point.x, points[0].point.y + oneLength));
        } else {
            var tailLength = 10 * scaleRatio;
            var headLength = 20 * scaleRatio;
            var tailWidth = 1 * scaleRatio;
            var headWidth = 3 * scaleRatio;
            res.push(calcParallel(points[0].point, points[1].point, tailLength));
            for (var i = 0; i < points.length - 1; i++) {
                res.push(calcVertical(points[i + 1].point, points[i].point,
                    Math.round((headWidth - tailWidth) * i / (points.length - 1) + tailWidth), true));
            }
            res.push(calcVertical(points[points.length - 2].point, points[points.length - 1].point, headWidth, false));
            res.push(calcParallel(points[points.length - 1].point, points[points.length - 2].point, headLength));
            res.push(calcVertical(points[points.length - 2].point, points[points.length - 1].point, headWidth, true));
            for (var i = points.length - 1; i > 0; i--) {
                res.push(calcVertical(points[i].point, points[i - 1].point,
                    Math.round((headWidth - tailWidth) * (i - 1) / (points.length - 1) + tailWidth), false));
            }
        }
        return res;
    }

    update() {
        if (this.allowBlade) {
            this.graphics.clear();
            if (this.scene.input)
                if (this.scene.input.activePointer.isDown) {
                    var point = {
                        point: new Phaser.Geom.Point(this.scene.input.x, this.scene.input.y),
                        time: new Date().getTime()
                    }
                    if (!this.lastPoint) {
                        this.lastPoint = point
                        this.points.push(point);
                    } else {
                        const _lastPoint = this.lastPoint.point
                        const _point = point.point
                        var dis = (_lastPoint.x - _point.x) * (_lastPoint.x - _point.x) +
                            (_lastPoint.y - _point.y) * (_lastPoint.y - _point.y);
                        if (dis > 200 * scaleRatio) {
                            this.lastPoint = point;
                            this.points.push(point);
                        }
                    }
                }

            if (this.points.length < 1) {
                return;
            }
            if (new Date().getTime() - this.points[0].time > this.POINTLIFETIME) {
                this.points.shift();
            }
            if (this.points.length < 1) {
                return;
            }
            this.blade.setTo(this.generateBlade(this.points));
            this.graphics.fillStyle(0xffffff, 0.8);
            const fillPoints = this.blade.points
            this.graphics.fillPoints(fillPoints, false, false);
        }
    }

    checkCollide(sprite: Phaser.GameObjects.Sprite, onCollide: (deg:number) => void) {
        if (this.allowBlade && this.scene.input.activePointer.isDown && this.points.length > 2) {
            const collide_points: Array<Phaser.Geom.Point> = []
            for (var i = 0; i < this.points.length; i++) {
                if (Phaser.Geom.Rectangle.Contains(sprite.getBounds(), this.points[i].point.x, this.points[i].point.y)) {
                    collide_points.push(this.points[i].point)
                    if((i+1) < this.points.length){
                        collide_points.push(this.points[i+1].point)
                    } else if(i > 0){
                        collide_points.push(this.points[i-1].point)
                    }
                    break;
                }
            }
            if(collide_points.length > 0){
                const deg = this.calcDegree(collide_points)
                onCollide(deg);
            }

        }
    }

    calcDegree(points: Array<Phaser.Geom.Point>){
        let deg;
        if (points.length === 1){
            return 0;
        }
        if (points[0].x == points[1].x) {
            deg = 90;
        } else {
            var val = (points[0].y - points[1].y) / (points[0].x - points[1].x);
            deg = Math.round(Math.atan(val) / Math.PI * 180);
        }
        if (deg < 0) {
            deg = deg + 180;
        }
        return deg;
    }

    setAllowBlade() {
        this.allowBlade = true;
    }

}

class FruitTexture {
    colorMap = {
        "apple": 0xFFC3E925,
        "banana": 0xFFFFE337,
        "basaha": 0xFFEB2D13,
        "peach": 0xFFF8C928,
        "sandia": 0xFF739E0F
    }

    init(textures: Phaser.Textures.TextureManager) {
        for (const [name, color_num] of Object.entries(this.colorMap)) {
            const key = `flameParticle-${name}`
            const canvas = textures.createCanvas(key, 80 * scaleRatio, 80 * scaleRatio)
            this.generateCanvas(canvas, color_num)
        }
    }

    generateCanvas(canvas: Phaser.Textures.CanvasTexture, color_num: number) {
        var len = 40 * scaleRatio;
        const context = canvas.context
        context.clearRect(0, 0, 2 * len, 2 * len);
        var radgrad = context.createRadialGradient(len, len, 4, len, len, len);
        let color = Phaser.Display.Color.IntegerToColor(color_num);
        radgrad.addColorStop(0, color.rgba);
        color.alpha = 0;
        radgrad.addColorStop(1, color.rgba);
        context.fillStyle = radgrad;
        context.fillRect(0, 0, 2 * len, 2 * len);
        canvas.refresh();
    }
}

const fruits_degree_offset:Record<string, number> = {
    "apple": -45,
    "banana": -90,
    "basaha": -135,
    "peach": -45,
    "sandia": -100
}

class Fruit {
    name: string
    degree_offset: number
    scene: Phaser.Scene
    particles: Phaser.GameObjects.Particles.ParticleEmitterManager
    sprite: Phaser.Physics.Arcade.Sprite

    constructor(name: string, scene: Phaser.Scene) {
        this.name = name
        this.degree_offset = fruits_degree_offset[name]
        this.scene = scene
        const key = `flameParticle-${name}`
        this.sprite = scene.physics.add.sprite(0, 0, this.name);
        this.sprite.setScale(assetScale)
        this.particles = this.scene.add.particles(key)
        this.particles.createEmitter({
            on: false,
            maxParticles: 20,
            alpha: {
                start: 1,
                end: 0.1,
                steps: 30
            },
            scaleX: {
                start: 0.1,
                end: 1,
                steps: 30
            },
            scaleY: {
                start: 0.1,
                end: 1,
                steps: 30
            },
            speedX: {
                min: -400,
                max: 400
            },
            speedY: {
                min: -400,
                max: 400
            },
            gravityY: 0,
            lifespan: 2000
        })
    }

    half(deg: number, shouldEmit: boolean) {
        const sprite = this.sprite
        const angle = this.degree_offset + deg
        if (sprite && sprite.body) {
            const x = sprite?.x
            const y = sprite?.y
            const halfOne = this.scene.physics.add.sprite(x, y, this.name + '-1');
            halfOne.setScale(assetScale)
            halfOne.angle = angle;
            halfOne.body.velocity.x = 100 * scaleRatio + sprite.body.velocity.x;
            halfOne.body.velocity.y = sprite.body.velocity.y;
            halfOne.body.gravity.y = 1000 * scaleRatio;
            halfOne.setCollideWorldBounds(true);
            halfOne.body.onWorldBounds = true;
            const halfTwo = this.scene.physics.add.sprite(x, y, this.name + '-2');
            halfTwo.setScale(assetScale)
            halfTwo.angle = angle;
            halfTwo.body.velocity.x = -100 * scaleRatio + sprite.body.velocity.x;
            halfTwo.body.velocity.y = sprite.body.velocity.y;
            halfTwo.body.gravity.y = 1000 * scaleRatio;
            halfTwo.setCollideWorldBounds(true);
            halfTwo.body.onWorldBounds = true;
            sprite.destroy();
            if (shouldEmit) {
                this.particles.emitParticle(10, x, y)
            }
        }

    }

    destroy() {
        this.sprite.destroy()
        this.particles.destroy()
    }
}

class BombTexture {
    init(textures: Phaser.Textures.TextureManager) {
        const key = `flameParticle-bomb`
        const canvas = textures.createCanvas(key, 50 * scaleRatio, 50 * scaleRatio)
        this.generateCanvas(canvas)
    }

    generateCanvas(canvas: Phaser.Textures.CanvasTexture) {
        var len = 10 * scaleRatio;
        const context = canvas.context
        context.fillStyle = "#FFFFFFFF";
        context.fillRect(25 * scaleRatio, 25 * scaleRatio, len, len)
        canvas.refresh()
    }
}

class Bomb {
    scene: Phaser.Scene
    particles: Phaser.GameObjects.Particles.ParticleEmitterManager
    sprite: Phaser.Physics.Arcade.Sprite
    group: Phaser.GameObjects.Group

    constructor(scene: Phaser.Scene) {
        this.scene = scene
        const key = `flameParticle-bomb`
        this.group = scene.physics.add.group()
        this.sprite = scene.physics.add.sprite(0, 0, "bomb");
        this.sprite.setScale(assetScale)
        this.particles = this.scene.add.particles(key)
        this.group.add(this.sprite)
        this.particles.createEmitter({
            on: true,
            follow: this.sprite,
            followOffset: { x: -25, y: -25 },
            alpha: {
                start: 1,
                end: 0.1,
                steps: 20
            },
            speedX: {
                min: -60,
                max: 60
            },
            speedY: {
                min: -60,
                max: 60
            },
            scaleX: {
                start: 1,
                end: 0.8,
                steps: 20
            },
            scaleY: {
                start: 1,
                end: 0.8,
                steps: 20
            },
            frequency: 50,
            // gravityY: 80
            lifespan: 500,
        })
    }

    explode(onWhite: () => void, onCompleteCallBack: () => void) {
        let lights: Phaser.GameObjects.Graphics[] = [];
        const tweens: Phaser.Types.Tweens.TweenBuilderConfig[] = []
        const sprite = this.sprite
        var startDeg = Math.floor(Math.random() * 360);
        for (var i = 0; i < 8; i++) {
            var light = this.scene.add.graphics({ x: sprite.body.x + sprite.displayWidth / 2, y: sprite.body.y + sprite.displayHeight / 2 });
            var points = [];
            points[0] = new Phaser.Geom.Point(0, 0);
            points[1] = new Phaser.Geom.Point(Math.floor(800 * scaleRatio * degCos(startDeg + i * 45)),
                Math.floor(800 * scaleRatio * degSin(startDeg + i * 45)));
            points[2] = new Phaser.Geom.Point(Math.floor(800 * scaleRatio * degCos(startDeg + i * 45 + 10)),
                Math.floor(800 * scaleRatio * degSin(startDeg + i * 45 + 10)));
            light.fillStyle(0xffffff);
            light.fillPoints(points);
            light.alpha = 0;
            lights.push(light);
            tweens.push({
                targets: light,
                props: {
                    alpha: 1
                },
                duration: 100,
                ease: "Linear"
            })
        }
        const whiteScreen = this.scene.add.graphics({ x: 0, y: 0 })
        whiteScreen.fillStyle(0xffffff);
        whiteScreen.fillRect(0, 0, 360 * scaleRatio, 480 * scaleRatio);
        whiteScreen.alpha = 0;
        tweens.push({
            targets: whiteScreen,
            props: {
                alpha: 1
            },
            duration: 800,
            ease: "Sine-easyInOut"
        })

        const timeline = this.scene.tweens.timeline({
            yoyo: true,
            // totalDuration: 2000,
            onComplete: () => {
                for (const light of lights) {
                    light.destroy()
                }
                onWhite()
                this.scene.tweens.add({
                    targets: whiteScreen,
                    props: {
                        alpha: 0
                    },
                    duration: 800,
                    ease: "Sine-easyInOut",
                    onComplete: () => {
                        onCompleteCallBack()
                    }
                })

            }
        })
        for (const tween of tweens) {
            timeline.add(tween)
        }
        timeline.play()
    }

    sprites() {
        return this.group.children.entries
    }

    destroy() {
        this.particles.destroy()
        this.sprite.destroy()
    }
}

export interface CutFruitConfig {
    has_bomb: boolean,
    max_lost: number
}

class CutFruitScene extends Phaser.Scene {
    bg: Phaser.GameObjects.Image | undefined
    config: CutFruitConfig
    showXXX: boolean
    blade!: Blade
    fruits: (Fruit | Bomb)[]
    gravity: number
    score: number = 0
    playing: boolean = true
    bombExplode: boolean = false
    lostCount: number = 0
    scoreImage: Phaser.GameObjects.Image | undefined
    best: Phaser.GameObjects.Image | undefined
    scoreText: Phaser.GameObjects.BitmapText | undefined
    xxxGroup: Phaser.GameObjects.Group | undefined
    lostScoreSprites: Array<Phaser.GameObjects.Image>
    level_info: LevelInfo
    notify_cb: Function
    report_played: boolean
    emitter_cb: Function

    constructor(config: CutFruitConfig, level:LevelInfo, callback:Function, emitter:Function) {
        super("CutFruitScene")
        this.config =  {...{
            has_bomb: true,
            max_lost: 3
        }, ...config}

        if(this.config.max_lost != 3){
            this.showXXX = false
        } else {
            this.showXXX = true
        }
        this.level_info = level
        this.notify_cb = callback
        this.report_played = true
        this.emitter_cb = emitter ?? (() => {})

        this.fruits = []
        this.lostScoreSprites = []
        this.gravity = 1000 * scaleRatio
    }

    preload() {
        this.load.image('apple', 'assets/cutfruit/apple.png');
        this.load.image('apple-1', 'assets/cutfruit/apple-1.png');
        this.load.image('apple-2', 'assets/cutfruit/apple-2.png');
        this.load.image('background', 'assets/cutfruit/background.jpg');
        this.load.image('banana', 'assets/cutfruit/banana.png');
        this.load.image('banana-1', 'assets/cutfruit/banana-1.png');
        this.load.image('banana-2', 'assets/cutfruit/banana-2.png');
        this.load.image('basaha', 'assets/cutfruit/basaha.png');
        this.load.image('basaha-1', 'assets/cutfruit/basaha-1.png');
        this.load.image('basaha-2', 'assets/cutfruit/basaha-2.png');
        this.load.image('bomb', 'assets/cutfruit/bomb.png');
        this.load.image('game-over', 'assets/cutfruit/game-over.png');
        this.load.image('lose', 'assets/cutfruit/lose.png');
        this.load.image('peach', 'assets/cutfruit/peach.png');
        this.load.image('peach-1', 'assets/cutfruit/peach-1.png');
        this.load.image('peach-2', 'assets/cutfruit/peach-2.png');
        this.load.image('sandia', 'assets/cutfruit/sandia.png');
        this.load.image('sandia-1', 'assets/cutfruit/sandia-1.png');
        this.load.image('sandia-2', 'assets/cutfruit/sandia-2.png');
        this.load.image('score', 'assets/cutfruit/score.png');
        this.load.image('shadow', 'assets/cutfruit/shadow.png');
        this.load.image('x', 'assets/cutfruit/x.png');
        this.load.image('xf', 'assets/cutfruit/xf.png');
        this.load.image('xx', 'assets/cutfruit/xx.png');
        this.load.image('xxf', 'assets/cutfruit/xxf.png');
        this.load.image('xxx', 'assets/cutfruit/xxx.png');
        this.load.image('xxxf', 'assets/cutfruit/xxxf.png');
        this.load.bitmapFont('number', 'assets/cutfruit/bitmapFont.png', 'assets/cutfruit/bitmapFont.xml');
        const textures = new FruitTexture()
        textures.init(this.textures)
        const bomb_textures = new BombTexture()
        bomb_textures.init(this.textures)
    }

    create() {
        this.bg = this.add.image(180 * scaleRatio, 240 * scaleRatio, 'background');
        this.bg.setScale(assetScale)
        this.blade = new Blade(this)
        this.blade.setAllowBlade()
        this.fruits = []
        this.bombExplode = false
        this.lostCount = 0
        this.score = 0
        this.playing = true
        this.scoreAnim();
        this.scoreTextAnim();
        this.xxxAnim();
        this.physics.world.setBounds(-100*scaleRatio, -100*scaleRatio, 560*scaleRatio, 680*scaleRatio)
        this.physics.world.on('worldbounds', (body:Phaser.Physics.Arcade.Body) => {
            const gameObj = body.gameObject
            gameObj.destroy()
        })
    }

    scoreAnim() {
        this.scoreImage = this.add.image(-16 * scaleRatio, (8 + 16) * scaleRatio, 'score');
        this.scoreImage.setScale(assetScale)
        this.scoreImage.x = -this.scoreImage.width;
        this.tweens.add({
            targets: this.scoreImage,
            props: {
                x: (8 + 16) * scaleRatio
            },
            delay: 0,
            duration: 300,
            ease: "Sine.easeInOut"
        })
    }

    scoreTextAnim() {
        this.scoreText = this.add.bitmapText(-25 * scaleRatio, 8 * scaleRatio, 'number', this.score + '', 25 * scaleRatio);
        this.scoreText.setOrigin(0, 0)
        this.scoreText.text = this.score + '';
        this.tweens.add({
            targets: this.scoreText,
            props: {
                x: 44 * scaleRatio
            },
            delay: 0,
            duration: 300,
            ease: "Sine.easeInOut"
        })
    }

    xxxAnim() {
        if(this.showXXX){
            this.xxxGroup = this.add.group();
            this.xxxGroup.setOrigin(0, 0)
            const x = this.add.image(0, 0, 'x');
            x.setScale(assetScale)
            x.setOrigin(0, 0)
            const xf = this.add.image(0, 0, 'xf')
            xf.setScale(assetScale)
            xf.setOrigin(0, 0)
            xf.setAlpha(0)
            this.lostScoreSprites.push(x)
            this.lostScoreSprites.push(xf)
            const xx = this.add.image(22 * scaleRatio, 0, 'xx');
            xx.setScale(assetScale)
            xx.setOrigin(0, 0)
            const xxf = this.add.image(22 * scaleRatio, 0, 'xxf');
            xxf.setScale(assetScale)
            xxf.setOrigin(0, 0)
            xxf.setAlpha(0)
            this.lostScoreSprites.push(xx)
            this.lostScoreSprites.push(xxf)
            const xxx = this.add.image(49 * scaleRatio, 0, 'xxx');
            xxx.setScale(assetScale)
            xxx.setOrigin(0, 0)
            const xxxf = this.add.image(49 * scaleRatio, 0, 'xxxf');
            xxxf.setScale(assetScale)
            xxxf.setOrigin(0, 0)
            xxxf.setAlpha(0)
            this.lostScoreSprites.push(xxx)
            this.lostScoreSprites.push(xxxf)
            this.xxxGroup.add(x);
            this.xxxGroup.add(xx);
            this.xxxGroup.add(xxx);
            this.xxxGroup.add(xf);
            this.xxxGroup.add(xxf);
            this.xxxGroup.add(xxxf);
            this.xxxGroup.incXY(360 * scaleRatio, 8 * scaleRatio)
            this.tweens.add({
                targets: this.xxxGroup.children.entries,
                props: {
                    x: `-=${89 * scaleRatio}`
                },
                delay: 0,
                duration: 300,
                ease: "Sine,easeInOut"
            })
        }
    }

    renderLost() {
        if(this.showXXX){
            if(this.lostCount >= 1){
                this.lostScoreSprites[0].setAlpha(0)
                this.lostScoreSprites[1].setAlpha(1)
            }
            if(this.lostCount >= 2){
                this.lostScoreSprites[2].setAlpha(0)
                this.lostScoreSprites[3].setAlpha(1)
            }
            if(this.lostCount >= 3){
                this.lostScoreSprites[4].setAlpha(0)
                this.lostScoreSprites[5].setAlpha(1)
            }
        }
    }

    update() {
        this.blade?.update()
        if (!this.bombExplode) {
            const fruits = this.fruits
            const inworldFruits = this.fruits.filter((fruit) => {
                if (fruit.sprite && fruit.sprite.body) {
                    if ((fruit.sprite.body.velocity.y > 0 && fruit.sprite.y > 480 * scaleRatio) ||
                        (fruit.sprite.body.velocity.x > 0 && fruit.sprite.x > 360 * scaleRatio) ||
                        (fruit.sprite.body.velocity.x < 0 && fruit.sprite.x < 0)) {
                        return false
                    }
                }
                return true
            })
            this.fruits = inworldFruits
            for (const fruit of fruits) {
                if (!inworldFruits.includes(fruit)) {
                    if (fruit instanceof Fruit) {
                        this.onOut(fruit)
                    }
                    fruit.destroy()
                }
            }
        }
        if (this.playing && this.fruits.length == 0 && !this.bombExplode) {
            this.startFruit();
        }
        if (!this.bombExplode) {
            for (var i = 0; i < this.fruits.length; i++) {
                var fruit = this.fruits[i];
                this.blade?.checkCollide(fruit.sprite, (deg: number) => {
                    if (fruit instanceof Fruit) {
                        this.onKill(fruit, deg);
                    } else {
                        this.onBomb(fruit);
                    }
                });
            }
        }
        this.checkState()
    }

    checkState() {
    }

    startFruit() {
        var number = randomMinMax(1, 5);
        var hasBomb = Math.floor(Math.random() * 2);
        var bombIndex = -1;
        if (this.config.has_bomb && hasBomb) {
            bombIndex = Math.floor(Math.random() * number);
        }
        for (var i = 0; i < number; i++) {
            if (i == bombIndex) {
                this.fruits.push(this.randomFruit(false));
            } else {
                this.fruits.push(this.randomFruit(true));
            }
        }
    }

    randomFruit(isFruit: boolean) {
        var fruitArray = ["apple", "banana", "basaha", "peach", "sandia"];
        var index = Math.floor(Math.random() * fruitArray.length);
        var x = randomPosX(360 * scaleRatio);
        var y = randomPosY(480 * scaleRatio);
        var vx = randomVelocityX(x, 360 * scaleRatio);
        var vy = randomVelocityY();
        var fruit;

        if (isFruit) {
            fruit = new Fruit(fruitArray[index], this);
            const angle = randomMinMax(0, 180)
            fruit.sprite.angle = angle
        } else {
            fruit = new Bomb(this);
        }
        fruit.sprite.x = x
        fruit.sprite.y = y
        fruit.sprite.body.velocity.x = vx;
        fruit.sprite.body.velocity.y = vy;
        fruit.sprite.body.gravity.y = this.gravity
        return fruit;
    }

    onOut(fruit: Fruit | Bomb) {
        var x;
        var y;
        const height = 480 * scaleRatio
        const width = 360 * scaleRatio
        // 从下面出去
        if (fruit.sprite.y > height) {
            x = fruit.sprite.x;
            y = height - 30 * scaleRatio;
        } else if (fruit.sprite.x < 0) {
            // 从左边出去
            x = 30 * scaleRatio;
            y = fruit.sprite.y;
        } else {
            // 从右边出去
            x = width - 30 * scaleRatio;
            y = fruit.sprite.y;
        }
        var lose = this.add.sprite(x, y, 'lose');
        lose.setScale(0.0, 0.0);
        this.tweens.add({
            props: {
                scaleX: assetScale,
                scaleY: assetScale
            },
            targets: [lose],
            duration: 300,
            delay: 0,
            ease: 'Sine.easeInOut',
            yoyo: true,
            onComplete: () => {
                lose.destroy()
            }
        })
        if (fruit instanceof Fruit) {
            this.lostCount++
            this.renderLost()
            if(this.config.max_lost > 0 && this.lostCount >= this.config.max_lost){
                this.gameOver()
            }
        }

    }

    onKill(fruit: Fruit, deg:number) {
        fruit.half(deg, true);
        this.score = this.score + 1;
        if (this.scoreText) {
            this.scoreText.text = this.score + '';
        }
        this.fruits.splice(this.fruits.indexOf(fruit), 1)
        if(this.report_played){
            this.emitter_cb('played', {})
            this.report_played = false
        }
    }

    onBomb(bomb: Bomb) {
        this.bombExplode = true;
        for (var i = 0; i < this.fruits.length; i++) {
            this.fruits[i].sprite.body.gravity.y = 0;
            this.fruits[i].sprite.body.velocity.y = 0;
            this.fruits[i].sprite.body.velocity.x = 0;
        }
        bomb.explode(() => {
            for (var i = 0; i < this.fruits.length; i++) {
                this.fruits[i].destroy();
            }
            this.fruits.splice(0, this.fruits.length);
        },
            () => {
                this.gameOver();
            })
    }

    gameOver() {
        if(this.playing === false){
            return
        }
        this.playing = false;
        const gameOverSprite = this.add.sprite(180 * scaleRatio, 240 * scaleRatio, 'game-over');
        gameOverSprite.setScale(0);
        this.tweens.add({
            targets: gameOverSprite,
            props: {
                scaleX: assetScale,
                scaleY: assetScale
            },
            delay: 0,
            duration: 300,
            ease: "Sine.easeInOut"
        })
        this.notify_cb({
            succeed: true,
            archievement: {
                rating: 3,
                score: this.score
            },
            level: this.level_info
        })
    }

    apply(name: string) {
        return {
            ok: false,
            message: "这个功能暂时还支持不了"
        }
    }

    canApply(name: string): ConditionResponse{
        return {
            ok: false,
            message: "无法支持该动作"
        }
    }
}


const gameConfig = {
    type: Phaser.AUTO,
    width: 360 * scaleRatio,
    height: 480 * scaleRatio,
    canvasStyle: `width: 360px;height:480px`,
    parent: "playable-container",
    physics: {
        default: 'arcade',
        arcade: {
            debug: false,
        },
    },
    disableContextMenu: true,
    transparent: true

}
export const CutFruitPlayable = defineComponent({
    name: "CutFruitPlayable",
    props: {
        config: { type: Object as PropType<CutFruitConfig>, required: true },
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
            const scene = this.$options.game.scene.getScene("CutFruitScene") as CutFruitScene
            return scene.apply(name)
        },

        canApply(name: string){
            const scene = this.$options.game.scene.getScene("CutFruitScene") as CutFruitScene
            return scene.canApply(name)
        },

        createGame() {
            const game = new Phaser.Game({...this.gameConfig})
            this.$options.game = game
            game.scene.add('CutFruitScene', new CutFruitScene(this.config, this.level, (played: PlayableResult)=>{
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
        return h('div', { "id": "playable-container", style: {} })
    }
})

export default CutFruitPlayable;
