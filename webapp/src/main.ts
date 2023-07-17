import { createHighOrderApp, app_platform, modal_helper, AdReady, AdOptions, AdPlugin } from '@highorder/app'
import { CapacitorHttp, HttpHeaders, HttpResponse } from '@capacitor/core';
import { WeChatPlugin } from '@highorder/app/src/platform';

class WebAdSimulationPlugin {
    adNum: number = 0
    modal_helper: any = undefined

    async initialize(options: Record<string, any>): Promise<void> {
        console.log('WebAdSimulationPlugin initialize', options)
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
                    text: "Ad not supported in webapp. This is a fake interstitial Ad.",
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

    async prepareReward(options: AdOptions): Promise<void>{
        this.adNum += 1
    }

    async showReward(options: AdOptions): Promise<void>{
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

    async isRewardReady(options: AdOptions): Promise<AdReady>{
        return { ready: this.adNum > 0 }
    }
}

class DefaultWebWeCahtSimulationPlugin {

    async initialize(options: {appId: string, merchantId?:string}): Promise<void> {
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

export class WebAppHostPlatform {
    adPlugins: Record<string, AdPlugin> = {}
    wechatPlugin: WeChatPlugin

    constructor(){
        this.wechatPlugin = new DefaultWebWeCahtSimulationPlugin();
    }

    async initialize(options: Record<string, any>): Promise<void> {
    }

    exitApp(){

    }

    openUrl(url: string) {
        window.open(url, '_blank');
    }

    getPlatform() {
        return {
            "name": "web",
            "vendor": "unknown"
        }
    }

    getAdPluginInstance(vendor: string) {
        if (!this.adPlugins.hasOwnProperty(vendor)) {
            this.adPlugins[vendor] = new WebAdSimulationPlugin()
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

app_platform.register(new WebAppHostPlatform())
const app_configs = []

function getSearchParameters(): Record<string, any> {
    const paramstr = window.location.search.slice(1);
    return paramstr != null && paramstr != "" ? transformToOject(paramstr) : {};
}

function transformToOject( paramstr:string ) {
    var params:Record<string, any> = {};
    var prmarr = paramstr.split("&");
    for ( var i = 0; i < prmarr.length; i++) {
        var tmparr = prmarr[i].split("=");
        params[tmparr[0].trim()] = decodeURIComponent(tmparr[1]).trim();
    }
    return params;
}

const options = getSearchParameters();

const  highorder_app_config = {
    appId: options.app_id ?? "",
    baseUrl: options.base_url ?? "",
    privacyUrl: options.privacy_url ?? `/static/APP_${options.app_id}/content/main/privacy.html`,
    clientKey: options.client_key ?? "",
    clientSecret: options.client_secret ?? ""
}

console.log(highorder_app_config)

app_configs.push(highorder_app_config)

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
        console.log('request', req)
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

    const tag = `CapacitorHttp fetch ${Date.now()} ${resource}`;
    console.time(tag);
    try {
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
        return Promise.reject(error);
    }
};

// app_platform.setCustomFetch(cap_fetch)

createHighOrderApp(app_configs, {}).then((app: any) => {
    app.mount('#app')
})
