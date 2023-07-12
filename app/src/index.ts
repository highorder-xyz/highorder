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

    await bootup(app_configs, init_options)
    return app
}

