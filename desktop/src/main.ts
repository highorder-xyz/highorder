import { createHighOrderApp, app_platform, modal_helper, AdReady, AdOptions, AdPlugin, WeChatPlugin} from '@highorder/app'
import { Body, HttpVerb, fetch } from '@tauri-apps/api/http';
import * as AppConf from './app.conf.json'

declare global {
    interface Navigator {
        getBattery: any;
        oscpu: any;
    }

    interface Window {
        InstallTrigger?: any;
        ApplePaySession?: any;
        chrome?: any;
        MSStream?: any;
    }
}

class DesktopAdSimulationPlugin {
    adNum: number = 0
    modal_helper: any = undefined

    async initialize(options: Record<string, any>): Promise<void> {
        console.log('DesktopAdSimulationPlugin initialize', options)
        this.modal_helper = modal_helper
    }

    async prepareInterstitial(options: AdOptions): Promise<void> {
        this.adNum += 1
    }

    async showInterstitial(): Promise<void> {
        if (this.modal_helper) {
            await new Promise<void>((resolve, reject) => {
                this.modal_helper.open_any({
                    title: "Interstitial Ad",
                    text: "Ad not supported in desktop. This is a fake interstitial Ad.",
                    actionConfirmText: "close",
                    onModalConfirmed: () => {
                        resolve()
                    }
                })
            });
        }

        if (this.adNum > 0)
            this.adNum -= 1
    }

    async isInterstitialReady(): Promise<AdReady> {
        return { ready: this.adNum > 0 }
    }

    async prepareReward(options: AdOptions): Promise<void> {
        this.adNum += 1
    }

    async showReward(options: AdOptions): Promise<void> {
        if (this.modal_helper) {
            await new Promise<void>((resolve, reject) => {
                this.modal_helper.open_any({
                    title: "Reward Ad",
                    text: "Ad not supported in webapp. This is a fake interstitial Ad.",
                    actionConfirmText: "close",
                    onModalConfirmed: () => {
                        resolve()
                    }
                })
            })
        }

        if (this.adNum > 0)
            this.adNum -= 1
    }

    async isRewardReady(options: AdOptions): Promise<AdReady> {
        return { ready: this.adNum > 0 }
    }
}

class DefaultDesktopWeChatSimulationPlugin {

    async initialize(options: { appId: string, merchantId?: string }): Promise<void> {
    }

    async isInstalled(): Promise<{ installed: boolean }> {
        return { installed: false }
    }

    async pay(payParam: { prepayId: string; packageValue: string; nonceStr: string; timeStamp: string; sign: string }): Promise<{ value: string }> {
        console.log(payParam);
        return { value: '' };
    }

    async launchMiniProgram(options: { userName: string; path: string; miniProgramType: number }): Promise<void> {
        console.log(options);
    }

    async shareImage(options: { image: string; title: string; description: string; scene: number }): Promise<void> {
        console.log(options);
    }

    async shareLink(options: { url: string; title: string; description: string; thumb?: string; scene: number }): Promise<void> {
        console.log(options);
    }

    async shareMiniProgram(options: { webpageUrl: string; userName: string; path: string; hdImageData: string; withShareTicket: boolean; miniProgramType: number; title: string; description: string; scene: number }): Promise<void> {
        console.log(options);
    }

    async shareText(options: { text: string; scene: string }): Promise<void> {
        console.log(options);
    }

    async sendAuthRequest(options: { scope: string; state: string }): Promise<void> {
        console.log(options);
    }

    async wxOpenCustomerServiceChat(options: { corpId: string; url: string }): Promise<any> {
        console.log(options);
    }
}

function getUserAgent() {
    const ua = navigator.userAgent;
    const uaFields: any = {};
    const start = ua.indexOf('(') + 1;
    let end = ua.indexOf(') AppleWebKit');
    if (ua.indexOf(') Gecko') !== -1) {
        end = ua.indexOf(') Gecko');
    }
    const fields = ua.substring(start, end);
    if (ua.indexOf('Android') !== -1) {
        const tmpFields = fields.replace('; wv', '').split('; ').pop();
        if (tmpFields) {
            uaFields.model = tmpFields.split(' Build')[0];
        }
        uaFields.osVersion = fields.split('; ')[1];
    } else {
        uaFields.model = fields.split('; ')[0];
        if (typeof navigator !== 'undefined' && navigator.oscpu) {
            uaFields.osVersion = navigator.oscpu;
        } else {
            if (ua.indexOf('Windows') !== -1) {
                uaFields.osVersion = fields;
            } else {
                const tmpFields = fields.split('; ').pop();
                if (tmpFields) {
                    const lastParts = tmpFields
                        .replace(' like Mac OS X', '')
                        .split(' ');
                    uaFields.osVersion = lastParts[lastParts.length - 1].replace(
                        /_/g,
                        '.',
                    );
                }
            }
        }
    }

    if (/android/i.test(ua)) {
        uaFields.operatingSystem = 'android';
    } else if (/iPad|iPhone|iPod/.test(ua) && !window.MSStream) {
        uaFields.operatingSystem = 'ios';
    } else if (/Win/.test(ua)) {
        uaFields.operatingSystem = 'windows';
    } else if (/Mac/i.test(ua)) {
        uaFields.operatingSystem = 'mac';
    } else {
        uaFields.operatingSystem = 'unknown';
    }

    // Check for browsers based on non-standard javascript apis, only not user agent
    const isSafari = !!window.ApplePaySession;
    const isChrome = !!window.chrome;
    const isFirefox = /Firefox/.test(ua);
    const isEdge = /Edg/.test(ua);
    const isFirefoxIOS = /FxiOS/.test(ua);
    const isChromeIOS = /CriOS/.test(ua);
    const isEdgeIOS = /EdgiOS/.test(ua);

    // FF and Edge User Agents both end with "/MAJOR.MINOR"
    if (
        isSafari ||
        (isChrome && !isEdge) ||
        isFirefoxIOS ||
        isChromeIOS ||
        isEdgeIOS
    ) {
        // Safari version comes as     "... Version/MAJOR.MINOR ..."
        // Chrome version comes as     "... Chrome/MAJOR.MINOR ..."
        // FirefoxIOS version comes as "... FxiOS/MAJOR.MINOR ..."
        // ChromeIOS version comes as  "... CriOS/MAJOR.MINOR ..."
        let searchWord: string;
        if (isFirefoxIOS) {
            searchWord = 'FxiOS';
        } else if (isChromeIOS) {
            searchWord = 'CriOS';
        } else if (isEdgeIOS) {
            searchWord = 'EdgiOS';
        } else if (isSafari) {
            searchWord = 'Version';
        } else {
            searchWord = 'Chrome';
        }

        const words = ua.split(' ');
        for (const word of words) {
            if (word.includes(searchWord)) {
                const version = word.split('/')[1];
                uaFields.browserVersion = version;
            }
        }
    } else if (isFirefox || isEdge) {
        const reverseUA = ua.split('').reverse().join('');
        const reverseVersion = reverseUA.split('/')[0];
        const version = reverseVersion.split('').reverse().join('');
        uaFields.browserVersion = version;
    }

    return uaFields;
}

function getLanguageTag() {
    if (navigator.language) {
        return navigator.language;
    }
    return undefined
}

function getScreenSize() {
    if (window && window.screen) {
        const w = window.screen.width
        const h = window.screen.height
        return {
            "width": w,
            "height": h
        }
    }
    return {
        "width": -1,
        "height": -1
    }
}

function getPageSize() {
    if (typeof window !== 'undefined') {
        const w = window.innerWidth
        const h = window.innerHeight
        return {
            "width": w,
            "height": h
        }
    }
    return {
        "width": -1,
        "height": -1
    }
}

export class DesktopAppHostPlatform {
    adPlugins: Record<string, AdPlugin> = {}
    wechatPlugin: WeChatPlugin

    constructor() {
        this.wechatPlugin = new DefaultDesktopWeChatSimulationPlugin();
    }

    async initialize(options: Record<string, any>): Promise<void> {
    }

    exitApp() {

    }

    openUrl(url: string) {
        window.open(url, '_blank');
    }

    mustAgreePrivacy() {
        return false;
    }

    getPlatform() {
        const uaFields = getUserAgent()
        const languageTag = getLanguageTag()
        const screenSize = getScreenSize()
        return {
            "name": "desktop",
            "vendor": "unknown",
            "os": uaFields.operatingSystem,
            "os_version": uaFields.osVersion,
            "language": languageTag,
            "screen_size": screenSize,
            "page_size": getPageSize(),
            "is_virtual": false,
            "web_version": uaFields.browserVersion,
        }
    }

    getAdPluginInstance(vendor: string) {
        if (!this.adPlugins.hasOwnProperty(vendor)) {
            this.adPlugins[vendor] = new DesktopAdSimulationPlugin()
        }
        return this.adPlugins[vendor]
    }

    getWeChatPluginInstance() {
        return this.wechatPlugin;
    }


    async setUser(user_id: string, property: Record<string, string>) {

    }

    async logEvent(name: string, params: Record<string, unknown>) {
        console.log('AnalyticsEvent', name, params)
    }
}

app_platform.register(new DesktopAppHostPlatform())
const app_configs = []

const options = AppConf.app

const highorder_app_config = {
    appId: options.appId ?? "",
    baseUrl: options.baseUrl ?? "",
    privacyUrl: options.privacyUrl ?? `/static/APP_${options.appId}/content/main/privacy.html`,
    clientKey: options.clientKey ?? "",
    clientSecret: options.clientSecret ?? ""
}

console.log(highorder_app_config)

app_configs.push(highorder_app_config)

async function tauri_fetch(resource: RequestInfo, options?: RequestInit) {
    let originFetch = window.fetch;
    let url: string = resource.toString();
    let method = options?.method ? options.method : undefined
    let body = options?.body ? options.body : ""
    if (body !== undefined){
        body = body.toString()
    }
    let headers = options?.headers;
    if (options?.headers instanceof Headers) {
        headers = Object.fromEntries((options.headers as any).entries());
    }

    if (resource instanceof Request) {
        let req = resource as Request
        console.log('request', req)
        url = req.url;
        method = req.method
        body = await req.text()
        headers = Object.fromEntries((req.headers as any).entries())
    } else {

    }

    if (
        !(
            url.startsWith('http:') ||
            url.startsWith('https:')
        )
    ) {
        return originFetch(resource, options);
    }

    const tag = `TauriHttp fetch ${Date.now()} ${resource}`;
    console.time(tag);
    try {
        const nativeResponse = await fetch(url, {
            method: method as HttpVerb,
            body: Body.text(body),
            headers: headers
        });
        const data =
            typeof nativeResponse.data === 'string'
                ? nativeResponse.data
                : JSON.stringify(nativeResponse.data);
        // intercept & parse response before returning
        const response = new Response(data, {
            headers: nativeResponse.headers,
            status: nativeResponse.status,
        });

        console.timeEnd(tag);
        return response;
    } catch (error) {
        console.timeEnd(tag);
        return Promise.reject(error);
    }
};

app_platform.setCustomFetch(tauri_fetch)

createHighOrderApp(app_configs, {}).then((app: any) => {
    app.mount('#app')
})
