import {createApp, defineAsyncComponent} from 'vue'
import {App} from './app'
import './index.css'
import { AppCore, AppConfig} from "./core"
import { app_platform } from './platform'

export type { AppConfig } from './core'
export { app_platform } from './platform'
export { modal_helper } from './app'
export type { AppPlatformInterface, AdReady, AdOptions, AdPlugin, WeChatPlugin} from './platform'

export async function bootup(app_configs: AppConfig[], init_options:Record<string, any>): Promise<void> {
    for(const config of app_configs){
        AppCore.addAppConfig(config)
    }
    await AppCore.init()
    const app_id = app_configs[0].appId
    await AppCore.switchTo(app_id)
    const app_core = AppCore.getCore(app_id)
    if(app_core.privacy_agreed){
        await app_platform.initialize(init_options)
    } else {
        app_platform.init_options = init_options
    }
}

export async function createHighOrderApp(app_configs: AppConfig[], init_options:Record<string, any> = {}) {
    const app = createApp(App)

    app.component('SeaSunsetMotion', defineAsyncComponent(async () =>{
        const SeaSunsetMotion = await import('./motion/sea_sunset.js')
        return SeaSunsetMotion
    }))

    app.component('SeaBirdMotion', defineAsyncComponent(async () =>{
        const SeaBirdMotion = await import('./motion/sea_bird.js')
        return SeaBirdMotion
    }))

    app.component('BookFlipMotion', defineAsyncComponent(async () =>{
        const BookFlipMotion = await import('./motion/book_flip.vue')
        return BookFlipMotion
    }))

    app.component('SleepCatMotion', defineAsyncComponent(async () =>{
        const SleepCatMotion = await import('./motion/sleep_cat.vue')
        return SleepCatMotion
    }))

    app.component('WallVinesMotion', defineAsyncComponent(async () =>{
        const WallVinesMotion = await import('./motion/wall_vines.vue')
        return WallVinesMotion
    }))

    app.component('WallGrassMotion', defineAsyncComponent(async () =>{
        const WallGrassMotion = await import('./motion/wall_grass.vue')
        return WallGrassMotion
    }))

    app.component('OnePictureMotion', defineAsyncComponent(async () =>{
        const OnePictureMotion = await import('./motion/one_picture.vue')
        return OnePictureMotion
    }))


    app.component('WordFigureOut', defineAsyncComponent(async () =>{
        const WordFigureOut = await import('./playable/word_figureout.js')
        return WordFigureOut
    }))

    app.component('ChengyuWordle', defineAsyncComponent(async () =>{
        const ChengyuWordle = await import('./playable/chengyu_wordle.js')
        return ChengyuWordle
    }))

    app.component('Threetiles', defineAsyncComponent(async () =>{
        const Threetiles = await import('./playable/threetiles.js')
        return Threetiles
    }))

    app.component('Catchcat', defineAsyncComponent(async () =>{
        const Catchcat = await import('./playable/catchcat.js')
        return Catchcat
    }))

    app.component('ChengyuCross', defineAsyncComponent(async () =>{
        const ChengyuCross = await import('./playable/chengyu_cross.js')
        return ChengyuCross
    }))

    app.component('ChengyuRelay', defineAsyncComponent(async () =>{
        const ChengyuRelay = await import('./playable/chengyu_relay.js')
        return ChengyuRelay
    }))

    app.component('ShiciBlank', defineAsyncComponent(async () =>{
        const ShiciBlank = await import('./playable/shici_blank.js')
        return ShiciBlank
    }))

    app.component('Cutfruit', defineAsyncComponent(async () =>{
        const Cutfruit = await import('./playable/cutfruit.js')
        return Cutfruit
    }))

    app.component('RotateRight', defineAsyncComponent(async () =>{
        const RotateRight = await import('./playable/rotate_right.js')
        return RotateRight
    }))

    await bootup(app_configs, init_options)
    return app
}

