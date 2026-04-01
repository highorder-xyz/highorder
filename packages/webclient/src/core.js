import { app_platform } from './platform.js'
import { DataStore } from './datastore.js'
import { ServiceOperation } from './client.js'

const APP_VERSION = '0.1.0'

export const AnalyticsEventKind = {
  page_show: 'PageShow',
  ad_show_event: 'AdShowEvent',
  playable_event: 'PlayableEvent',
  played_event: 'PlayedEvent',
  item_event: 'ItemEvent',
  button_event: 'ButtonEvent'
}

export class Page {
  static instances = {}

  static getPage(app_id) {
    if (this.instances[app_id]) return this.instances[app_id]
    const page = new Page(app_id)
    this.instances[app_id] = page
    return page
  }

  constructor(app_id) {
    this.app_id = app_id
    this.name = 'app'
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

export const appGlobal = { app_id: '' }

export class AppCore {
  static instances = {}
  static app_configs = {}

  static addAppConfig(config) {
    this.app_configs[config.appId] = config
  }

  static async init() {
    // datastore uses lazy open
  }

  static async switchTo(app_id) {
    if (!this.instances[app_id]) {
      const config = this.app_configs[app_id]
      const core = new AppCore(config)
      await core.load()
      this.instances[app_id] = core
    }
    appGlobal.app_id = app_id
  }

  static getCore(app_id) {
    return this.instances[app_id]
  }

  constructor(config) {
    this.config = { ...config }
    let baseUrl = (config.baseUrl || '').trim()
    if (baseUrl.endsWith('/')) baseUrl = baseUrl.slice(0, -1)
    this.config.baseUrl = baseUrl

    this.app_id = config.appId
    this.svc = new ServiceOperation(this.config, {
      getUser: async (app_id) => await (await import('./datastore.js')).AppDataStore.getUser(app_id),
      getSession: async (app_id) => await (await import('./datastore.js')).AppDataStore.getSession(app_id),
      saveUser: async (app_id, user) => await (await import('./datastore.js')).AppDataStore.saveUser(app_id, user),
      saveSession: async (app_id, session) => await (await import('./datastore.js')).AppDataStore.saveSession(app_id, session),
      deleteUser: async (app_id) => await (await import('./datastore.js')).AppDataStore.deleteUser(app_id),
      deleteSession: async (app_id) => await (await import('./datastore.js')).AppDataStore.deleteSession(app_id)
    })
    this.app_page = Page.getPage(this.app_id)
    this.platform = app_platform.getPlatform()
    this.privacy_agreed = false
    this.session_started = false
    this.error_recovering = false
    this.errors = []
    this.max_recover_retries = 6
    this.version = APP_VERSION
  }

  getPageContext() {
    const p = { ...app_platform.getPlatform() }
    const platform = p.name
    delete p.name
    return {
      platform,
      route: this.app_page.route,
      version: this.version,
      ...p
    }
  }

  async load() {
    await this.svc.init()
    this.privacy_agreed = await this.getPrivacyAgreed()
    await this.setPlatformUser()
  }

  async getContent(url) {
    return await this.svc.getContent(url)
  }

  full_link(url) {
    if (!url) return ''
    if (!String(url).includes('/')) return url
    if (String(url).includes('://')) return url
    return `${this.config.baseUrl}${url}`
  }

  async setPlatformUser() {
    if (this.svc.user && this.svc.user.user_id) {
      await app_platform.setUser(this.svc.user.user_id, {})
    }
  }

  async getPrivacyAgreed() {
    let value = await DataStore.get('privacy_agreed')
    if (value === 1) return true
    value = await DataStore.get_app_kv([this.app_id, 'privacy_agreed'])
    return value === 1
  }

  async savePrivacyAgreed() {
    this.privacy_agreed = true
    await DataStore.save({ key: 'privacy_agreed', value: 1 })
    await DataStore.save_app_kv({ app_id: this.app_id, key: 'privacy_agreed', value: 1 })
    await app_platform.initialize(app_platform.init_options)
  }

  async sessionStart() {
    try {
      const commands = await this.svc.holaSessionStart(this.getPageContext())
      this.session_started = true
      await this.setPlatformUser()
      return await this.handleCommandList(commands)
    } catch (err) {
      return await this.handleError(err)
    }
  }

  async callAction(args) {
    try {
      const commands = await this.svc.holaCallAction(args, this.getPageContext())
      return await this.handleCommandList(commands)
    } catch (err) {
      return await this.handleError(err)
    }
  }

  async pageInteract(name, event, handler, locals) {
    try {
      const commands = await this.svc.holaPageInteract(name, event, handler, locals, this.getPageContext())
      return await this.handleCommandList(commands)
    } catch (err) {
      return await this.handleError(err)
    }
  }

  async dialogInteract(dialog_id, name, event, handler, locals) {
    try {
      const commands = await this.svc.holaDialogInteract(dialog_id, name, event, handler, locals, this.getPageContext())
      return await this.handleCommandList(commands)
    } catch (err) {
      return await this.handleError(err)
    }
  }

  async navigateTo(route) {
    try {
      const commands = await this.svc.holaNavigateTo(route, this.getPageContext())
      return await this.handleCommandList(commands)
    } catch (err) {
      return await this.handleError(err)
    }
  }

  async handleErrorResponse(err) {
    const commands = []
    const error_type = err?.error?.error_type
    const code_category = Math.floor((err?.code || 0) / 100)
    if (error_type === 'SessionInvalid' || error_type === 'AuthorizeRequired') {
      await this.svc.deleteSession()
      commands.push({ type: 'command', name: 'start_new_session', args: {} })
    } else if (error_type === 'ServerNoResponse') {
      commands.push({
        type: 'command',
        name: 'show_modal',
        args: {
          type: 'modal',
          title: 'SERVER NO RESPONSE',
          content: 'Please check network and retry.',
          confirm: { text: 'OK', action: 'route.navigate_to', args: { route: '/' } }
        }
      })
    } else if (error_type === 'InternalServerError' || code_category === 5) {
      commands.push({
        type: 'command',
        name: 'show_modal',
        args: {
          type: 'modal',
          title: 'SERVER ERROR',
          content: 'Server error. Please retry.',
          confirm: { text: 'Retry', action: 'route.navigate_to', args: { route: '/' } }
        }
      })
    } else if (error_type === 'RequestInvalidError' || code_category === 4) {
      commands.push({
        type: 'command',
        name: 'show_modal',
        args: {
          type: 'modal',
          title: 'REQUEST INVALID',
          content: 'Client request invalid. Please update client.',
          confirm: { text: 'OK', action: 'route.navigate_to', args: { route: '/' } }
        }
      })
    } else {
      commands.push({
        type: 'command',
        name: 'show_modal',
        args: {
          type: 'modal',
          title: 'RECOVERING',
          content: 'Problem recovering. Please retry later.',
          confirm: { text: 'OK', action: 'route.navigate_to', args: { route: '/' } }
        }
      })
    }
    return commands
  }

  async handleError(err) {
    if (this.error_recovering === false) {
      this.error_recovering = true
      this.errors = []
    }
    if (this.errors.length > this.max_recover_retries) {
      return []
    }
    this.errors.push(err)
    if (err && err.code !== undefined && err.error) {
      return await this.handleErrorResponse(err)
    }
    throw err
  }

  reset_recover_state() {
    this.error_recovering = false
    this.errors = []
  }

  async handleCommandList(commands) {
    this.reset_recover_state()
    const ret = []
    for (const command of commands) {
      const cmd = await this.handleCommand(command)
      if (cmd) ret.push(cmd)
    }
    return ret
  }

  async handleCommand(command) {
    if (command.name === 'show_page') {
      const page = command.args.page
      this.app_page.reset()
      this.app_page.name = page.name
      this.app_page.route = page.route
      this.app_page.locals = page.locals || {}
      this.app_page.elements = page.elements || []
      this.app_page.version = this.app_page.version + 1
      app_platform.logEvent(AnalyticsEventKind.page_show, { route: page.route })
      return undefined
    }
    if (command.name === 'update_page') {
      const changed_page = command.args.changed_page
      if (this.app_page.route === changed_page.route) {
        for (const [idx, element] of Object.entries(changed_page.changed_elements || {})) {
          const k = parseInt(idx)
          if (!Number.isNaN(k) && k < this.app_page.elements.length) {
            this.app_page.elements[k] = element
          }
        }
      }
      return undefined
    }
    if (command.name === 'set_session') {
      await this.svc.setSession(command.args.user, command.args.session)
      await this.navigateTo(this.app_page.route)
      return undefined
    }
    if (command.name === 'clear_session') {
      await this.svc.clearSession()
      await this.navigateTo(this.app_page.route)
      return undefined
    }
    return command
  }
}
