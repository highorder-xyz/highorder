import { defineComponent, h, reactive, VNode, resolveComponent, DefineComponent} from 'vue'
import i18next from 'i18next';
import {
    PlainTextObject,
    HeaderElement,
    FooterElement, HeroElement, NavMenuElement, MenuItemElement,
    DecorationElement, MotionElement, PlayableElement,
    ActionBarElement,
    ActionElement,
    ModalWidgetElement,
    SeparatorElement,
    TitleElement,
    ParagraphElement,
    BulletedListElement,
    Item,
    ButtonElement,
    ModalElement,
    StarRatingElement,
    IconTextElement,
    AnnotationTextObject,
    RowLineElement,
    IconTitleElement,
    TableViewElement,
    HolaElement,
    CardElement,
    CardSwiperElement,
    ColumnElement,
    IconNumberElement,
    AnalyticsEventKind,
    appGlobal,
    Page,
    AppCore,
    VideoElement,
    ImageElement,
    IconElement,
    ProgressBarElement,
    NavBarElement,
    LinkElement,
    LogoElement,
    InputElement,
    SideBarElement,
    MenuElement,
    MenuItemObject,
    DataTableElement,
    ToolbarElement,
    DropdownElement,
    CloseModalArgs,
    TagElement,
    AvatarElement,
    CheckboxElement,
    ProgressbarElement,
    CalendarElement,
    InputSwitchElement,
    MultiSelectElement,
    TextareaElement,
    QrcodeElement
} from './core'
import { InitAdCommand, InitAdCommandArg, PlayableApplyCommand, PlayableApplyCommandArg, PlayableResult, ShowAdCommand, ShowAdCommandArg } from './client'
import {
    NavBar, Footer, Button, ActionDefinition,
    Modal, ActionBar, IconActionDefinition,
    NavMenu, Hero, MenuItem, Divider, Title, Paragraph, BulletedList, Alert, AlertType,
    IconText, StarRating, AnnotationText, IconTitle, TableView, CardSwiper, Card, Column, Row, IconCountText,
    Loader,
    VideoPlayer,
    ImageView,
    Icon,
    IconButton,
    ProgressBar,
    Header,
    Link,
    Logo,
    InputText,
    SideBar,
    Menu,
    DataTable,
    Toolbar,
    Dropdown,
    Dialog,
    Toast,
    Tag,
    Avatar,
    Checkbox,
    Progressbar,
    Calendar,
    InputSwitch,
    MultiSelect,
    Textarea,
    Qrcode
} from './components'

import { app_platform } from './platform';
import { HolaCommand, ShowAlertCommandArg, ShowMotionCommandArg } from './client';

import { AdHelper, AdShowOptions } from './ad';
import { randomString } from './db';
import { ApplyableInstance, ConditionResponse } from './playable/defines'
import { showConfetti } from './motion/confetti';
import { ComponentInterface } from 'ionicons/dist/types/stencil-public-runtime';

type PlayableComponent = ApplyableInstance;

const themes_all = {
    'fluent-light': {},
    'retro-light': {},
    'tailwind-light': {},
    'md-dark-indigo': {},
    'md-light-indigo': {},
    'md-dark-deeppurple': {},
    'md-light-deeppurple': {},
    'lara-dark-teal': {},
    'lara-light-teal': {},
    'lara-dark-indigo': {},
    'lara-light-indigo': {},
    'lara-dark-purple': {},
    'lara-light-purple': {},
    'lara-dark-blue': {},
    'lara-light-blue': {}
}

function replaceAll(string:string, search:string, replace:string) {
    return string.split(search).join(replace);
}

function toPascalCase(name:string) {
    let thePascalCase = `-${name}`.replace(/-./g, match => match[1].toUpperCase())
    return thePascalCase;
}

export function renderPlayableComponent(name: string, props: any, children:any): VNode {
    const _name = name.toLowerCase().replace(/_/g, '-')
    const component_name = toPascalCase(_name)
    const component = resolveComponent(component_name)
    console.log('renderPlayableComponent', component_name, props)
    if(component){
        return h(component, props, children)
    }
    return h('div', {...props}, 'not exits playable')
}

export function renderMotionComponent(name: string, props: any, children:any): VNode {
    const _name = name.toLowerCase().replace(/_/g, '-')
    const component_name = toPascalCase(_name) + 'Motion'
    const component = resolveComponent(component_name)

    console.log('renderMotionComponent', component_name, component, props)
    if(component){
        return h(component, props, children)
    }
    return h('div', {...props}, 'not exits motion')
}

export function showMotion(name: string, args: object): void {
    const _name = name.toLowerCase().replace(/_/g, '-')

    if(_name === 'confetti'){
        showConfetti(args)
    }
}

export function renderDecorationComponent(name: string, props: any, children:any): VNode {
    const _name = name.toLowerCase().replace(/_/g, '-')
    const component_name = toPascalCase(_name) + 'Motion'
    const component = resolveComponent(component_name)

    console.log('renderDecorationComponent', component_name, component)
    if(component){
        return h(component, props, children)
    }
    return h('div', {...props}, 'not exits decoration')
}

export function switchTheme(app_id:string, newTheme:string, linkElementId:string, callback:Function) {
    const linkElement = document.getElementById(linkElementId);
    if (linkElement === null){
        console.log(`theme node ID ${linkElementId} not exits, switchTheme failed.`)
        return
    }
    const cloneLinkElement = linkElement!.cloneNode(true) as HTMLElement;
    const app_core = AppCore.getCore(app_id)
    const assetsUrl = app_core.config.assetsUrl
    const newThemeUrl = `${assetsUrl}/themes/${newTheme}/theme.css`;

    cloneLinkElement.setAttribute('id', linkElementId + '-clone');
    cloneLinkElement.setAttribute('href', newThemeUrl);
    cloneLinkElement.addEventListener('load', () => {
        linkElement.remove();
        cloneLinkElement.setAttribute('id', linkElementId);

        if (callback) {
            callback();
        }
    });
    linkElement.parentNode && linkElement.parentNode.insertBefore(cloneLinkElement, linkElement.nextSibling);
}

export function changeTheme(app_id:string, newTheme:string, callback:Function) {
    return switchTheme(app_id, newTheme, 'theme-link', callback)
}

export interface AlertOption{
    top?:number,
    bottom?: number,
    width?: number,
    duration?: number,
    closeIn?: number
}

export interface ComponentRefs{
    $refs: Record<string, unknown>
}

export class AlertHelper {
    option:AlertOption
    ref: string
    container: ComponentRefs

    constructor(container:ComponentRefs, option:AlertOption | undefined = undefined) {
        this.container = container
        this.option = option ?? {
            top: -120,
            bottom: 40,
            width: 360,
            duration: 300,
            closeIn: 3000
        }
        const num = Math.floor(Math.random() * (9999 - 1000) + 1000)
        this.ref = 'alert_root_' + num.toString()
    }

    show(alertMessage: string,
        alertHeader?: string,){
        const alert = this.container.$refs[this.ref] as AlertType
        alert.showAlert(alertMessage, alertHeader)
    }

    render() {
        return h(Alert, {ref:this.ref, ...this.option})
    }
}


export type ModalOption = Record<string, any>

export class ModalUpdater {
    helper: ModalHelper
    modal_id: string


    constructor(helper:ModalHelper, modal_id:string)
    {
        this.helper = helper
        this.modal_id = modal_id
    }

    update(option:ModalOption){
        this.helper.update(this.modal_id, option)
    }
}

export interface ModalParameter {
    modal_id: string;
    option: ModalOption;
    close_listeners: Array<(param:ModalParameter) => void>;
    slot_render?: Function;
}

export class ModalHelper {
    root_modal: ModalParameter | undefined
    current: ModalParameter | undefined
    modal_stack: Array<ModalParameter>
    app?: ComponentInterface

    constructor() {
        this.root_modal = undefined
        this.modal_stack = []
        this.current = undefined
        this.app = undefined
    }

    setApp(app:ComponentInterface){
        this.app = app
    }

    new_modal_id(){
        return randomString(10)
    }

    open_any(option: ModalOption, slot_render: Function | undefined = undefined){
        const modal_id = this.new_modal_id()
        if(this.current){
            const param: ModalParameter = {modal_id: modal_id, option: option, slot_render:slot_render, close_listeners:[]}
            return this.open_sub(param, { route: '/unknown', modal_id: this.current?.modal_id})
        } else {
            return this.open(modal_id, option, slot_render)
        }

    }

    open(modal_id:string, option: ModalOption, slot_render: Function | undefined = undefined){
        if(this.current){
            return new ModalUpdater(this, this.current.modal_id)
        }
        const param: ModalParameter = {modal_id: modal_id, option: option, slot_render:slot_render, close_listeners:[]}
        param.option['onModalClosed'] = () => {
            this.close()
        }
        this.current = param
        this.root_modal = param
        return new ModalUpdater(this, param.modal_id)
    }

    async open_wait(modal_id:string, option: ModalOption, context:RenderContext, slot_render: Function | undefined = undefined){
        if(this.current && this.current.modal_id !== context.modal_id){
            console.log('open wait modal error. current modal exists.')
            return
        }
        const param: ModalParameter = {modal_id: modal_id, option: option, slot_render:slot_render, close_listeners:[]}
        return new Promise<void>((resolve) => {
            param.close_listeners.push((param:ModalParameter) => {
                resolve()
            })
            if(this.current){
                this.open_sub(param, context, false)
            } else {
                param.option['onModalClosed'] = () => {
                    this.close()
                }
                this.current = param
                this.root_modal = param
            }

        })
    }

    open_sub(param: ModalParameter, context: RenderContext, inplace:boolean = false){
        if(!this.current){
            console.log('error open_sub modal,  must be called in modal')
            return
        }
        if(this.current && this.current.modal_id !== context.modal_id){
            console.log('error open_sub modal, current modal_id not match parent_model_id')
            return
        }
        if(!inplace){
            this.modal_stack.push(this.current)
            this.hide(this.current.modal_id)
        } else {
            param.close_listeners = param.close_listeners.concat(this.current.close_listeners)
        }
        this.current = undefined
        param.option['onModalClosed'] = () => {
            this.popup(param.modal_id)
            console.log('modal close, new current', this, this.current)
        }
        this.current = param
    }


    update(modal_id:string, option:ModalOption){
        const current = this.current
        if(current) {
            if(modal_id === current.modal_id){
                current.option = {...current.option, ...option}
            }
        }

    }

    render(){
        const nodes: VNode[] = []
        for(const modal_param of this.modal_stack){
            const modal_id = modal_param.modal_id
            const slot_render = modal_param.slot_render ?? (() => ([]))
            const option = modal_param.option
            nodes.push(h(Dialog, {ref: `modal_${modal_id}`, showNow:true, modal_id:modal_id, ...option}, {
                default: () => {
                    return slot_render()
                }
            }))
        }
        if(this.current){
            const current = this.current
            const modal_id = current.modal_id
            const slot_render = current.slot_render ?? (() => ([]))
            const option = current.option
            nodes.push(h(Dialog, {ref: `modal_${modal_id}`, showNow:true, modal_id:modal_id, ...option}, {
                default: () => {
                    return slot_render()
                }
            }))
        }
        return nodes;
    }

    show(modal_id?:string){
        if(!modal_id || modal_id.length == 0){
            return
        }
        const ref = `modal_${modal_id}`
        this.app && this.app.$refs[ref].show()
    }

    hide(modal_id?:string){
        if(!modal_id || modal_id.length == 0){
            return
        }
        const ref = `modal_${modal_id}`
        this.app && this.app.$refs[ref].hide()
    }

    popup(modal_id?:string){
        if(!modal_id || modal_id.length == 0){
            return
        }
        if(this.current && this.current?.modal_id === modal_id){
            if(this.modal_stack.length > 0){
                const current = this.current
                const param = this.modal_stack.pop()
                this.current = param
                this.show(param?.modal_id)
                for(const listener of current.close_listeners){
                    listener(current)
                }
            } else {
                this.close()
            }

        }
    }

    close(){
        const param = this.root_modal
        if(this.root_modal){
            this.reset()
        }
        if(param){
            for(const listener of param.close_listeners){
                listener(param)
            }
        }
    }

    reset() {
        this.current = undefined
        this.root_modal = undefined
        this.modal_stack = []
    }
}

let privacy_cancelled_times = 0

export const helpers = reactive({
    modal_helper: new ModalHelper()
})

export const modal_helper = helpers.modal_helper


export interface RenderContext {
    route: string;
    modal_id: string | undefined;
    locals?: Record<string, any>
}

function with_context(context: RenderContext, args:Record<string, any>){
    const new_context = Object.assign({}, context);
    return Object.assign(new_context, args)
}

export const App = defineComponent({
    name: "App",
    data() {
        const app_id = appGlobal.app_id
        modal_helper.setApp(this)
        return {
            app_id: app_id,
            loading: false,
            modal_helper: modal_helper,
            alert_helper: new AlertHelper(this),
            ad_helper: new AdHelper(modal_helper),
            theme: app_platform.getTheme()
        }
    },
    computed: {
        page() {
            return Page.getPage((this as any).app_id)
        }
    },
    watch:{
        "page.route"() {
            if(history.pushState) {
                history.pushState(null, '', `#${this.page.route}`);
            }
            else {
                location.hash = `#${this.page.route}`;
            }
        },
        "page.version"() {
            this.modal_helper.reset()
        }
    },
    created() {
        const app_core = AppCore.getCore(this.app_id)
        const context:RenderContext = {
            route: '/unknown',
            modal_id: undefined
        }
        window.addEventListener('popstate', (evt) => {
            this.handleBackTo(evt.target, context)
        })
        if( window.location.hash.length > 1){
            this.navigateTo(window.location.hash.slice(1), context)
        } else {
            if (app_platform.mustAgreePrivacy() && !app_core.privacy_agreed){
                this.showPrivacyModal()
            } else {
                console.log('session start')
                this.sessionStart()
            }

        }
    },
    beforeMount() {
        const theme = app_platform.getTheme()
        if(typeof theme  === 'string' && theme.length > 0){
            if(theme in themes_all){
                changeTheme(this.app_id, theme, () => {})
            } else {
                console.log(`Theme ${theme} not supported.`)
            }
        }
    },
    methods: {
        showPrivacyModal(content_html?: string){
            const app_core = AppCore.getCore(this.app_id)
            const modal_id = this.modal_helper.new_modal_id()
            const modal_updater = this.modal_helper.open(modal_id, {
                actions: [{
                    "text": i18next.t('view_privacy_detail'),
                    clicked: async () => {
                        const content_link = app_core.config.privacyUrl
                        if(content_link){
                            try {
                                const html_content = await app_core.getContent(content_link)
                                modal_updater.update({
                                    actions: [],
                                    content_html: html_content
                                })
                            } catch (err){
                                this.alert_helper.show(i18next.t('unable_connect_to_server'))
                            }
                        }
                    }
                }],
                content_html: content_html ?? i18next.t('privacy_html_summary'),
                actionsVertical: true,
                actionConfirmText: i18next.t('agree'),
                actionCancelText: i18next.t('disagree'),
                onModalConfirmed: () => {
                    app_core.savePrivacyAgreed()
                    this.alert_helper.show(i18next.t('loading_and_wait'))
                    this.sessionStart()
                },
                onModalCancelled: () => {
                    const p = app_platform.getPlatform()
                    const name = p.name.toLowerCase()
                    if (name == 'android'){
                        this.alert_helper.show(i18next.t('privacy_disagree_confirm_android'))
                    } else {
                        this.alert_helper.show(i18next.t('privacy_disagree_confirm'))
                    }

                    privacy_cancelled_times += 1
                    if(privacy_cancelled_times >= 3){
                        app_platform.exitApp()
                    }
                    setTimeout(() => {
                        this.showPrivacyModal(i18next.t('privacy_cancelled_content'));
                    }, 1000);
                }
            })
        },

        sessionStart(){
            const timerId = setTimeout(()=> {
                this.loading = true;
            }, 1000)
            const app_core = AppCore.getCore(this.app_id)
            app_core.sessionStart().then((commands: HolaCommand[]) => {
                console.log('session start.')
                clearTimeout(timerId)
                this.loading = false
                this.handleImmediateCommands(commands, {route:"/", modal_id: undefined, })
            }).catch((err: Error) => {
                console.log('load home page error.', err)
                clearTimeout(timerId)
                this.loading = false
                const modal_id = this.modal_helper.new_modal_id()
                this.modal_helper.open(modal_id, {
                    text: i18next.t('makesure_network_and_latest_version'),
                    actionsVertical: true,
                    actionConfirmText: i18next.t('retry_text'),
                    onModalConfirmed: () => {
                        this.alert_helper.show(i18next.t('retring_and_waiting'))
                        app_platform.logEvent(AnalyticsEventKind.button_event, {
                            route: this.page.route,
                            text: "errdlg_confirm"
                        })
                        this.sessionStart()
                    }
                })
            })
        },

        callAction(args:Record<string, any>, context: RenderContext){
            const app_core = AppCore.getCore(this.app_id)
            app_core.callAction(args).then((commands: HolaCommand[]) => {
                this.handleImmediateCommands(commands, context)
            }).catch((err: Error) => {
                throw err;
            })
        },

        loginWeixin(context: RenderContext) {
            const app_core = AppCore.getCore(this.app_id)
            app_core.loginWeixin().then((commands: HolaCommand[]) => {
                this.handleImmediateCommands(commands, context)
            }).catch((err: Error) => {
                throw err;
            })
        },

        pageInteract(name:string, event:string, handler:string, page:Page, context: RenderContext){
            const timerId = setTimeout(()=> {
                this.loading = true;
            }, 1000)
            const app_core = AppCore.getCore(this.app_id)
            let locals = page.locals
            if(context.locals){
                locals = context.locals
                locals['_more'] = page.locals
            }
            app_core.pageInteract(name, event, handler, locals).then((commands: HolaCommand[]) => {
                clearTimeout(timerId)
                this.loading = false
                this.handleImmediateCommands(commands, context)
            }).catch((err: Error) => {
                clearTimeout(timerId)
                this.loading = false
                const modal_id = this.modal_helper.new_modal_id()
                this.modal_helper.open(modal_id, {
                    text: i18next.t('makesure_network_and_latest_version'),
                    actionsVertical: true,
                    actionConfirmText: i18next.t('retry_text'),
                    onModalConfirmed: () => {
                        this.alert_helper.show(i18next.t('retring_and_waiting'))
                        app_platform.logEvent(AnalyticsEventKind.button_event, {
                            route: this.page.route,
                            text: "errdlg_confirm"
                        })
                        this.pageInteract(name, event, handler, page, context)
                    }
                })
            })
        },

        dialogInteract(name:string, event:string, handler:string, page:Page, context: RenderContext){
            const timerId = setTimeout(()=> {
                this.loading = true;
            }, 1000)
            const app_core = AppCore.getCore(this.app_id)
            let locals = page.locals
            if(context.locals){
                locals = context.locals
                locals['_more'] = page.locals
            }

            app_core.dialogInteract(context.modal_id ?? "", name, event, handler, locals).then((commands: HolaCommand[]) => {
                clearTimeout(timerId)
                this.loading = false
                this.handleImmediateCommands(commands, context)
            }).catch((err: Error) => {
                clearTimeout(timerId)
                this.loading = false
                const modal_id = this.modal_helper.new_modal_id()
                this.modal_helper.open(modal_id, {
                    text: i18next.t('makesure_network_and_latest_version'),
                    actionsVertical: true,
                    actionConfirmText: i18next.t('retry_text'),
                    onModalConfirmed: () => {
                        this.alert_helper.show(i18next.t('retring_and_waiting'))
                        app_platform.logEvent(AnalyticsEventKind.button_event, {
                            route: this.page.route,
                            text: "errdlg_confirm"
                        })
                        this.dialogInteract(name, event, handler, page, context)
                    }
                })
            })
        },

        navigateTo(route:string, context: RenderContext){
            const timerId = setTimeout(()=> {
                this.loading = true;
            }, 1000)
            const app_core = AppCore.getCore(this.app_id)
            app_core.navigateTo(route).then((commands: HolaCommand[]) => {
                clearTimeout(timerId)
                this.loading = false
                this.handleImmediateCommands(commands, context)
            }).catch((err: Error) => {
                clearTimeout(timerId)
                this.loading = false
                const modal_id = this.modal_helper.new_modal_id()
                this.modal_helper.open(modal_id, {
                    text: i18next.t('makesure_network_and_latest_version'),
                    actionsVertical: true,
                    actionConfirmText: i18next.t('retry_text'),
                    onModalConfirmed: () => {
                        this.alert_helper.show(i18next.t('retring_and_waiting'))
                        app_platform.logEvent(AnalyticsEventKind.button_event, {
                            route: this.page.route,
                            text: "errdlg_confirm"
                        })
                        this.navigateTo(route, context)
                    }
                })
            })
        },

        playableNext(level_id:string, context: RenderContext) {
            const app_core = AppCore.getCore(this.app_id)
            app_core.playableNext(level_id).then((commands: HolaCommand[]) => {
                this.handleImmediateCommands(commands, context)
            }).catch((err: Error) => {
                throw err;
            })
        },

        playableRetry(level_id:string, context: RenderContext) {
            const app_core = AppCore.getCore(this.app_id)
            app_core.playableRetry(level_id).then((commands: HolaCommand[]) => {
                this.handleImmediateCommands(commands, context)
            }).catch((err: Error) => {
                throw err;
            })
        },

        playableCompleted(played: PlayableResult, context: RenderContext) {
            const app_core = AppCore.getCore(this.app_id)
            app_core.playableCompleted(played).then((commands: HolaCommand[]) => {
                this.handleImmediateCommands(commands, context)
            }).catch((err: Error) => {
                throw err;
            })
        },

        handleBackTo(target: any, context: RenderContext) {
            const new_hash = (target as Window).location.hash
            if (new_hash.length > 1) {
                this.navigateTo(new_hash.slice(1), context)
            }
        },

        executeUseItem(item_name: string, context:RenderContext){
            const app_core = AppCore.getCore(this.app_id)
            app_core.itemUse(item_name).then((commands: HolaCommand[]) => {
                this.handleImmediateCommands(commands, context)
            }).catch((err: Error) => {
                throw err;
            })
        },

        executeBuyItem(item_name: string, context:RenderContext){
            const app_core = AppCore.getCore(this.app_id)
            app_core.itemBuy(item_name).then((commands: HolaCommand[]) => {
                this.handleImmediateCommands(commands, context)
            }).catch((err: Error) => {
                throw err;
            })
        },

        executeShowAd(ad_args: Record<string, any>, callback:Function) {
            console.log('show ad', ad_args)
            this.ad_helper.showAdNow(ad_args as AdShowOptions, (ret: ConditionResponse) => {
                if(ret.ok){
                    app_platform.logEvent(AnalyticsEventKind.ad_show_event, {
                        name: "active",
                        route: this.page.route,
                        vendor: ad_args['ad_vendor'],
                        ad_type: ad_args['ad_type']
                    })
                }

                callback(ret)
            })
        },

        async handleImmediateCommands(commands: HolaCommand[], context: RenderContext){
            for(const [idx, command] of commands.entries()){
                if(command.name === 'start_new_session'){
                    this.sessionStart()
                } else if(command.name === 'show_motion'){
                    const args = command.args as ShowMotionCommandArg
                    showMotion(args.name, args.args);
                } else if (command.name === 'show_alert'){
                    const args = command.args as ShowAlertCommandArg
                    const msg = args.text
                    const title = args.title
                    const duration = args.duration ?? 3000
                    const extra: Record<string, any> = {}
                    let severity:any = "info"
                    console.log('show_alert', args)
                    // this.alert_helper.show(msg, title)
                    for(const tag of args.tags ?? []){
                        if (["info", "success", "warn", "error"].includes(tag)){
                            severity = tag
                        }

                        if (["top-right", "top-left", "bottom-left", "bottom-right"].includes(tag)){
                            extra['group'] = {
                                "top-right": "tr", "top-left": "tl",
                                "bottom-left": "bl", "bottom-right": "br"}[tag]
                        }
                    }
                    this.$toast.add({ severity: severity, ...extra, summary: title, detail: msg, life: duration })
                } else if (command.name === 'show_modal'){
                    const open_modal = command.args as ModalElement
                    const modal_id = this.modal_helper.new_modal_id()
                    let dlg_context = { ...context }
                    dlg_context.modal_id = modal_id
                    dlg_context.locals = Object.assign({}, (open_modal.locals ?? {}))

                    await this.modal_helper.open_wait(modal_id,
                        this.getModalOption(open_modal, dlg_context),
                        context,
                        () => {
                            if(open_modal.elements){
                                return this.renderModalElements(open_modal.elements, dlg_context)
                            }
                        }
                    )
                } else if (command.name === 'close_modal'){
                    const args = command.args as CloseModalArgs
                    const modal_id = args.modal_id
                    await this.modal_helper.popup(modal_id)
                } else if (command.name === 'init_ad') {
                    const args = (command as InitAdCommand).args as InitAdCommandArg
                    for(const config of args.configs) {
                        this.ad_helper.initAd(config)
                    }
                } else if (command.name === 'show_ad') {
                    const args = (command as ShowAdCommand).args as ShowAdCommandArg
                    this.ad_helper.showAdNow(args, (ret: ConditionResponse) => {
                        const leftCommands = commands.slice(idx+1)
                        if(leftCommands.length > 0){
                            this.handleImmediateCommands(leftCommands, context)
                        }
                    })
                    app_platform.logEvent(AnalyticsEventKind.ad_show_event, {
                        name: "passive",
                        route: this.page.route,
                        vendor: args.ad_vendor,
                        ad_type: args.ad_type
                    })
                    break;
                } else if (command.name === 'playable_apply') {
                    const args = (command as PlayableApplyCommand).args as PlayableApplyCommandArg
                    const effect = args.effect
                    const playable = this.$refs.playable_0 as PlayableComponent
                    if (playable){
                        playable.apply(effect)
                    }
                } else {
                    console.error(`no handler for immediate command ${command.name}`)
                }
            }
        },

        executeAction(action: string, args: Record<string, any> = {}, context: RenderContext){
            console.log('execute action: ', action, args)
            const acts = action.split('.')
            if(acts.length < 1){
                console.error(`invalid action ${action}, with arg ${args}`)
                return
            }
            const ns = acts[0]

            if(ns === 'builtin'){
                const func = acts[1]
            } else if (ns === 'login') {
                const func = acts[1]
                if ( func === 'weixin' ){
                    this.loginWeixin(context)
                } else {
                    console.log(`unknown login action ${action}`)
                }
            } else if (ns === 'logout') {
                const func = acts[1]
            } else if (ns === 'route') {
                const func = acts[1]
                if ( func === 'back'){
                    window.history.back()
                } else if ( func === 'navigate_to'){
                    const target = args.route ?? '/'
                    this.navigateTo(target, context)
                } else if ( func === 'refresh'){
                    const target = this.page.route
                    this.navigateTo(target, context)
                } else {
                    console.log(`unknown playable action ${action}`)
                }
            } else if (ns === 'action') {
                const func = acts[1]
                if(func === 'call'){
                    this.callAction(args, context)
                } else {
                    console.log(`unknown action ${action}`)
                }
            } else if (ns === 'playable') {
                const func = acts[1]
                const playable = this.$refs.playable_0 as PlayableComponent
                if(func === 'retry'){
                    this.playableRetry(args.level_id, context)
                    app_platform.logEvent(AnalyticsEventKind.playable_event, {
                        name: "retry",
                        route: this.page.route,
                        level_id: args.level_id ?? ""
                    })
                } else if (func === 'next'){
                    this.playableNext(args.level_id, context)
                    app_platform.logEvent(AnalyticsEventKind.playable_event, {
                        name: "next",
                        route: this.page.route,
                        level_id: args.level_id ?? ""
                    })
                } else if (func === 'apply'){
                    playable.apply(args.effect)
                    app_platform.logEvent(AnalyticsEventKind.playable_event, {
                        name: "apply",
                        route: this.page.route,
                        level_id: args.level_id ?? "",
                        effect: args.effect
                    })
                } else {
                    console.log(`unknown playable action ${action}`)
                }
            } else if (ns === 'item') {
                const func = acts[1]
                if(func === 'use'){
                    this.executeUseItem(args["item_name"], context)
                    app_platform.logEvent(AnalyticsEventKind.item_event, {
                        name: "use",
                        route: this.page.route,
                        item_name: args.item_name,
                        item_count: 1
                    })
                }else if(func === 'buy'){
                    this.executeBuyItem(args["item_name"], context)
                    app_platform.logEvent(AnalyticsEventKind.item_event, {
                        name: "buy",
                        route: this.page.route,
                        item_name: args.item_name,
                        item_count: 1
                    })
                } else {
                    console.log(`unknown item action ${action}`)
                }
            } else if (ns === 'ad') {
                const func = acts[1]
                if(func === 'show'){
                    const ad_args = args.ad_args
                    this.executeShowAd(ad_args, () => {

                    })
                    app_platform.logEvent(AnalyticsEventKind.ad_show_event, {
                        name: "active",
                        route: this.page.route,
                        vendor: ad_args.ad_vendor,
                        ad_type: ad_args.ad_type
                    })
                } else {
                    console.log(`unknown ad action ${action}`)
                }
            } else {
                console.log(`unknown action ${action}`)
            }
        },

        executeConditionAction(action: string, args: Record<string, any>, callback: Function){
            console.log('execute condition action: ', action, args)
            const acts = action.split('.')
            if(acts.length < 1){
                console.error(`invalid action ${action}, with arg ${args}`)
                return
            }
            const ns = acts[0]
            if (ns === 'playable') {
                const func = acts[1]
                const playable = this.$refs.playable_0 as PlayableComponent
                if (func === 'canApply'){
                    const can = playable.canApply(args.effect)
                    callback(can)
                } else if(func === 'apply') {
                    const ret = playable.apply(args.effect)
                    if (ret.ok){
                        callback({ok: ret.ok, message: ret.message})
                    } else {
                        callback({ok: ret.ok, message: ret.error})
                    }
                } else {
                    callback({ok: false, message: i18next.t('unsupported_condition')})
                }

            } else if (ns === 'ad') {
                const func = acts[1]
                if(func === 'show'){
                    const ad_args = args
                    this.executeShowAd(ad_args, (cond: ConditionResponse) => {
                        callback(cond)
                    })

                } else {
                    callback({ok: false, message: i18next.t('unsupported_condition')})
                }
            } else {
                callback({ok: false, message: i18next.t('unsupported_condition')})
            }
        },

        tranformStyle(style: Record<string, any>){
            const new_style: Record<string, any> = {}
            for(const [key, value] of Object.entries(style)){
                if(key === 'size'){
                    new_style['h_size'] = value,
                    new_style['v_size'] = value
                } else {
                    new_style[key] = value
                }
            }
            return new_style
        },

        renderNavBar(element: NavBarElement, context: RenderContext): VNode {
            return h(NavBar, {
                title: element.title ?? "",
                showHome:element.show_home || false,
                showBack: element.show_back || false,
                onHomeClicked: () => {
                    this.navigateTo('/', context);
                    app_platform.logEvent(AnalyticsEventKind.button_event, {
                        route: this.page.route,
                        text: 'home'
                    })
                },
                onBackClicked: () => {
                    window.history.back()
                    app_platform.logEvent(AnalyticsEventKind.button_event, {
                        route: this.page.route,
                        text: 'back'
                    })
                }
            }, {
                default: () => {
                    const nodes = []
                    if(element.elements){
                        for(const el of element.elements){
                            nodes.push(this.renderModalWidget(el, context))
                        }
                    }
                    return nodes
                }
            })
        },

        renderDecoration(element: DecorationElement, context: RenderContext): VNode {
            return renderDecorationComponent(element.name, {...element.properties }, undefined)
        },

        renderMotion(element: MotionElement, context: RenderContext): VNode {
            return renderMotionComponent(element.name, { ...element.properties }, undefined)
        },

        renderPlayable(element: PlayableElement, context: RenderContext): VNode {
            const app_core = AppCore.getCore(this.app_id)
            return renderPlayableComponent(element.name, { ref:"playable_0", config: element.config,
                level: {collection: element.collection, level_id: element.level_id},
                onSucceed: async (played: PlayableResult) => {
                    if(!played.level){
                        played.level = {}
                    }
                    played.level.level_id = element.level_id
                    app_platform.logEvent(AnalyticsEventKind.playable_event, {
                        name: "succeed",
                        route: this.page.route,
                        level_id: element.level_id
                    })
                    const commands = await app_core.playableCompleted(played)
                    this.handleImmediateCommands(commands, context)

                },
                onFailed: async (played: PlayableResult) => {
                    if(!played.level){
                        played.level = {}
                    }
                    played.level.level_id = element.level_id
                    app_platform.logEvent(AnalyticsEventKind.playable_event, {
                        name: "failed",
                        route: this.page.route,
                        level_id: element.level_id
                    })
                    const commands = await app_core.playableCompleted(played)
                    this.handleImmediateCommands(commands, context)
                },
                onPlayed: () => {
                    app_platform.logEvent(AnalyticsEventKind.played_event, {
                        name: element.name,
                        route: this.page.route,
                        level_id: element.level_id
                    })
                }
            }, undefined)
        },

        renderSubElements(elements: HolaElement[] | undefined, context: RenderContext): VNode[] {
            const sub_nodes:VNode[] = []
            if(elements && elements?.length > 0){
                for(const sub_element of elements){
                    const n = this.renderElement(sub_element as HolaElement, context)
                    if(n !== undefined){
                        if(Array.isArray(n)){
                            sub_nodes.push(...n)
                        } else {
                            sub_nodes.push(n)
                        }
                    }
                }
            }
            return sub_nodes
        },

        renderHeader(element: HeaderElement, context: RenderContext): VNode {
            return h(Header, {}, {
                "start": () => {
                    return this.renderSubElements(element.start_elements, context)
                },
                "center": () => {
                    return this.renderSubElements(element.elements, context)
                },
                "end": () => {
                    return this.renderSubElements(element.end_elements, context)
                }
            })
        },

        renderFooter(element: FooterElement, context: RenderContext): VNode {
            const app_core = AppCore.getCore(this.app_id)
            const footer_main = element.element
            let text = element.text ?? ""
            if (footer_main && footer_main.type == 'plain-text') {
                text = (footer_main as PlainTextObject)["text"]
            }
            const right_actions: ActionDefinition[] = []
            if (element['right_elements']) {
                for (const simple_action of element['right_elements']) {
                    right_actions.push({
                        icon: app_core.full_link(simple_action.icon) ?? '',
                        text: simple_action.text,
                        clicked: () => {
                            console.log('will rout to ', simple_action.route)
                            if(simple_action.route) {
                                this.navigateTo(simple_action.route, context)
                            }
                            app_platform.logEvent(AnalyticsEventKind.button_event, {
                                route: this.page.route,
                                text: simple_action.text
                            })
                        }
                    })
                }
            }
            return h(Footer, { text: text, rightActions: right_actions })
        },

        renderDivider(element: SeparatorElement, context: RenderContext){
            return h(Divider)
        },

        renderTitle(element: TitleElement, context: RenderContext){
            return h(Title, {title: element.title, level: element.level, sub_title: element.sub_title ?? ""})
        },

        renderLink(element: LinkElement, context: RenderContext){
            return h(Link, {text: element.text,
                target_url: element.target_url,
                open_mode: element.open_mode ?? "new",
                onClicked: () => {
                    const url = element.target_url
                    const open_mode = element.open_mode ?? "new"
                    if(open_mode === "new"){
                        app_platform.openUrl(url)
                    }
                }
            })
        },

        renderAvatar(element: AvatarElement, context: RenderContext){
            return h(Avatar, {...element})
        },

        renderCheckbox(element: CheckboxElement, context: RenderContext){
            return h(Checkbox, {...element})
        },

        renderProgressbar(element: ProgressbarElement, context: RenderContext){
            return h(Progressbar, {...element})
        },

        renderCalendar(element: CalendarElement, context: RenderContext){
            return h(Calendar, {...element})
        },

        renderInputSwitch(element: InputSwitchElement, context: RenderContext){
            return h(InputSwitch, {...element})
        },

        renderMultiSelect(element: MultiSelectElement, context: RenderContext){
            const props: Record<string, any> = Object.assign({}, element)
            delete props.type
            delete props.options
            const options: Array<Record<string, any>> = []
            for(const opt of element.options?? []){
                if(opt.type && opt.type == 'element-option'){
                    options.push({
                        label: opt.label,
                        name: opt.name,
                        slot: () => {
                            return this.renderElementOrList(opt.element, context)
                        }
                    })
                } else {
                    options.push({
                        label: opt.label,
                        name: opt.name
                    })
                }
            }
            props.options = options

            return h(MultiSelect, {...props})
        },

        renderTextarea(element: TextareaElement, context: RenderContext){
            return h(Textarea, {...element})
        },

        renderQrcode(element: QrcodeElement, context: RenderContext){
            const props: Record<string, any> = {}
            props.value = element.code
            return h(Qrcode, {...props})
        },

        renderParagraph(element: ParagraphElement, context: RenderContext){
            return h(Paragraph, {
                text: element.text,
                align: element.align
            })
        },

        renderBulletedList(element: BulletedListElement, context: RenderContext){
            return h(BulletedList, {
                texts: element.texts
            })
        },

        renderStarRating(element: StarRatingElement, context: RenderContext){
            return h(StarRating, {rating:element.rating, annimation:element.animate})
        },

        renderIcon(element: IconElement, context: RenderContext){
            const style = element.style ?? {}
            const app_core = AppCore.getCore(this.app_id)
            return h(Icon, {...style, icon:app_core.full_link(element.icon)})
        },

        renderIconText(element: IconTextElement, context: RenderContext){
            const style = element.style ?? {}
            const app_core = AppCore.getCore(this.app_id)
            return h(IconText, {...style, text:element.text, icon:app_core.full_link(element.icon)})
        },

        renderIconNumber(element: IconNumberElement, context: RenderContext){
            const app_core = AppCore.getCore(this.app_id)
            return h(IconCountText, {
                icon: app_core.full_link(element.icon),
                animate: element.animate,
                wrapper: {
                    count: element.number
                }
            })
        },

        renderIconTitle(element: IconTitleElement, context: RenderContext){
            const app_core = AppCore.getCore(this.app_id)
            return h(IconTitle, {icon: app_core.full_link(element.icon), count:element.count})
        },

        renderButton(element: ButtonElement, context: RenderContext){
            const actionFn = () => {
                if(element.action){
                    this.executeAction(element.action, element.args, context)
                }
            }

            const style = this.tranformStyle(element.style ?? {})
            let close_modal = false
            if(element.action_props){
                close_modal = element.action_props!['close_modal'] ?? false
            }
            let menu: any = undefined
            const menu_name = 'menu_xxxxxx222'
            let modal: any = undefined
            let click_handler = element.events?.click ?? null
            if(click_handler){
                let click_handlers:Array<any> = []
                if(!Array.isArray(click_handler)){
                    click_handlers = [click_handler]
                } else {
                    click_handlers = click_handler
                }
                for(const handler of click_handlers){
                    if(['open-menu'].includes(handler.type)){
                        const items = handler.menu.items ?? []
                        menu = h(Menu, {
                            items: items,
                            popup: true,
                            ref: menu_name,
                            onMenuItemClicked: (handler: string) => {
                                this.pageInteract("", 'click', handler, this.page, context)
                            }
                        }, {})
                    } else if(['open-modal'].includes(handler.type)) {

                    }
                }
            }



            const btn = h(Button, {
                text: element.text,
                icon: element.icon,
                href: element.href ?? "",
                open_new: element.open_new,
                sub_text: element.sub_text ?? "",
                disable: element.disable ?? false,
                disable_text: element.disable_text ?? "",
                style: style,
                ...style,
                color: element.style?.color ?? "surface",
                onClicked:() => {
                    if(element.show_ad){
                        this.ad_helper.showAdNow(element.show_ad as AdShowOptions, (ret: ConditionResponse) => {
                            if(ret.ok){
                                if(element.action){
                                    actionFn();
                                }
                            } else {
                                if(ret.message){
                                    this.alert_helper.show(ret.message)
                                }
                            }
                            if (context.modal_id !== undefined){
                                this.modal_helper.popup(context.modal_id)
                            }
                        })
                        app_platform.logEvent(AnalyticsEventKind.ad_show_event, {
                            name: "active",
                            route: this.page.route,
                            vendor: element.show_ad['ad_vendor'],
                            ad_type: element.show_ad['ad_type']
                        })
                    } else if (element.open_modal){
                        this.openModal(element.open_modal as ModalElement, element.open_modal_args ?? {}, context)
                    } else if (element.action_condition && element.action){
                        const action = element.action_condition.action
                        const args = element.action_condition.args
                        this.executeConditionAction(action, args, (ret: ConditionResponse)=>{
                            if(ret.ok){
                                actionFn();
                                if (close_modal && context.modal_id !== undefined){
                                    this.modal_helper.popup(context.modal_id)
                                }
                            } else {
                                if(ret.message){
                                    this.alert_helper.show(ret.message)
                                }
                            }

                        })
                    } else if(element.action) {
                        actionFn()
                        if (close_modal && context.modal_id !== undefined){
                            this.modal_helper.popup(context.modal_id)
                        }
                    } else if(element.handlers) {
                        this.pageInteract("", 'click', element.handlers.click ?? "", this.page, context)
                    } else if(element.name) {
                        this.pageInteract(element.name, 'click', "", this.page, context)
                    } else {
                        if(menu){
                            (this.$refs[menu_name] as any).toggle(event)
                        }
                    }
                    app_platform.logEvent(AnalyticsEventKind.button_event, {
                        route: this.page.route,
                        text: element.text
                    })
                }
            })

            if(menu){
                return [btn, menu]
            }else{
                return btn
            }
        },

        renderIconButton(element: ButtonElement, context: RenderContext){
            const actionFn = () => {
                if(element.action){
                    this.executeAction(element.action, element.args, context)
                }
            }

            const style = this.tranformStyle(element.style ?? {})
            return h(IconButton, {
                text: element.text,
                icon: element.icon,
                ...style,
                color: element.style?.color ?? "surface",
                onClicked:() => {
                    if(element.action){
                        if(element.show_ad){
                            this.ad_helper.showAdNow(element.show_ad as AdShowOptions, (ret: ConditionResponse) => {
                                if(ret.ok){
                                    actionFn();
                                } else {
                                    if(ret.message){
                                        this.alert_helper.show(ret.message)
                                    }
                                }
                                if (context.modal_id !== undefined){
                                    this.modal_helper.popup(context.modal_id)
                                }
                            })
                            app_platform.logEvent(AnalyticsEventKind.ad_show_event, {
                                name: "active",
                                route: this.page.route,
                                vendor: element.show_ad['ad_vendor'],
                                ad_type: element.show_ad['ad_type']
                            })
                        } else if (element.action_condition){
                            const action = element.action_condition.action
                            const args = element.action_condition.args
                            this.executeConditionAction(action, args, (ret: ConditionResponse)=>{
                                if(ret.ok){
                                    actionFn();
                                } else {
                                    if(ret.message){
                                        this.alert_helper.show(ret.message)
                                    }
                                }
                                if (context.modal_id !== undefined){
                                    this.modal_helper.popup(context.modal_id)
                                }

                            })
                        } else {
                            actionFn()
                        }
                    }
                    app_platform.logEvent(AnalyticsEventKind.button_event, {
                        route: this.page.route,
                        text: element.text
                    })
                }
            })
        },

        renderProgressBar(element: ProgressBarElement, context: RenderContext){
            const props:Record<string, any> = {
            }
            if(element.percent !== undefined){
                props['percent'] = element.percent
            }

            if(element.value !== undefined && element.total !== undefined){
                props['value'] = element.value
                props['total'] = element.total
            }
            return h(ProgressBar, {...props, ...element.style}, {})
        },

        renderAnnotationText(element: AnnotationTextObject, context: RenderContext) {
            return h(AnnotationText, {text: element.text, annotation: element.annotation})
        },

        renderPlainText(element: PlainTextObject, context: RenderContext) {
            return h('div', {}, element.text)
        },

        renderRowLine(element: RowLineElement, context: RenderContext) {
            return h(Row, {...element.style}, {
                default: () => {
                    const nodes:VNode[] = []
                    for(const el of element.elements){
                        const sub_node = this.renderElement(el, context)
                        if(Array.isArray(sub_node)){
                            nodes.push(...sub_node)
                        } else if(sub_node){
                            nodes.push(sub_node)
                        }
                    }
                    return nodes
                }
            })
        },

        renderColumn(element: ColumnElement, context: RenderContext) {
            return h(Column, {...element.style}, {
                default: () => {
                    const nodes = []
                    for(const el of element.elements){
                        nodes.push(this.renderElement(el, context))
                    }
                    return nodes
                }
            })
        },

        renderImage(element: ImageElement, context: RenderContext) {
            const args: any = {
                image_url: element.image_url
            }
            if (element.image_type){
                args.image_type = element.image_type
            }
            return h(ImageView, {...args, ...element.style})
        },

        renderVideo(element: VideoElement, context: RenderContext) {
            const args: any = {
                video_url: element.video_url,
                poster_url: element.poster_url,
                aspect: element.aspect,
                autoplay: element.autoplay ?? false
            }
            if (element.video_type){
                args.video_type = element.video_type
            }
            return h(VideoPlayer, {...args, ...element.style})
        },

        renderModalWidget(element:ModalWidgetElement, context:RenderContext): VNode | VNode[] | undefined {
            if(!element){
                return undefined
            }
            if (element.type == 'separator' || element.type == 'divider') {
                return this.renderDivider(element as SeparatorElement, context)
            } else if (element.type == 'title') {
                return this.renderTitle(element as TitleElement, context)
            } else if (element.type == 'link') {
                return this.renderLink(element as LinkElement, context)
            } else if (element.type == 'paragraph') {
                return this.renderParagraph(element as ParagraphElement, context)
            } else if (element.type == 'bulleted-list') {
                return this.renderBulletedList(element as BulletedListElement, context)
            } else if (element.type == 'button') {
                return this.renderButton(element as ButtonElement, context)
            } else if (element.type == 'icon-button') {
                return this.renderIconButton(element as ButtonElement, context)
            } else if (element.type == 'progress-bar') {
                return this.renderProgressBar(element as ProgressBarElement, context)
            } else if (element.type == 'star-rating') {
                return this.renderStarRating(element as StarRatingElement, context)
            } else if (element.type == 'icon') {
                return this.renderIcon(element as IconElement, context)
            } else if (element.type == 'icon-text') {
                return this.renderIconText(element as IconTextElement, context)
            } else if (element.type == 'icon-number') {
                return this.renderIconNumber(element as IconNumberElement, context)
            } else if (element.type == 'icon-title') {
                return this.renderIconTitle(element as IconTitleElement, context)
            } else if (element.type == 'annotation-text') {
                return this.renderAnnotationText(element as AnnotationTextObject, context)
            } else if (element.type == 'row') {
                return this.renderRowLine(element as RowLineElement, context)
            } else if (element.type == 'column') {
                return this.renderColumn(element as ColumnElement, context)
            } else if (element.type == 'plain-text') {
                return this.renderPlainText(element as PlainTextObject, context)
            } else if (element.type == 'image') {
                return this.renderImage(element as ImageElement, context)
            } else if (element.type == 'video') {
                return this.renderVideo(element as VideoElement, context)
            } else if (element.type == 'nav-menu') {
                return this.renderNavMenu(element as NavMenuElement, context)
            } else if (element.type == 'data-table') {
                return this.renderDataTable(element as DataTableElement, context)
            } else if (element.type === "input") {
                return this.renderInput(element as InputElement, context)
            } else if (element.type === "dropdown") {
                return this.renderDropdown(element as DropdownElement, context)
            } else if (element.type === "tag") {
                return this.renderTag(element as TagElement, context)
            } else if (element.type === "avatar") {
                return this.renderAvatar(element as AvatarElement, context)
            } else if (element.type === "checkbox") {
                return this.renderCheckbox(element as CheckboxElement, context)
            } else if (element.type === "progressbar") {
                return this.renderProgressbar(element as ProgressbarElement, context)
            } else if (element.type === "calendar") {
                return this.renderCalendar(element as CalendarElement, context)
            } else if (element.type === "input-switch") {
                return this.renderInputSwitch(element as InputSwitchElement, context)
            } else if (element.type === "multi-select") {
                return this.renderMultiSelect(element as MultiSelectElement, context)
            } else if (element.type === "textarea") {
                return this.renderTextarea(element as TextareaElement, context)
            } else if (element.type === "qrcode") {
                return this.renderQrcode(element as QrcodeElement, context)
            } else if (element.type == 'motion') {
                return this.renderMotion(element as MotionElement, context)
            } else {
                console.warn(`not supported widget type ${element.type}`)
            }
        },

        renderModalElements(elements: ModalWidgetElement[], context:RenderContext): VNode[] {
            const nodes: VNode[] = []
            for(const element of elements){
                const el_node = this.renderModalWidget(element, context)
                if(el_node){
                    if(Array.isArray(el_node)){
                        nodes.push(...el_node)
                    } else {
                        nodes.push(el_node)
                    }
                }
            }
            return nodes
        },

        getModalOption(open_modal: ModalElement, context: RenderContext){
            const title_action = open_modal.title_action ?? undefined
            if(title_action !== undefined &&  Object.keys(title_action).length > 0){
                title_action.clicked = () => {
                    this.executeAction(title_action.action, title_action.args, context)
                }
            }
            const modal_options:Record<string, any> = {
                title: open_modal.title,
                title_action: open_modal.title_action ?? undefined,
                style: open_modal.style ?? {},
                actionConfirmText: open_modal.confirm?.text,
                actionCancelText: open_modal.cancel?.text,
                onModalConfirmed: () => {
                    const name = open_modal.name ?? ""
                    const handler = open_modal.confirm?.click ?? ""
                    if(open_modal.confirm?.action){
                        this.executeAction(open_modal.confirm.action, open_modal.confirm.args, context)
                    } else if( name.length > 0 || handler.length > 0 ) {
                        this.dialogInteract(name, "confirm", handler, this.page, context)
                    } else {
                        this.modal_helper.popup(context.modal_id ?? "")
                    }
                    app_platform.logEvent(AnalyticsEventKind.button_event, {
                        route: this.page.route,
                        text: open_modal.confirm?.text ?? "confirm"
                    })
                },
                onModalCancelled: () => {
                    if(open_modal.cancel?.action){
                        this.executeAction(open_modal.cancel.action, open_modal.cancel.args, context)
                    }
                    app_platform.logEvent(AnalyticsEventKind.button_event, {
                        route: this.page.route,
                        text: open_modal.cancel?.text ?? "cancel"
                    })
                }
            }
            if(open_modal.content){
                modal_options.text = open_modal.content
            }
            return modal_options
        },

        openModal(open_modal: ModalElement, args: Record<string, any>, context: RenderContext){
            const modal_id = this.modal_helper.new_modal_id()
            let dlg_context = { ...context }
            dlg_context.modal_id = modal_id
            dlg_context.locals = {}

            let inplace = false
            if ('inplace' in args){
                inplace = args['inplace']
            }

            if(context.modal_id !== undefined){
                this.modal_helper.open_sub(
                    {
                        modal_id: modal_id,
                        option: this.getModalOption(open_modal, dlg_context),
                        close_listeners: [],
                        slot_render: () => {
                            if(open_modal.elements){
                                return this.renderModalElements(open_modal.elements, dlg_context)
                            }
                        }
                    },
                    context,
                    inplace
                )
            } else {
                this.modal_helper.open(
                    modal_id,
                    this.getModalOption(open_modal, dlg_context),
                    () => {
                        if(open_modal.elements){
                            return this.renderModalElements(open_modal.elements, dlg_context)
                        }
                    }
                )
            }

        },


        renderActionBar(element: ActionBarElement, context: RenderContext): VNode {
            const actions:IconActionDefinition[] = [];
            const app_core = AppCore.getCore(this.app_id)
            for(const el of element.elements){
                if(el.type === 'button'){
                    const action = el as ActionElement
                    actions.push({
                        name: action.text ?? 'default',
                        icon: app_core.full_link(action.icon) ?? '',
                        text: action.text,
                        count: action.count,
                        clicked: () => {
                            if(action.route) {
                                this.navigateTo(action.route, context)
                            } else if (action.open_modal){
                                this.openModal(action.open_modal, action.open_modal_args ?? {}, context)
                            } else if (action.action){
                                this.executeAction(action.action, action.args, context)
                            }

                            app_platform.logEvent(AnalyticsEventKind.button_event, {
                                route: this.page.route,
                                text: action.text
                            })

                        }
                    })
                }
            }
            return h(ActionBar, {actions: actions})
        },

        renderTableView(element: TableViewElement, context: RenderContext): VNode {
            return h(TableView, {
                columns: element.columns,
                showHeader: element.show?.header || false,
                showInnerColumn: element.show?.inner_column || false,
                showInnerRow: element.show?.inner_row || false,
                rows: element.rows,
                cellRender: (cell:any) => {
                    const cell_element = cell as HolaElement;
                    return this.renderElementOrList(cell_element, context)
                }
            })
        },


        renderSideBar(element: SideBarElement, context: RenderContext): VNode {
            return h(SideBar, {
                style: element.style ?? {},
                elements: element.elements ?? []
            }, {
                "default": () => {
                    const elements = element.elements ?? []
                    return this.renderElementOrList(elements, context)
                }
            })
        },

        renderCard(element: CardElement, context: RenderContext): VNode {
            return h(Card, {
                title: element.title ?? "",
                text: element.text ?? "",
                image_src: element.image_src ?? "",
                showBorder: element.show_border ?? true,
                style: element.style ?? {}
            }, {
                default: () => {
                    return this.renderElementOrList(element.elements, context)
                }
            })
        },

        renderInput(element: InputElement, context: RenderContext): VNode {
            const name = element.name ?? ""
            let locals: Record<string, any> =  context.locals ?? this.page.locals
            const input = h(InputText, {
                label: element.label ?? "",
                password: element.password ?? false,
                value: element.value ?? "",
                name: name,
                onTextChanged: (text: string) => {
                    if(name.length > 0){
                        locals[name] = text
                    }
                }
            })
            return input
        },

        renderDropdown(element: DropdownElement, context: RenderContext): VNode {
            const name = element.name ?? ""
            let locals: Record<string, any> =  context.locals ?? this.page.locals
            const input = h(Dropdown, {
                label: element.label ?? "",
                value: element.value ?? "",
                options: element.options ?? [],
                name: name,
                onSelectChanged: (value: string) => {
                    if(name.length > 0){
                        locals[name] = value
                    }
                }
            })
            return input
        },

        renderTag(element: TagElement, context: RenderContext): VNode {
            const tag = h(Tag, {
                text: element.text ?? "",
                color: element.color ?? ""
            })
            return tag
        },

        renderCardSwiper(element: CardSwiperElement, context: RenderContext): VNode {
            return h(CardSwiper, {
                title: element.title ?? "",
                cards: element.elements,
                cardRender: (card: any) => {
                    return this.renderElementOrList(card, context)
                }
            })
        },

        renderLogo(element: LogoElement, context: RenderContext): VNode {
            return h(Logo, { text: element.text ?? "", image_src: element.image_src ?? "" })
        },

        renderHero(element: HeroElement, context: RenderContext): VNode {
            return h(Hero, {
                title: element.title ?? "",
                text: element.text ?? "",
                image_src: element.image_src ?? "",
                annotation_text: element.element })
        },

        renderNavMenu(element: NavMenuElement, context: RenderContext): VNode {
            const style = element.style ?? {}
            const items: MenuItem[] = []
            const app_core = AppCore.getCore(this.app_id)
            for(const item of element.elements){
                items.push({
                    text: item.text,
                    sub_text: item.sub_text ?? "",
                    disable: item.disable ?? false,
                    disable_text: item.disable_text ?? "",
                    icon: app_core.full_link(item.icon),
                    clicked: async () => {
                        if(item.route !== undefined){
                            this.navigateTo(item.route, context)
                        } else if(item.open_url){
                            app_platform.openUrl(item.open_url)
                        } else if(item.open_modal) {
                            const app_core = AppCore.getCore(this.app_id)
                            const modal = item.open_modal
                            const modal_id = this.modal_helper.new_modal_id()
                            const modal_updater = this.modal_helper.open(
                                modal_id,
                                {title:modal.title, actionConfirmText:modal.confirm?.text ?? ''}
                            )
                            if(modal.content_link){
                                try {
                                    const html_content = await app_core.getContent(modal.content_link)
                                    modal_updater.update({content_html: html_content})
                                } catch {
                                    console.log('fetch html error.')
                                    this.alert_helper.show(i18next.t('unable_connect_to_server'))
                                }
                            }

                        }
                        app_platform.logEvent(AnalyticsEventKind.button_event, {
                            route: this.page.route,
                            text: item.text
                        })
                    }
                })
            }
            return h(NavMenu, {...style, items: items})
        },

        renderDataTable(element: DataTableElement, context: RenderContext): VNode {
            const style = element.style ?? {}
            const columns: any[] = []
            const data = []
            for(const obj of element.data ?? []){
                const new_obj = Object.assign({__col_names: {}}, obj)
                for(const [k, v] of Object.entries(obj)){
                    if(k.includes(".")){
                        const new_k = replaceAll(k, '.', '__');
                        (new_obj.__col_names as Record<string, any>)[new_k] = v
                    }
                }
                data.push(new_obj)
            }
            for(const col of (element.columns ?? [])){
                const field_name = col['field'] ?? ""
                if(field_name.indexOf('__col_') == 0) {
                    const new_col = Object.assign({}, col)
                    delete new_col['field']
                    new_col['slot'] = ({locals}: any) => {

                        const new_locals = Object.keys(locals)
                            .filter(key => key.indexOf('__col_') != 0)
                            .reduce((obj:any, key:any) => {
                                obj[key] = locals[key];
                                return obj;
                            }, {});
                        const new_context = with_context(context, {locals: new_locals})
                        return this.renderElementOrList(locals[field_name], new_context)
                    }
                    columns.push(new_col)
                } else  if(field_name.includes('.')){
                    const _name = replaceAll(field_name, '.', '__')
                    const new_name = `__col_names.${_name}`
                    const new_col = Object.assign({}, col)
                    new_col['field'] = new_name
                    columns.push(new_col)
                } else {
                    columns.push(col)
                }
            }
            return h(DataTable, {
                data: data,
                columns: columns,
                style: style,
                paginator: element.paginator
            })
        },

        renderToolbar(element: ToolbarElement, context: RenderContext): VNode {
            const style = element.style ?? {}
            return h(Toolbar, {style: style}, {
                "start": () => {
                    return this.renderElementOrList(element.start_elements ?? [], context)
                },
                "center": () => {
                    return this.renderElementOrList(element.elements ?? [], context)
                },
                "end": () => {
                    return this.renderElementOrList(element.end_elements ?? [], context)
                }
            })
        },

        renderMenu(element: MenuElement, context: RenderContext): VNode {
            const style = element.style ?? {}
            const items: MenuItemObject[] = element.items ?? []

            return h(Menu, {
                style:style,
                items: items,
                label: element.label ?? "",
                icon: element.icon ?? "",
                onMenuItemClicked: (handler: string) => {
                    this.pageInteract("", 'click', handler ?? '', this.page, context)
                }
            })
        },

        renderElementOrList(element: HolaElement | HolaElement[], context: RenderContext): VNode | VNode[] | undefined{
            if(Array.isArray(element)){
                const elements:VNode[] = []
                for(const el of element){
                    const rendered = this.renderElement(el, context)
                    if(rendered){
                        if(Array.isArray(rendered)){
                            elements.push(...rendered)
                        } else {
                            elements.push(rendered)
                        }
                    }
                }
                return elements
            }else{
                return this.renderElement(element, context)
            }
        },

        renderElement(element: HolaElement, context: RenderContext): VNode | VNode[] | undefined {
            if (element.type === "navbar") {
                return this.renderNavBar(element as NavBarElement, context)
            } else if (element.type === "header") {
                return this.renderHeader(element as HeaderElement, context)
            } else if (element.type === "footer") {
                return this.renderFooter(element as FooterElement, context)
            } else if (element.type === "logo") {
                return this.renderLogo(element as LogoElement, context)
            } else if (element.type === "hero") {
                return this.renderHero(element as HeroElement, context)
            } else if (element.type === "nav-menu") {
                return this.renderNavMenu(element as NavMenuElement, context)
            } else if (element.type === "menu") {
                return this.renderMenu(element as MenuElement, context)
            } else if (element.type === "decoration") {
                return this.renderDecoration(element as DecorationElement, context)
            } else if (element.type === "motion") {
                return this.renderMotion(element as MotionElement, context)
            } else if (element.type === "playable") {
                return this.renderPlayable(element as PlayableElement, context)
            } else if (element.type === "action-bar") {
                return this.renderActionBar(element as ActionBarElement, context)
            } else if (element.type === "table-view") {
                return this.renderTableView(element as TableViewElement, context)
            } else if (element.type === "side-bar") {
                return this.renderSideBar(element as SideBarElement, context)
            } else if (element.type === "card") {
                return this.renderCard(element as CardElement, context)
            } else if (element.type === "toolbar") {
                return this.renderToolbar(element as ToolbarElement, context)
            } else if (element.type === "card-swiper") {
                return this.renderCardSwiper(element as CardSwiperElement, context)
            } else {
                return this.renderModalWidget(element as ModalWidgetElement, context)
            }
        },

        renderPage(): VNode {
            const children: VNode[] = []
            for (const element of this.page.elements) {
                const context = {
                    route: this.page.route,
                    modal_id: undefined
                }
                const rendered = this.renderElement(element, context)
                if(rendered){
                    if(Array.isArray(rendered)){
                        children.push(...rendered)
                    } else {
                        children.push(rendered)
                    }

                }
            }
            return h('div', { class: ["page"] }, [...children])
        },

        renderAdditional(): VNode[] {
            const children: VNode[] = []
            const modelNode2 = this.modal_helper.render()
            if (modelNode2) {
                children.push(...modelNode2)
            }

            children.push(this.alert_helper.render())
            children.push(h(Toast, {}, {}))
            children.push(h('canvas', {id:"motion_canvas", class:"motion_canvas"}))
            const app_core = AppCore.getCore(this.app_id)
            if(this.loading){
                children.push(h(Loader))
            }
            return children
        }
    },
    render() {
        const rendered = [this.renderPage(), ...this.renderAdditional()]
        return rendered
    }
})