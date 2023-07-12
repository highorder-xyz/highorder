import { reactive, UnwrapNestedRefs } from "vue"
import { ShowPageCommand, ServiceOperation, QuestCommand,
    ShowNarrationCommand,
    ServiceConfig,
    UpdatePageCommand,
    ErrorResponse,
    StartNewSessionCommand,
    QuestCommonCommand,
    SetSessionCommand} from "./client";
import { PlayableResult } from './client'
import { DataStore, randomString } from "./db";
import { app_platform } from "./platform";

const CORE_VERSION = '0.1.0'

export enum  AnalyticsEventKind {
    page_show = 'PageShow',
    ad_show_event = 'AdShowEvent',
    playable_event = 'PlayableEvent',
    played_event = 'PlayedEvent',
    item_event = 'ItemEvent',
    button_event = 'ButtonEvent'
}

export interface PageShowParam{
    route: string
}

export interface PlayableParam{
    name: string
    route: string
    level_id: string
    effect?: string
}

export interface AdShowParam {
    name: string
    route: string,
    vendor: string,
    ad_type: string
}


export interface ItemParam {
    name: string
    route: string,
    item_name: string,
    item_count: number
}

export interface ButtonParam {
    route: string,
    text: string
}


export interface HeaderElement {
    type: string
    title?: string
    show_home: boolean
    show_profile: boolean
    show_back: boolean
    elements?: QuestElement[];
}

export interface AnnotationTextObject {
    type: string;
    text: string;
    annotation: string;
}

export interface PlainTextObject {
    type: string;
    text: string;
}

export interface SeparatorElement {
    type: string;
}

export interface ParagraphElement {
    type: string;
    text: string;
    align?: string
}

export interface BulletedListElement {
    type: string;
    texts: string[]
}

export interface ActionableElement{
    action: string;
    args: Record<string, any>
}

export interface ButtonElement {
    type: string;
    text: string;
    icon?: string;
    sub_text?: string;
    disable?: boolean;
    disable_text?: string;
    style?: Record<string, any>;
    open_modal?: Record<string, any>
    open_modal_args?: Record<string, any>;
    show_ad?:Record<string, any>
    action: string;
    action_condition?: ActionableElement
    action_props?: Record<string, any>
    args: Record<string, any>

}

export interface TitleElement {
    type: string;
    level: number
    text: string
}

export interface ProgressBarElement {
    type: string;
    percent?: number;
    value?: number;
    total?: number;
    style?: Record<string, any>
}

export interface StarRatingElement {
    type: string;
    rating: number;
    animate: boolean;
}

export interface IconElement {
    icon: string;
    style: Record<string, any>
}

export interface IconTextElement {
    type: string;
    text: string;
    icon: string;
    style: Record<string, any>
}

export interface IconNumberElement {
    type: string;
    number: number;
    icon: string;
    animate: boolean
}

export interface IconTitleElement {
    type: string;
    icon: string;
    count: number;
}

export interface ImageElement {
    type: string;
    image_url: string;
    image_type?: string;
    style?: Record<string, any>
}

export interface VideoElement {
    type: string;
    video_url: string;
    poster_url?: string;
    aspect?: string,
    video_type?: string;
    autoplay?: boolean;
    style?: Record<string, any>
}

export interface ItemWidgetElement {
    type: string;
    name: string;
    show?: {
        icon?: boolean;
        display_name?: boolean;
        description?: boolean;
    }
    count?: {
        template?: string;
        template_have?: string;
        template_not?: string;
    }
}

export interface RowLineElement {
    type: string;
    elements: ModalWidgetElement[];
    style?: Record<string, any>
}
export interface ColumnElement {
    type: string;
    elements: ModalWidgetElement[];
    style?: Record<string, any>
}

export type ModalWidgetElement = ItemWidgetElement | TitleElement
    | SeparatorElement | ParagraphElement | BulletedListElement
    | RowLineElement | ColumnElement | ButtonElement | StarRatingElement
    | PlainTextObject | AnnotationTextObject ;

export interface ModalElement {
    type: string;
    title?: string;
    title_action?: Record<string, any>;
    content?: string;
    content_link?: string;
    style?: Record<string, any>;
    elements?: ModalWidgetElement[]
    confirm?: {
        text: string;
        action: string
        args: Record<string, any>
    };
    cancel?: {
        text: string;
        action: string
        args: Record<string, any>
    }
}

export interface MenuItemElement {
    type: string;
    text: string;
    sub_text: string;
    disable?: boolean;
    disable_text?: string;
    icon?: string;
    route: string;
    open_url?: string;
    open_modal?: ModalElement;
    open_modal_args?: Record<string, any>;
}

export interface ActionButtonElement {
    type: string;
    icon?: string;
    route?: string;
    text?: string;
    count?: number
    disable?: boolean;
    disable_text?: string;
    open_modal?: ModalElement
    open_modal_args?: Record<string, any>;
    action: string;
    action_condition?: ActionableElement
    action_props?: Record<string, any>
    args: Record<string, any>
}


export type ActionElement = ActionButtonElement;

export interface HeroElement {
    type: string
    element: AnnotationTextObject
}

export interface DecorationElement {
    type: string
    name: string
    properties: object
}

export interface MotionElement {
    type: string
    name: string
    properties: object
}

export interface PlayableElement {
    type: string
    name: string
    collection?: string
    level_id: string
    config: object
}

export interface NavMenuElement {
    type: string
    style: Record<string, any>
    elements: MenuItemElement[]
}

export interface FooterElement {
    type: string
    left_elements?: ActionElement[];
    element: PlainTextObject;
    right_elements?: ActionElement[];
}

export interface ActionBarElement {
    type: string
    left_elements?: ActionElement[];
    elements: ActionElement[];
    right_elements?: ActionElement[];
}


export interface TableViewElement {
    type: string
    columns: string[];
    rows: QuestElement[][];
    show?: {
        header?: boolean,
        inner_column?: boolean,
        inner_row?: boolean
    };
}

export interface CardElement{
    type: string
    title: string
    show_border: boolean
    elements: QuestElement[]
}

export interface CardSwiperElement {
    type: string
    title: string
    elements: QuestElement[]
}

export type QuestElement = (HeaderElement | FooterElement
    | HeroElement | NavMenuElement | DecorationElement
    | MotionElement | PlayableElement | ActionBarElement
    | TableViewElement | ModalWidgetElement);

export interface QuestPage {
    type: string
    name: string
    route: string
    elements: QuestElement[]
}


export interface UpdatePageObject {
    name: string
    route: string
    changed_elements: Record<string, QuestElement>
}


export interface NarrationParagraph {
    text: string | string[]
}

export interface QuestNarration {
    type: string
    name: string
    style?: Record<string, any>
    paragraphs: NarrationParagraph[]
}


export class Page {
    static instances: Record<string, UnwrapNestedRefs<Page>> = {}
    app_id: string
    name: string
    route: string
    elements: Array<QuestElement>
    narration: QuestNarration
    narration_idx: number
    version: number

    static getPage(app_id: string){
        if(this.instances.hasOwnProperty(app_id)){
            return this.instances[app_id]
        } else {
            const page = reactive(new Page(app_id))
            this.instances[app_id] = page
            return page
        }
    }

    constructor(app_id: string) {
        this.app_id = app_id
        this.name = "app"
        this.route = '/'
        this.elements = []
        this.narration = {
            type: "narration",
            name: "default",
            paragraphs: []
        }
        this.narration_idx = 0
        this.version = 0
    }

    emptyNarration() {
        this.narration = {
            type: "narration",
            name: "default",
            paragraphs: []
        }
        this.narration_idx = 0
    }

    reset() {
        this.emptyNarration()
        this.version += 1
    }

    isEmpty() {
        return this.elements.length === 0
    }
}

export let appGlobal = reactive({"app_id": ""})

export interface Item {
    name: string,
    count: number,
    icon?: string,
    display_name: string,
    description?: string,
    hint?: string,
    price?: number,
    limit?: number,
}

export interface LevelState {
    name: string,
    successed: boolean
}

export interface ItemState {
    name: string,
    count: number
}

export interface ItemReward {
    name: string,
    count: number,
    buff_name?: string,
    buff_count?: number
}

export interface AppConfig {
    appId: string,
    baseUrl: string,
    privacyUrl: string,
    clientKey: string,
    clientSecret: string
}

export class AppCore {
    static instances: Record<string, AppCore> = {}
    static app_configs: Record<string, AppConfig> = {}
    app_id: string
    svc: ServiceOperation
    config: AppConfig
    privacy_agreed: boolean = false
    app_page: UnwrapNestedRefs<Page>
    session_started: boolean = false
    error_recovering: boolean = false
    errors: any[] = []
    max_recover_retries: number = 6
    version: string = CORE_VERSION

    constructor(config:AppConfig) {
        this.config = config
        let baseUrl = config.baseUrl.trim()
        if(baseUrl.endsWith('/')){
            baseUrl = baseUrl.slice(0, -1)
        }
        this.config.baseUrl = baseUrl
        this.app_id = config.appId
        this.svc = new ServiceOperation(this.config as ServiceConfig)
        this.app_page = Page.getPage(this.app_id)
    }

    static async switchTo(app_id:string){
        if(!this.instances.hasOwnProperty(app_id)){
            const config = this.app_configs[app_id]
            const core = new AppCore(config)
            await core.load()
            this.instances[app_id] = core
        }
        appGlobal.app_id = app_id
    }

    static addAppConfig(config: AppConfig){
        this.app_configs[config.appId] = config
    }

    static async init(): Promise<void> {
        await DataStore.init()
    }

    static getCore(app_id: string) : AppCore {
        return this.instances[app_id]
    }

    getPageContext() {
        const p = app_platform.getPlatform()
        return {
            platform: p.name,
            vendor: p.vendor ?? "unknown",
            route: this.app_page.route,
            version: this.version
        }
    }


    async setPlatformUser(): Promise<void> {
        if(this.svc.user){
            await app_platform.setUser(this.svc.user.user_id, {})
        }
    }

    async load(): Promise<void> {
        await this.svc.init()
        this.privacy_agreed = await this.getPrivacyAgreed()
        await this.setPlatformUser()
    }

    async getContent(url: string): Promise<string> {
        return await this.svc.getContent(url);
    }

    full_link(url: string | undefined): string {
        if(!url){
            return ""
        }
        if(!url.includes('/')){
            return url;
        }
        if(url.includes("://")){
            return url;
        }
        return `${this.config.baseUrl}${url}`
    }

    async getPrivacyAgreed(){
        let value = await DataStore.get("privacy_agreed")
        if(value === 1){
            return true
        }
        value = await DataStore.get_app_kv([this.app_id, "privacy_agreed"])
        if(value === 1){
            return true
        }
        return false
    }

    async savePrivacyAgreed(){
        this.privacy_agreed = true
        await DataStore.save({key:"privacy_agreed", value:1})
        await DataStore.save_app_kv({app_id: this.app_id, key:"privacy_agreed", value:1})
        await app_platform.initialize(app_platform.init_options)
    }

    async loginWeixin(): Promise<QuestCommand[]>{
        try {
            const wechat = app_platform.getWeChatPluginInstance()
            if(!wechat){
                throw Error("WeChatPlugin not initialized.")
            }
            const state = "HIGHORDER" + randomString(12)
            const ret = await wechat!.sendAuthRequest({scope:"snsapi_userinfo", state: state})
            const commands = await this.svc.questAuthWeixin({code:ret.code}, this.getPageContext())
            await this.setPlatformUser()
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }
    }

    async sessionStart(): Promise<QuestCommand[]> {
        try{
            const commands = await this.svc.questSessionStart(this.getPageContext())
            this.session_started = true
            await this.setPlatformUser()
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }
    }

    async callAction(args: Record<string, any>): Promise<QuestCommand[]> {
        try {
            const commands = await this.svc.questCallAction(args, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async navigateTo(route: string): Promise<QuestCommand[]> {
        try {
            const commands = await this.svc.questNavigateTo(route, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async narrationShowed(name: string): Promise<QuestCommand[]> {
        try {
            const commands = await this.svc.questNarrationShowed(name, this.getPageContext())
            const ret_commands = await this.handleCommandList(commands)
            this.app_page.emptyNarration()
            return ret_commands
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async playableCompleted(played: PlayableResult): Promise<QuestCommand[]> {
        console.log('playable completed.', played)
        try {
            const commands = await this.svc.questPlayableCompleted(played, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async playableNext(level_id: string): Promise<QuestCommand[]> {
        try {
            const commands = await this.svc.questPlayableNext(level_id, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async playableRetry(level_id: string): Promise<QuestCommand[]> {
        try {
            const commands = await this.svc.questPlayableRetry(level_id, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async itemUse(item_name: string): Promise<QuestCommand[]> {
        try {
            const commands = await this.svc.questItemUse(item_name, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async itemBuy(item_name: string): Promise<QuestCommand[]> {
        try {
            const commands = await this.svc.questItemBuy(item_name, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async adShowed(ad_args: Record<string, any>): Promise<QuestCommand[]> {
        try {
            const commands = await this.svc.questAdShowed(ad_args, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async handleUnknownError(err: any): Promise<QuestCommand[]> {
        return []
    }

    buildShowModalCommand(modal: ModalElement){
        return {
            "type": "command",
            "name": "show_modal",
            "args": modal
        } as QuestCommonCommand
    }

    async handleErrorResponse(err: ErrorResponse): Promise<QuestCommand[]> {
        const commands:QuestCommand[] = []
        const error_type = err.error.error_type
        const code_category = Math.floor(err.code/100)
        if(error_type === 'SessionInvalid' || error_type === 'AuthorizeRequired'){
            await this.svc.deleteSession()
            const command: StartNewSessionCommand = {
                "type": "command",
                "name": "start_new_session",
                "args": {}
            }
            commands.push(command)
        } else if(error_type === 'ServerNoResponse') {
            const command: QuestCommonCommand = this.buildShowModalCommand({
                "type":"modal",
                content:"无法进行网络连接，请检查网络状况，或者给App连接网络的权限。",
                confirm:{
                    text: "好的，网络好了",
                    action: "",
                    args: {}
                }
            })
            if(this.app_page.isEmpty()){
                const confirm = (command.args as ModalElement).confirm
                if(confirm){
                    confirm.action = "route.navigate_to"
                    confirm.args = {route: "/home"}
                }
            }
            commands.push(command)
        } else if(error_type === 'InternalServerError' || code_category === 5) {
            const command: QuestCommonCommand = this.buildShowModalCommand({
                "type":"modal",
                content:"服务器可能正在升级，请6秒后重试。",
                confirm:{
                    text: "好的，重试",
                    action: "",
                    args: {}
                }
            })
            if(this.app_page.isEmpty()){
                const confirm = (command.args as ModalElement).confirm
                if(confirm){
                    confirm.action = "route.navigate_to"
                    confirm.args = {route: "/home"}
                }
            }
            commands.push(command)
        } else if(error_type === 'RequestInvalidError' || code_category === 4){
            const command: QuestCommonCommand = this.buildShowModalCommand({
                "type":"modal",
                content:"请检查App版本，确保已经是最新的版本了。",
                confirm:{
                    text: "好的，是最新版本",
                    action: "",
                    args: {}
                }
            })
            if(this.app_page.isEmpty()){
                const confirm = (command.args as ModalElement).confirm
                if(confirm){
                    confirm.action = "route.navigate_to"
                    confirm.args = {route: "/home"}
                }
            }
            commands.push(command)
        } else {
            const command: QuestCommonCommand = this.buildShowModalCommand({
                "type":"modal",
                content:"发现了问题，努力自救中。。。",
                confirm:{
                    text: "好的，加油",
                    action: "",
                    args: {}
                }
            })
            if(this.app_page.isEmpty()){
                const confirm = (command.args as ModalElement).confirm
                if(confirm){
                    confirm.action = "route.navigate_to"
                    confirm.args = {route: "/home"}
                }
            }
            commands.push(command)
        }
        return commands
    }

    async handleError(err: any): Promise<QuestCommand[]> {
        if(this.error_recovering === false){
            this.error_recovering = true
            this.errors = []
        }
        if(this.errors.length > this.max_recover_retries){
            return []
        }
        this.errors.push(err)
        if(err instanceof ErrorResponse){
            return await this.handleErrorResponse(err as ErrorResponse)
        } else {
            // return await this.handleUnknownError(err)
            throw(err);
        }
    }

    reset_recover_state(){
        this.error_recovering = false
        this.errors = []
    }

    async handleCommandList(commands: QuestCommand[]): Promise<QuestCommand[]> {
        this.reset_recover_state()
        const ret_commands = []
        for (const command of commands) {
            const cmd = await this.handleCommand(command)
            if (cmd) {
                ret_commands.push(cmd)
            }
        }
        return ret_commands
    }

    async handleCommand(command: QuestCommand): Promise<QuestCommand | undefined> {
        console.debug('handleCommand', command.name)
        if (command.name === 'show_page') {
            let showpage_cmd = command as ShowPageCommand
            const page = showpage_cmd.args.page as QuestPage
            this.app_page.reset()
            this.app_page.name = page.name
            this.app_page.route = page.route
            this.app_page.elements = page.elements
            app_platform.logEvent(AnalyticsEventKind.page_show, {route: page.route})
        } else if (command.name === 'update_page') {
            let updatepage_cmd = command as UpdatePageCommand
            const changed_page = updatepage_cmd.args.changed_page as UpdatePageObject
            if (this.app_page.route === changed_page.route){
                for(const [idx, element] of Object.entries(changed_page.changed_elements)){
                    const k = parseInt(idx)
                    if( isNaN(k)){
                        console.warn(`update page with wrong idx ${idx}`, element)
                    }else {
                        if(k >= this.app_page.elements.length){
                            console.warn(`update page with wrong idx ${k} bigger than elements length`, element)
                            continue
                        }
                        this.app_page.elements[k] = element
                    }
                }
            } else {
                console.log(`update page with wrong route ${changed_page.route}, app_page route is ${this.app_page.route}`)
            }
        } else if (command.name === 'show_narration') {
            const narration = (command as ShowNarrationCommand).args.narration as QuestNarration
            this.app_page.narration = narration
        } else if (command.name === 'set_player') {
        } else if (command.name === 'update_player') {
        } else if (command.name === 'set_session') {
            let _cmd = command as SetSessionCommand
            await this.svc.setSession(_cmd.args.user, _cmd.args.session)
            await this.navigateTo(this.app_page.route)
        } else {
            return command
        }
    }
}