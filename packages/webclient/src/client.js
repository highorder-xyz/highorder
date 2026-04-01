import CryptoJS from 'crypto-js'
import ky from 'ky'
import { app_platform } from './platform.js'

function trimStart(str, prefix) {
  let s = String(str)
  const p = String(prefix)
  while (s.startsWith(p)) s = s.slice(p.length)
  return s
}

function isDebugEnabled() {
  try {
    return typeof window !== 'undefined' && window.localStorage?.getItem('HIGHORDER_DEBUG') === '1'
  } catch {
    return false
  }
}

export class ErrorResponse extends Error {
  constructor(code, error) {
    super(error?.message || 'ErrorResponse')
    this.code = code
    this.error = error
    if (this.error && this.error.error_type === undefined) {
      const code_num = Math.floor(code / 100)
      if (code_num === 5) {
        this.error.error_type = 'InternalServerError'
        this.error.message = 'server internal error.'
      } else if (code_num === 4) {
        this.error.error_type = 'RequestInvalidError'
        this.error.message = 'request invalid.'
      } else {
        this.error.error_type = 'UnknownError'
        this.error.message = 'unknown what happened.'
      }
    }
  }
}

export class ServiceClient {
  constructor(config) {
    this.config = config
    this.sessionToken = undefined
  }

  setSessionToken(token) {
    this.sessionToken = token
  }

  isEmpty(target) {
    if (target === null || target === undefined) return true
    return Object.keys(target).length === 0 && target.constructor === Object
  }

  getSign(body) {
    const timestamp = Math.floor(Date.now() / 1000)
    const message = this.config.appId + timestamp + body
    const hash = CryptoJS.HmacSHA256(message, this.config.clientSecret)
    return [CryptoJS.enc.Hex.stringify(hash), timestamp, this.config.clientKey].join(',')
  }

  handleHttpError(status, body) {
    throw new ErrorResponse(status, {
      error_type: body?.error_type,
      message: body?.error_msg
    })
  }

  async request(url, method = 'GET', data = {}) {
    const body = !this.isEmpty(data.data) ? JSON.stringify(data.data) : ''
    const sign = this.getSign(body)
    const headers = data.headers || {}

    headers['X-HighOrder-Sign'] = sign
    headers['X-HighOrder-Application-Id'] = this.config.appId
    if (this.sessionToken !== undefined) {
      headers['X-HighOrder-Session-Token'] = this.sessionToken
    }

    const option = {
      method,
      prefixUrl: this.config.baseUrl,
      mode: 'cors',
      headers,
      timeout: 3000,
      retry: 2,
      body,
      fetch: app_platform.custom_fetch,
      throwHttpErrors: false
    }

    const resp = await ky(url, option)
    if (!resp.ok) {
      const json = await resp.json().catch(() => ({}))
      this.handleHttpError(resp.status, json)
    }
    return resp
  }

  async post(url, data) {
    return await this.request(url, 'POST', data)
  }
}

export class ServiceOperation {
  constructor(config, dataStore) {
    this.client = new ServiceClient(config)
    this.user = { user_id: '', user_name: '' }
    this.session = { session_token: '', session_type: 'unknown', user_id: '' }
    this.app_id = config.appId
    this.config = config
    this.dataStore = dataStore
  }

  async init() {
    if (!this.dataStore) return
    const user = await this.dataStore.getUser(this.app_id)
    const session = await this.dataStore.getSession(this.app_id)
    if (user) this.user = user
    if (session) this.session = session
    this.client.setSessionToken(this.session.session_token)
  }

  async setSession(user, session) {
    if (this.dataStore) {
      await this.dataStore.saveUser(this.app_id, user)
      await this.dataStore.saveSession(this.app_id, session)
    }
    this.user = user
    this.session = session
    this.client.setSessionToken(session.session_token)
    return { user, session }
  }

  async clearSession() {
    if (this.dataStore) {
      await this.dataStore.deleteUser(this.app_id)
      await this.dataStore.deleteSession(this.app_id)
    }
    this.user = { user_id: '', user_name: '' }
    this.session = { session_token: '', session_type: 'unknown', user_id: '' }
  }

  async deleteSession() {
    if (this.dataStore) {
      await this.dataStore.deleteSession(this.app_id)
    }
    this.session.session_token = ''
    this.client.setSessionToken('')
  }

  async holaRequest(args) {
    const debug = isDebugEnabled()
    if (debug) {
      console.debug('[webclient] holaRequest', args)
    }
    const resp = await this.client.post('/service/hola/main', args)
    const body = await resp.json()
    if (debug) {
      console.debug('[webclient] holaResponse', body)
    }
    return body?.data?.commands || []
  }

  async holaSessionStart(context) {
    return await this.holaRequest({
      data: {
        command: 'session_start',
        context
      }
    })
  }

  async holaCallAction(args, context) {
    return await this.holaRequest({
      data: { command: 'call_action', args, context }
    })
  }

  async holaPageInteract(name, event, handler, locals, context) {
    return await this.holaRequest({
      data: {
        command: 'page_interact',
        args: { name, event, handler, locals },
        context
      }
    })
  }

  async holaDialogInteract(dialog_id, name, event, handler, locals, context) {
    return await this.holaRequest({
      data: {
        command: 'dialog_interact',
        args: { dialog_id, name, event, handler, locals },
        context
      }
    })
  }

  async holaNavigateTo(route, context) {
    return await this.holaRequest({
      data: { command: 'route_to', args: { route }, context }
    })
  }

  async getContent(url) {
    let real_url = url
    if (!String(url).includes('://')) {
      real_url = this.config.baseUrl + trimStart(url, '/')
    }
    const option = {
      method: 'GET',
      mode: 'cors',
      timeout: 3000,
      retry: 2,
      fetch: app_platform.custom_fetch,
      throwHttpErrors: true
    }
    const resp = await ky(real_url, option)
    return await resp.text()
  }
}
