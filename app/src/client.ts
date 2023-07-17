
import CryptoJS from "crypto-js";
import { DataStore, AppDataStore } from "./db";
import ky, { HTTPError, KyResponse, Options, TimeoutError } from 'ky';
import { app_platform } from "./platform";

export type AnyItem = Record<string | "type", any>

export interface LevelInfo {
    collection?: string
    level_id?:string
    diffculty?: string
}

export interface LevelArchievement {
    score?: number,
    rating?: number,
}

export interface PlayableResult {
    succeed: boolean,
    archievement?: LevelArchievement,
    level?: LevelInfo,
    items?: AnyItem[]
}


interface RequestArgs {
    headers?: any,
    data?: any,
    formData?: FormData,
    bytes?: BinaryType
}

export interface ServiceConfig {
    appId: string,
    baseUrl: string,
    clientKey: string,
    clientSecret: string
}

function trimStart(str:string, chars:string) {
    var start = 0,
        end = str.length;

    while(start < end && chars.indexOf(str[start]) >= 0)
        ++start;

    return (start > 0) ? str.substring(start, end) : str;
}

export class ServiceClient {
    config: ServiceConfig
    sessionToken?: string

    constructor(config: ServiceConfig) {
        this.config = config
    }

    setSessionToken(token: string) {
        this.sessionToken = token
    }

    isEmpty(target: any) {
        if (target === null || target === undefined) {
            return true;
        }
        return Object.keys(target).length === 0 && target.constructor === Object;
    }

    getSign(body: string): string {
        let timestamp = Math.floor(Date.now() / 1000);
        let message = this.config.appId + timestamp + body;
        let hash = CryptoJS.HmacSHA256(message, this.config.clientSecret);
        let sign = [CryptoJS.enc.Hex.stringify(hash), timestamp, this.config.clientKey].join(',');
        return sign
    }

    handleHttpError(status:number, body: any): never{
        let err: ErrorResponse = new ErrorResponse(
            status,
            {
                error_type: body.error_type,
                message: body.error_msg
            }
        )
        throw err
    }

    async request(url: string, method: string = "GET", data: RequestArgs): Promise<KyResponse> {
        let body = !this.isEmpty(data.data) ? JSON.stringify(data.data) : '';
        var sign = this.getSign(body)
        var headers: any = data.headers || {}
        let real_url = trimStart(url, '/')
        if (sign != undefined) {
            headers['X-HighOrder-Sign'] = sign
            headers['X-HighOrder-Application-Id'] = this.config.appId
        }
        if (this.sessionToken != undefined) {
            headers['X-HighOrder-Session-Token'] = this.sessionToken
        }
        var option: Options = {
            method: method,
            prefixUrl: this.config.baseUrl,
            mode: "cors",
            headers: headers as Headers,
            timeout: 3000,
            retry: 2,
            body: body,
            fetch: app_platform.custom_fetch,
            throwHttpErrors: false
        }
        let response = await ky(real_url, option)
        if(! response.ok){
            let body = await response.json()
            this.handleHttpError(response.status, body)
        }
        return response
    }

    async get(url: string, data?: RequestArgs): Promise<KyResponse> {
        return await this.request(url, "GET", data || {})
    }

    async post(url: string, data?: RequestArgs): Promise<KyResponse> {
        return await this.request(url, "POST", data || {})
    }

    async put(url: string, data?: RequestArgs): Promise<KyResponse> {
        return await this.request(url, "PUT", data || {})
    }

    async head(url: string, data?: RequestArgs): Promise<KyResponse> {
        return await this.request(url, "HEAD", data || {})
    }

    async delete(url: string, data?: RequestArgs): Promise<KyResponse> {
        return await this.request(url, "DELETE", data || {})
    }

    async options(url: string, data?: RequestArgs): Promise<KyResponse> {
        return await this.request(url, "OPTIONS", data || {})
    }

}


export interface UserDetail {
    user_id: string
    user_name: string
}

export interface SessionDetail {
    user_id: string
    session_type: string
    session_token: string
}

export interface HolaCommonCommand{
    type: string,
    name: string,
    args: object,
}

export interface StartNewSessionCommand {
    type: string,
    name: string,
    args: object
}

export interface ShowPageCommandArg {
    page: object,
}

export interface ShowPageCommand{
    type: string,
    name: string,
    args: ShowPageCommandArg
}

export interface SetSessionCommandArg {
    session: SessionDetail,
    user: UserDetail
}

export interface SetSessionCommand{
    type: string,
    name: string,
    args: SetSessionCommandArg
}

export interface UpdatePageCommandArg {
    changed_page: object,
}

export interface UpdatePageCommand{
    type: string,
    name: string,
    args: UpdatePageCommandArg
}

export interface ShowMotionCommandArg {
    name: string,
    args: object
}

export interface ShowMotionCommand{
    type: string,
    name: string,
    args: ShowMotionCommandArg
}

export interface ShowAlertCommandArg {
    text: string,
    title: string
}

export interface ShowAlertCommand{
    type: string,
    name: string,
    args: ShowAlertCommandArg
}

export interface InitAdCommandArg {
    configs: Array<Record<string, any>>
}

export interface InitAdCommand {
    type: string,
    name: string,
    args: InitAdCommandArg
}

export interface ShowAdCommandArg {
    ad_vendor: string,
    ad_type: string,
    ad_code?: string,
    ad_hint?: Array<string>
    ad_candidates?: Array<{ad_code: string}>
}

export interface ShowAdCommand {
    type: string,
    name: string,
    args: Record<string, any>
}

export interface PlayableApplyCommandArg {
    effect: string
}

export interface PlayableApplyCommand {
    type: string,
    name: string,
    args: PlayableApplyCommandArg
}

export interface ShowNarrationCommand{
    type: string,
    name: string,
    args: {
        narration: object
    }
}

export type HolaCommand = ShowPageCommand | ShowNarrationCommand
    | ShowAlertCommand | ShowMotionCommand | StartNewSessionCommand
    | HolaCommonCommand;

export interface PageContext{
    platform: string,
    route: string,
    version?: string
}

export type ErrorData = {
    error_type: string
    message: string
}


export class ErrorResponse {
    code: number
    error: ErrorData
    constructor(code: number, error:ErrorData){
        this.code = code;
        this.error = error;
        if(error.error_type === undefined){
            const code_num = Math.floor(code/100)
            if( code_num === 5){
                this.error.error_type = 'InternalServerError'
                this.error.message = 'server internal error.'
            } else if(code_num === 4){
                this.error.error_type = 'RequestInvalidError'
                this.error.message = 'request invalid.'
            } else {
                this.error.error_type = 'UnknownError'
                this.error.message = 'unknown what happened.'
            }
        }
    }
}


function isSomeError<T>(err: any): err is T {
    return err instanceof Error;
}


export class ServiceOperation {
    client: ServiceClient
    user: UserDetail
    session: SessionDetail
    app_id: string
    config: ServiceConfig

    constructor(config: ServiceConfig) {
        this.client = new ServiceClient(config)
        this.user = {user_id:'', user_name:''}
        this.session = {session_token:'', session_type:'unknown', user_id:''}
        this.app_id = config.appId
        this.config = config
    }

    async init(){
        const data_store = await AppDataStore.get_store(this.app_id)
        const user = await data_store.getUser()
        const session = await data_store.getSession()
        if(user){
            this.user = user
        }
        if(session){
            this.session = session
        }
        this.client.setSessionToken(this.session.session_token)

    }

    handleError(error: Error): never{
        console.log(error)
        if (error.name === 'TimeoutError') {
            let err: ErrorResponse = new ErrorResponse(
                -1,
                {
                    error_type: "ServerNoResponse",
                    message: "Reques sent, but no response received."
                }
            )
            throw err
        } else {
            throw error
        }
    }

    async getLocalUid(): Promise<string> {
        const data_store = await AppDataStore.get_store(this.app_id)
        let uid = await data_store.getLocalUid()
        if(uid === undefined){
            throw Error('no local_uid, data store not init correctly.')
        }
        return uid as string
    }

    async getContent(url:string){
        let real_url = url;
        if(!url.includes("://")){
            real_url = this.config.baseUrl + trimStart(url, '/')
        }
        var option: Options = {
            method: "GET",
            mode: "cors",
            timeout: 3000,
            retry: 2,
            fetch: app_platform.custom_fetch,
            throwHttpErrors: true
        }
        try {
            let response = await ky(real_url, option)
            return await response.text();
        }  catch (any_error) {
            const error = any_error as Error;
            throw error
        }

    }

    async anonymousLogin(context: PageContext) {
        const local_uid = await this.getLocalUid()
        console.log('anonymousLogin')

        let reqArg: RequestArgs = {
            "data": {
                "command":"login",
                "args": {
                    "anonymous": true,
                    "local_uid": local_uid
                },
                "context": context
            }
        }
        try {
            let resp = await this.client.post('/service/hola/main', reqArg);
            let body = (await resp.json()) as any;
            const commands = body.data.commands
            for(const command of commands){
                if(command.name == 'set_session'){
                    let _cmd = command as SetSessionCommand
                    await this.setSession(_cmd.args.user, _cmd.args.session)
                }
            }
        } catch (error) {
            this.handleError(error as Error)
        }

    }

    async setSession(user:UserDetail, session:SessionDetail): Promise<{user: UserDetail, session:SessionDetail}> {
        try {
            const data_store = await AppDataStore.get_store(this.app_id)
            await data_store.saveUser(user)
            await data_store.saveSession(session)
            this.user = user
            this.session = session
            this.client.setSessionToken(session.session_token)
            return { user: user, session: session }
        } catch (error) {
            this.handleError(error as Error)
        }

    }

    async checkAndCreateSession(context: PageContext){
        if (this.user === undefined || this.user.user_id === undefined
            || this.user.user_id.length === 0
            || this.session === undefined
            || this.session.session_token === undefined
            || this.session.session_token.length === 0){
            const data_store = await AppDataStore.get_store(this.app_id)
            await this.anonymousLogin(context)
        }
    }

    async deleteSession(){
        const data_store = await AppDataStore.get_store(this.app_id)
        await data_store.deleteSession()
        this.session.session_token = ""
        this.client.setSessionToken("")
    }

    async holaRequest(args: RequestArgs): Promise<HolaCommand[]> {
        try {
            await this.checkAndCreateSession(args.data.context)
            let resp = await this.client.post('/service/hola/main', args);
            let body = (await resp.json()) as any;
            const commands = body.data.commands
            return commands
        } catch (error) {
            this.handleError(error as Error)
        }

    }

    async holaSessionStart(context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {
                "command":"session_start",
                "context": context
            },

        }
        return await this.holaRequest(reqArg)

    }

    async holaAuthWeixin(args: {code: string}, context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {
                "command":"auth_weixin",
                "args":args,
                "context": context
            },
        }
        return await this.holaRequest(reqArg)
    }

    async holaCallAction(args: object, context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {"command":"call_action", "args":args, "context":context}
        }
        return await this.holaRequest(reqArg)
    }

    async holaNavigateTo(route: string, context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {"command":"navigate_to", "args":{"route": route}, "context":context}
        }
        return await this.holaRequest(reqArg)
    }


    async holaNarrationShowed(name: string, context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {"command":"narration_showed", "args":{"name": name}, "context":context}
        }
        return await this.holaRequest(reqArg)
    }

    async holaPlayableCompleted(played: PlayableResult, context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {"command":"playable_completed", "args":{...played}, "context":context}
        }
        return await this.holaRequest(reqArg)
    }

    async holaPlayableNext(level_id: string, context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {"command":"playable_next", "args":{level_id:level_id}, "context":context}
        }
        return await this.holaRequest(reqArg)
    }

    async holaPlayableRetry(level_id: string, context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {"command":"playable_retry", "args":{level_id:level_id}, "context":context}
        }
        return await this.holaRequest(reqArg)
    }

    async holaItemUse(item_name: string, context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {"command":"item_use", "args":{item_name:item_name}, "context":context}
        }
        return await this.holaRequest(reqArg)
    }

    async holaItemBuy(item_name: string, context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {"command":"item_buy", "args":{item_name:item_name}, "context":context}
        }
        return await this.holaRequest(reqArg)
    }

    async holaAdShowed(ad_args: object, context: PageContext): Promise<HolaCommand[]> {
        let reqArg: RequestArgs = {
            "data": {"command":"ad_showed", "args":{ad_args:ad_args}, "context":context}
        }
        return await this.holaRequest(reqArg)
    }
}