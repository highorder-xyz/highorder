
import { ModalHelper } from './app'
import { AdOptions, AdPlugin, app_platform } from './platform';


export interface AdUnitConfigInterface{
    codeId: string,
    fullscreen?: boolean,
    ad_type?: string
}

export interface AdAppConfigInterface{
    vendor:string
    appId:string
    appName:string
    units: Array<AdUnitConfigInterface>,
    minPreparedAdCount?: number
}

interface AdUnitInfo{
    ad_type: string,
    ad_vendor: string,
    ad_app: string,
    ad_code: string,
    fullscreen: boolean
}

interface AdUnitOption{
    ad_type?: string,
    ad_vendor?: string,
    ad_code: string
}

export interface AdShowOptions{
    ad_vendor: string
    ad_type?: string
    ad_hint?: string[]
    ad_code?: string
    ad_confirm?: string
    ad_candidates?: Array<AdUnitOption>
}


export class AdManager {
    static instances: Record<string, AdManager>  = {}
    static adunits: Record<string, AdUnitInfo> = {}

    primaryConfig: AdAppConfigInterface
    primaryAd: AdPlugin
    minPreparedAd: number

    static async initAd(ad_config:Record<string, any>){
        console.log('AdManager initAd:', ad_config)
        const vendor: string = ad_config.vendor;
        let options = {appId: ad_config.appId, appName:ad_config.appName}

        const adplugin = app_platform.getAdPluginInstance(vendor)
        console.log('AdManager. adplugin', adplugin)
        if(adplugin){
            try{
                await adplugin.initialize(options)
                console.log('AdManager, initialize returns.')
                const admanager = new AdManager(ad_config as AdAppConfigInterface, adplugin)
                AdManager.instances[vendor] = admanager
                for(const unit of ad_config.units){
                    const codeId = unit.codeId
                    const ad_type = unit.ad_type ?? 'interstitial'
                    const fullscreen = unit.fullscreen ?? false
                    AdManager.adunits[codeId] = {
                        ad_vendor: vendor,
                        ad_code: codeId,
                        ad_type: ad_type,
                        ad_app: ad_config.appId,
                        fullscreen: fullscreen
                    }
                    console.log(unit)
                }
                await admanager.prepare()
                console.log(`AdManager for vendor ${vendor} inited ok.`, options)
            }
            catch(error) {
                console.log(error);
                console.log(`AdManager for vendor ${vendor} inited failed.`, options)
            }

        } else {
            console.error(`AdManager no ad plugin for vendor: ${vendor}`)
        }
        console.log(AdManager.adunits)
    }

    static get(vendor: string): AdManager | undefined {
        return AdManager.instances[vendor]
    }

    static getUnitInfoAndManager(ad_code: string): {unit:AdUnitInfo, manager: AdManager} | undefined {
        if(!(ad_code in AdManager.adunits)){
            return undefined
        }
        const adUnit = AdManager.adunits[ad_code]
        if(!(adUnit.ad_vendor in AdManager.instances)){
            return undefined
        }
        return {
            unit: adUnit,
            manager: AdManager.instances[adUnit.ad_vendor]
        }
    }

    static getUnitInfoAndManagerByVendor(vendor:string, ad_type:string): {unit:AdUnitInfo, manager: AdManager} | undefined {
        if(!(vendor in AdManager.instances)){
            return undefined
        }

        const manager = AdManager.instances[vendor]
        let ad_code:string | undefined = undefined
        for(const config of manager.primaryConfig.units){
            const unit_ad_type = config.ad_type ?? 'interstitial'
            if(ad_type === unit_ad_type){
                ad_code = config.codeId
                break
            }
        }
        if(ad_code === undefined){
            return undefined
        }

        return AdManager.getUnitInfoAndManager(ad_code)
    }

    constructor(config:AdAppConfigInterface, adPlugin:AdPlugin){
        this.primaryConfig = config
        this.primaryAd = adPlugin
        this.minPreparedAd = config.minPreparedAdCount ?? 1
    }


    async initialize():Promise<void> {
        await this.primaryAd?.initialize({ appId: this.primaryConfig.appId,
                appName: this.primaryConfig.appName })
    }




    async prepare():Promise<void>{
        if(this.primaryAd){
            for(const adUnit of this.primaryConfig.units){
                const ad_type = adUnit.ad_type ?? 'interstitial'
                const option = {
                    codeId: adUnit.codeId,
                    fullscreen: adUnit.fullscreen ?? false
                }
                if(ad_type == 'interstitial'){
                    await this.primaryAd?.prepareInterstitial(option);
                } else if(ad_type == 'reward') {
                    await this.primaryAd?.prepareReward(option);
                }

            }
        }

    }

    async hasAd(adunit: AdUnitInfo): Promise<boolean> {
        if(adunit.ad_type === 'interstitial'){
            const options = {
                codeId: adunit.ad_code,
                fullscreen: adunit.fullscreen
            }
            const ready = await this.primaryAd.isInterstitialReady(options)
            return ready.ready;
        } else if (adunit.ad_type === 'reward'){
            const options = {
                codeId: adunit.ad_code,
                fullscreen: adunit.fullscreen
            }
            const ready = await this.primaryAd.isRewardReady(options)
            return ready.ready;
        }
        return false;

    }

    async showAd(adunit: AdUnitInfo): Promise<boolean> {
        if(adunit.ad_type === 'interstitial'){
            const options = {
                codeId: adunit.ad_code,
                fullscreen: adunit.fullscreen
            }
            try {
                await this.primaryAd.showInterstitial(options)
                this.primaryAd.prepareInterstitial(options)
            } catch(err) {
                this.primaryAd.prepareInterstitial(options)
                throw(err);
            }

            return true;
        } else if (adunit.ad_type === 'reward'){
            const options = {
                codeId: adunit.ad_code,
                fullscreen: adunit.fullscreen
            }
            try {
                await this.primaryAd.showReward(options)
                this.primaryAd.prepareReward(options)
            } catch(err) {
                this.primaryAd.prepareReward(options)
                throw(err);
            }

            return true;
        }
        return false;
    }

    static async showAdNow(options:AdShowOptions, next_fn:Function): Promise<void> {
        console.log(AdManager.adunits, options)
        const ad_list = []
        const ad_code = options.ad_code
        if(ad_code !== undefined){
            const unit_and_manager = AdManager.getUnitInfoAndManager(ad_code)
            if(unit_and_manager !== undefined){
                ad_list.push(unit_and_manager)
            }

        } else {
            const vendor = options.ad_vendor
            const ad_type = options.ad_type
            if(ad_type !== undefined){
                const unit_and_manager = AdManager.getUnitInfoAndManagerByVendor(vendor, ad_type)
                if(unit_and_manager !== undefined){
                    ad_list.push(unit_and_manager)
                }
            }
        }

        const candidates = options.ad_candidates ?? []
        for(const it of candidates){
            const ad_code = it.ad_code;
            if(ad_code !== undefined){
                const unit_and_manager = AdManager.getUnitInfoAndManager(ad_code)
                if(unit_and_manager !== undefined){
                    ad_list.push(unit_and_manager)
                }
            }
        }

        for(const ad of ad_list){
            try{
                const admanager = ad?.manager
                const unit = ad?.unit

                console.log(`try show ad: ${ad.unit.ad_code}`)

                const has = await admanager.hasAd(unit)
                if(has){
                    const ad_showed = await admanager.showAd(unit)
                    if(!ad_showed){
                        continue
                    }
                    next_fn({ok: true})
                    return
                }
            } catch(err){
                console.error(`showAdNow error: ${err}`)
            }
        }
        next_fn({ok:false, message: "广告都被抢光了，请稍微尝试。多点击广告才能有更多广告！"})
    }

}


export class AdHelper {
    modal_helper: ModalHelper

    constructor(modal_helper:ModalHelper){
        this.modal_helper = modal_helper
    }

    async initAd(ad_config:Record<string, any>){
        await AdManager.initAd(ad_config)
    }

    showAdNow(options:AdShowOptions, nextfn: Function){
        const ad_hint = options.ad_hint
        if(ad_hint !== undefined && ad_hint.length > 0){
            const ad_confirm = options.ad_confirm ?? 'confirm'
            const ad_hint_text = ad_hint.join('\n')
            const modal_id = this.modal_helper.new_modal_id()
            this.modal_helper.open_any({
                text: ad_hint_text,
                "actionConfirmText": ad_confirm,
                "actionsPosition": "center",
                onModalConfirmed: () => {
                    AdManager.showAdNow(options, nextfn)
                }
            })
            return
        } else {
            AdManager.showAdNow(options, nextfn)
            return
        }
    }

}