
import * as Config from './config.json'
import { createHighOrderApp, app_platform, AdReady, AdOptions, AdPlugin, AppConfig, WeChatPlugin } from '@highorder/app'
import { App as CapacitorApp } from '@capacitor/app';
import { Browser } from '@capacitor/browser';
import { Device } from '@capacitor/device';

import { CapacitorHttp, HttpHeaders, HttpResponse } from '@capacitor/core';


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

export class CapacitorAppHostPlatform {
    adPlugins: Record<string, AdPlugin> = {}
    wechatPlugin: WeChatPlugin | undefined
    platform: string
    vendor: string
    inited: boolean
    initOptions: Record<string, any> = {}

    constructor(platform: string, vendor:string) {
        this.platform = platform
        this.vendor = vendor.toLowerCase()
        console.log('CapacitorAppHostPlatform construct')
        this.inited = false
        console.log('CapacitorAppHostPlatform construct end.')
    }

    async initialize(options: Record<string, any>): Promise<void> {
        console.log('CapacitorAppHostPlatform initialize start.')
        if(this.wechatPlugin){
            await this.wechatPlugin.initialize({appId:Config.wechat.appId, merchantId: Config.wechat.merchantId, universalLink: Config.wechat.universalLink});
        }
        this.inited = true
        console.log('CapacitorAppHostPlatform initialize end.')
    }

    exitApp(){
        CapacitorApp.exitApp();
    }

    openUrl(url: string) {
        Browser.open({ url: url })
    }

    mustAgreePrivacy() {
        return false;
    }

    getPlatform() {
        const uaFields = getUserAgent()
        const languageTag = getLanguageTag()
        const screenSize = getScreenSize()
        return {
            "name": this.platform,
            "vendor": this.vendor,
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
        console.log('getAdPluginInstance: ', vendor, this.adPlugins)
        return this.adPlugins[vendor]
    }

    getWeChatPluginInstance() {
        return this.wechatPlugin;
    }


    async setUser(user_id: string, property: Record<string, string>) {
        if(this.inited){
            // await setup user info,
        } else {
            this.initOptions.user_id = user_id
            this.initOptions.user_property = property
        }

    }

    async logEvent(name: string, params: Record<string, unknown>) {
        // await Analytics.logEvent({ name: name, params: params })
    }
}


CapacitorApp.addListener('backButton', ({ canGoBack }) => {
    if (!canGoBack) {
        CapacitorApp.exitApp();
    } else {
        window.history.back();
    }
});


async function cap_fetch(resource: RequestInfo,  options?: RequestInit){
    let originFetch = window.fetch;
    let url:string = resource.toString();
    let method = options?.method ? options.method : undefined
    let body = options?.body ? options.body : undefined
    let headers = options?.headers;
    if (options?.headers instanceof Headers) {
        headers = Object.fromEntries((options.headers as any).entries());
    }

    if(resource instanceof Request){
        let req = resource as Request
        url = req.url;
        method = req.method
        body = await req.text()
        headers = Object.fromEntries((req.headers as any).entries())
    }

    if (
        !(
            url.startsWith('http:') ||
            url.startsWith('https:')
        )
    ) {
        return originFetch(resource, options);
    }

    const tag = `custom http fetch ${Date.now()} ${resource}`;
    console.time(tag);
    try {
        console.log('cap_fetch, ', url)
        const nativeResponse: HttpResponse = await CapacitorHttp.request(
            {
                url: url,
                method: method,
                data: body,
                headers: headers as HttpHeaders,
            }
        );

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
        console.log(`fetch error: ${error}`)
        return Promise.reject(error);
    }
};


async function bootup() {
    const info = await Device.getInfo()
    const platform = info.platform
    app_platform.setCustomFetch(cap_fetch)
    app_platform.register(new CapacitorAppHostPlatform(platform, info.manufacturer))
}


bootup().then(() => {
    const app_config = Config.app
    if(import.meta.env.VITE_SERVICE_URL){
        console.log(`env ${import.meta.env.VITE_SERVICE_URL}`)
        app_config.baseUrl = import.meta.env.VITE_SERVICE_URL
    }
    createHighOrderApp([Config.app], {}).then((app) => { app.mount('#app') })
})


