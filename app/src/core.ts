import { reactive, UnwrapNestedRefs } from "vue"
import { ShowPageCommand, ServiceOperation, HolaCommand,
    ServiceConfig,
    UpdatePageCommand,
    ErrorResponse,
    StartNewSessionCommand,
    HolaCommonCommand,
    SetSessionCommand} from "./client";
import { PlayableResult } from './client'
import { DataStore, randomString } from "./db";
import { app_platform } from "./platform";
import i18next from 'i18next';

const APP_VERSION = '0.1.0'

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


export interface NavBarElement {
    type: string
    title?: string
    show_home: boolean
    show_profile: boolean
    show_back: boolean
    elements?: HolaElement[];
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
    name?: string;
    icon?: string;
    sub_text?: string;
    href?: string;
    handlers?: Record<string, string>
    open_new?: boolean;
    disable?: boolean;
    disable_text?: string;
    style?: Record<string, any>;
    open_modal?: Record<string, any>
    open_modal_args?: Record<string, any>;
    show_ad?:Record<string, any>
    action?: string;
    action_condition?: ActionableElement
    action_props?: Record<string, any>
    args?: Record<string, any>
    events?: Record<string, any>
}

export interface TitleElement {
    type: string;
    level: number
    title: string
    sub_title?: string
}

export interface LinkElement {
    type: string;
    text: string
    target_url: string
    open_mode?: string
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
    | PlainTextObject | AnnotationTextObject | DataTableElement;

export interface ModalElement {
    type: string;
    name?: string;
    title?: string;
    title_action?: Record<string, any>;
    content?: string;
    content_link?: string;
    style?: Record<string, any>;
    locals?: Record<string, any>;
    elements?: ModalWidgetElement[]
    confirm?: {
        text: string;
        action: string
        args: Record<string, any>
        click?: string
    };
    cancel?: {
        text: string;
        action: string
        args: Record<string, any>
        trigger?: boolean
        click?: string
    }
}

export interface CloseModalArgs {
    modal_id: string;
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
    title?: string
    text?: string
    image_src?: string
    element?: AnnotationTextObject
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

export interface MenuItemObject {
    label?: string;
    name?: string;
    icon?: string;
    handlers?: Record<string, string>;
}

export interface MenuElement {
    type: string
    label?: string
    icon?: string
    style?: Record<string, any>
    items: MenuItemObject[]
}

export interface HeaderElement {
    type: string
    start_elements?: HolaElement[];
    elements?: HolaElement[];
    end_elements?: HolaElement[];
}

export interface FooterElement {
    type: string
    text?: string
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
    rows: HolaElement[][];
    show?: {
        header?: boolean,
        inner_column?: boolean,
        inner_row?: boolean
    };
}

export interface SideBarElement {
    type: string,
    style?: Record<string, any>,
    elements?: HolaElement[]
}

export interface LogoElement{
    type: string
    text?: string
    image_src?: string
}

export interface CardElement{
    type: string
    title?: string
    text?: string
    image_src?: string
    show_border: boolean
    elements: HolaElement[]
    style?: Record<string, any>
}

export interface DataTableElement {
    type: string
    data: object[]
    columns: any[]
    style?: Record<string, any>
    paginator?: Record<string, any>
}

export interface ToolbarElement {
    type: string
    start_elements: HolaElement[]
    elements: HolaElement[]
    end_elements: HolaElement[]
    style?: Record<string, any>
}

export interface InputElement{
    type: string
    label?: string
    name?: string
    value?: string
    password?: boolean
    validate?: Record<string, any>
}

export interface DropdownElement {
    type: string
    value: string
    label?: string
    name?: string
    validate?: Record<string, any>
    options: Record<string, any>[]
}

export interface TagElement{
    type: string
    text?: string
    color: string
}

export interface AvatarElement{
    type: string
    icon?: string
    image_src?: string
    badge?: Record<string, any>
    style?: Record<string, any>
}

export interface CheckboxElement{
    type: string
    value: boolean | undefined
    binary?: boolean
    text?: string
    check_strike?: boolean;
    style?: Record<string, any>
}

export interface ProgressbarElement{
    type: string
    percent?: number;
    value?: number;
    total?: number;
    style?: Record<string, any>
}

export interface CalendarElement{
    type: string
    value?: string;
    value_format?: string;
    min_value?: string;
    max_value?: string;
    range?: boolean
    locale?: string;
    icon?: boolean
    show_date?: boolean
    show_time?: boolean
    style?: Record<string, any>
}


export interface InputSwitchElement{
    type: string
    value: boolean
    text?: string
    style?: Record<string, any>
}


export interface MultiSelectElement{
    type: string
    style?: Record<string, any>
    label?: string
    values?: Array<string>
    options?: Array<Record<string, any>>
    chips?: boolean
}


export interface TextareaElement{
    type: string
    style?: Record<string, any>
    value?: string
    label?: string
    rows?: number
    cols?: number
}

export interface CardSwiperElement {
    type: string
    title: string
    elements: HolaElement[]
}

export type HolaElement = (HeaderElement | FooterElement | NavBarElement
    | HeroElement | NavMenuElement | DecorationElement
    | MotionElement | PlayableElement | ActionBarElement
    | TableViewElement | ModalWidgetElement);


export interface HolaPage {
    type: string
    name: string
    route: string
    locals?: Record<string, any>
    elements: HolaElement[]
}


export interface UpdatePageObject {
    name: string
    route: string
    changed_elements: Record<string, HolaElement>
}


export class Page {
    static instances: Record<string, UnwrapNestedRefs<Page>> = {}
    app_id: string
    name: string
    route: string
    elements: Array<HolaElement>
    locals: Record<string, any>
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
        this.locals = {}
        this.version = 0
    }

    reset() {
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
    assetsUrl: string,
    clientKey: string,
    clientSecret: string
}

export class AppCore {
    static instances: Record<string, AppCore> = {}
    static app_configs: Record<string, AppConfig> = {}
    app_id: string
    svc: ServiceOperation
    config: AppConfig
    platform: Record<string, any>
    privacy_agreed: boolean = false
    app_page: UnwrapNestedRefs<Page>
    session_started: boolean = false
    error_recovering: boolean = false
    errors: any[] = []
    max_recover_retries: number = 6
    version: string = APP_VERSION

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
        this.platform = app_platform.getPlatform()
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
        const platform = p.name
        delete p.name
        return {
            platform: platform,
            route: this.app_page.route,
            version: this.version,
            ...p
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

    async loginWeixin(): Promise<HolaCommand[]>{
        try {
            const wechat = app_platform.getWeChatPluginInstance()
            if(!wechat){
                throw Error("WeChatPlugin not initialized.")
            }
            const state = "HIGHORDER" + randomString(12)
            const ret = await wechat!.sendAuthRequest({scope:"snsapi_userinfo", state: state})
            const commands = await this.svc.holaAuthWeixin({code:ret.code}, this.getPageContext())
            await this.setPlatformUser()
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }
    }

    async sessionStart(): Promise<HolaCommand[]> {
        try{
            const commands = await this.svc.holaSessionStart(this.getPageContext())
            this.session_started = true
            await this.setPlatformUser()
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }
    }

    async callAction(args: Record<string, any>): Promise<HolaCommand[]> {
        try {
            const commands = await this.svc.holaCallAction(args, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async pageInteract(name: string, event:string, handler:string, locals:object): Promise<HolaCommand[]> {
        try {
            const commands = await this.svc.holaPageInteract(name, event, handler, locals, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async dialogInteract(dialog_id: string, name: string, event:string, handler:string, locals:object): Promise<HolaCommand[]> {
        try {
            const commands = await this.svc.holaDialogInteract(dialog_id, name, event, handler, locals, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async navigateTo(route: string): Promise<HolaCommand[]> {
        try {
            const commands = await this.svc.holaNavigateTo(route, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async playableCompleted(played: PlayableResult): Promise<HolaCommand[]> {
        console.log('playable completed.', played)
        try {
            const commands = await this.svc.holaPlayableCompleted(played, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async playableNext(level_id: string): Promise<HolaCommand[]> {
        try {
            const commands = await this.svc.holaPlayableNext(level_id, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async playableRetry(level_id: string): Promise<HolaCommand[]> {
        try {
            const commands = await this.svc.holaPlayableRetry(level_id, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async itemUse(item_name: string): Promise<HolaCommand[]> {
        try {
            const commands = await this.svc.holaItemUse(item_name, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async itemBuy(item_name: string): Promise<HolaCommand[]> {
        try {
            const commands = await this.svc.holaItemBuy(item_name, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async adShowed(ad_args: Record<string, any>): Promise<HolaCommand[]> {
        try {
            const commands = await this.svc.holaAdShowed(ad_args, this.getPageContext())
            return await this.handleCommandList(commands)
        } catch(err: any) {
            return await this.handleError(err)
        }

    }

    async handleUnknownError(err: any): Promise<HolaCommand[]> {
        return []
    }

    buildShowModalCommand(modal: ModalElement){
        return {
            "type": "command",
            "name": "show_modal",
            "args": modal
        } as HolaCommonCommand
    }

    async handleErrorResponse(err: ErrorResponse): Promise<HolaCommand[]> {
        const commands:HolaCommand[] = []
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
            const command: HolaCommonCommand = this.buildShowModalCommand({
                "type":"modal",
                title: 'SERVER NO RESPONSE',
                content: i18next.t('check_network'),
                confirm:{
                    text: i18next.t('network_ok'),
                    action: "",
                    args: {}
                }
            })
            if(this.app_page.isEmpty()){
                const confirm = (command.args as ModalElement).confirm
                if(confirm){
                    confirm.action = "route.navigate_to"
                    confirm.args = {route: "/"}
                }
            }
            commands.push(command)
        } else if(error_type === 'InternalServerError' || code_category === 5) {
            const command: HolaCommonCommand = this.buildShowModalCommand({
                "type":"modal",
                title: 'SERVER ERROR',
                content: i18next.t('server_upgrading'),
                confirm:{
                    text: i18next.t('retry_text'),
                    action: "",
                    args: {}
                }
            })
            if(this.app_page.isEmpty()){
                const confirm = (command.args as ModalElement).confirm
                if(confirm){
                    confirm.action = "route.navigate_to"
                    confirm.args = {route: "/"}
                }
            }
            commands.push(command)
        } else if(error_type === 'RequestInvalidError' || code_category === 4){
            const command: HolaCommonCommand = this.buildShowModalCommand({
                "type":"modal",
                title: 'REQUEST INVALID',
                content: i18next.t('check_client_version'),
                confirm:{
                    text: i18next.t('client_version_ok'),
                    action: "",
                    args: {}
                }
            })
            if(this.app_page.isEmpty()){
                const confirm = (command.args as ModalElement).confirm
                if(confirm){
                    confirm.action = "route.navigate_to"
                    confirm.args = {route: "/"}
                }
            }
            commands.push(command)
        } else {
            const command: HolaCommonCommand = this.buildShowModalCommand({
                "type":"modal",
                title: 'RECOVERING',
                content: i18next.t('problem_recovering'),
                confirm:{
                    text: i18next.t('fine_ok'),
                    action: "",
                    args: {}
                }
            })
            if(this.app_page.isEmpty()){
                const confirm = (command.args as ModalElement).confirm
                if(confirm){
                    confirm.action = "route.navigate_to"
                    confirm.args = {route: "/"}
                }
            }
            commands.push(command)
        }
        return commands
    }

    async handleError(err: any): Promise<HolaCommand[]> {
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

    async handleCommandList(commands: HolaCommand[]): Promise<HolaCommand[]> {
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

    async handleCommand(command: HolaCommand): Promise<HolaCommand | undefined> {
        console.debug('handleCommand', command.name)
        if (command.name === 'show_page') {
            let showpage_cmd = command as ShowPageCommand
            const page = showpage_cmd.args.page as HolaPage
            this.app_page.reset()
            this.app_page.name = page.name
            this.app_page.route = page.route
            this.app_page.locals = page.locals ?? {}
            this.app_page.elements = page.elements
            this.app_page.version = this.app_page.version + 1
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
        } else if (command.name === 'set_session') {
            let _cmd = command as SetSessionCommand
            await this.svc.setSession(_cmd.args.user, _cmd.args.session)
            await this.navigateTo(this.app_page.route)
        } else if (command.name === 'clear_session') {
            await this.svc.clearSession()
            await this.navigateTo(this.app_page.route)
        } else {
            return command
        }
    }
}
