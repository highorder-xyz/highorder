
export interface AppPlatformInterface {
    initialize: (options: Record<string, any>) => Promise<void>
    exitApp: () => void
    openUrl: (url:string) => void
    mustAgreePrivacy: () => boolean
    getPlatform: () => Record<string | 'name', any>
    getAdPluginInstance: (vendor: string) => AdPlugin | undefined
    getWeChatPluginInstance:() => WeChatPlugin | undefined
    setUser: ( user_id: string, property: Record<string, string>) => Promise<void>
    logEvent: ( name: string, params: Record<string, unknown> ) => Promise<void>

}

export interface AdPlugin {
    initialize(options: AdInitializationOptions): Promise<void>;
    prepareInterstitial(options: AdOptions): Promise<void>;
    showInterstitial(options: AdOptions): Promise<void>;
    isInterstitialReady(options: AdOptions): Promise<AdReady>;
    prepareReward(options: AdOptions): Promise<void>;
    showReward(options: AdOptions): Promise<void>;
    isRewardReady(options: AdOptions): Promise<AdReady>;
}

export interface WeChatPlugin {
    initialize(options: {appId: string, merchantId?:string, universalLink?:string}): Promise<void>
    pay(options: { prepayId: string, packageValue: string, nonceStr: string, timeStamp: string, sign: string }): Promise<{value: string}>;
    isInstalled(): Promise<{ installed: boolean }>;
    shareText(options: { text: string, scene: string }): Promise<any>;
    shareLink(options: { url: string, title: string, description: string, thumb?: string, scene: number }): Promise<any>;
    shareImage(options: { image: string, title: string, description: string, scene: number }): Promise<any>;
    shareMiniProgram(options: { webpageUrl: string, userName: string, path: string, hdImageData: string, withShareTicket: boolean, miniProgramType: number, title: string, description: string, scene: number }): Promise<any>;
    launchMiniProgram(options: { userName: string, path: string, miniProgramType: number }): Promise<any>;
    sendAuthRequest(options: { scope: string, state: string }): Promise<any>;
    wxOpenCustomerServiceChat(options: { corpId: string, url: string }): Promise<any>;
}

export interface AdInitializationOptions {
    appId: string;
    appName: string;
}

export interface AdReady {
    ready: boolean;
}

export interface AdOptions {
    codeId: string;
    fullscreen: boolean;
    isTesting?: boolean;
}

export interface AdRuntimeError {
    /**
     * Gets the error's code.
     */
    code: number;
    /**
     * Gets the message describing the error.
     */
    message: string;
}

class AppHostPlatform {
    host!: AppPlatformInterface
    init_options: Record<string, any> = {}
    inited: boolean = false
    custom_fetch: ((input: RequestInfo, init?: RequestInit) => Promise<Response>) | undefined

    constructor(){
    }

    async initialize(options: Record<string, any>): Promise<void>{
        if(this.inited){
            return
        }
        this.init_options = options
        await this.host.initialize(options)
        this.inited = true
    }

    exitApp() {
        return this.host.exitApp();
    }

    getPlatform() {
        return this.host.getPlatform()
    }

    getTheme() {
        return this.init_options.theme ?? undefined
    }

    mustAgreePrivacy() {
        return this.host.mustAgreePrivacy()
    }

    getFetch() {
        return this.custom_fetch ?? window.fetch
    }

    register(host: AppPlatformInterface){
        this.host = host
    }

    getAdPluginInstance(vendor: string) {
        return this.host.getAdPluginInstance(vendor)
    }

    getWeChatPluginInstance() {
        return this.host.getWeChatPluginInstance()
    }


    setCustomFetch(custom_fetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>) {
        this.custom_fetch = custom_fetch
    }

    getFunction(name:keyof AppPlatformInterface) {
        if(this.host && this.host.hasOwnProperty(name)){
            const attr = this.host[name]
            if(typeof attr == 'function'){
                return attr
            }
        }
        return undefined
    }

    openUrl(url:string):void {
        this.host.openUrl(url)
    }

    async setUser(user_id: string, property: Record<string, string>) {
        await this.host.setUser(user_id, property)
    }

    async logEvent( name: string, params: Record<string, unknown> ){
        // console.log('log_event', name)
        await this.host.logEvent(name, params)
    }
}

export const app_platform = new AppHostPlatform()