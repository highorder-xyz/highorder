export const app_platform = {
  init_options: {},
  custom_fetch: undefined,
  register(platform) {
    this._platform = platform
  },
  getPlatform() {
    if (this._platform && typeof this._platform.getPlatform === 'function') {
      return this._platform.getPlatform()
    }
    return {
      name: 'web',
      vendor: 'unknown',
      os: 'unknown',
      os_version: 'unknown',
      language: typeof navigator !== 'undefined' ? navigator.language : 'en',
      screen_size: { width: -1, height: -1 },
      page_size: {
        width: typeof window !== 'undefined' ? window.innerWidth : -1,
        height: typeof window !== 'undefined' ? window.innerHeight : -1
      },
      is_virtual: false,
      web_version: 'unknown',
      timezone: { offset: new Date().getTimezoneOffset() * 60 }
    }
  },
  mustAgreePrivacy() {
    if (this._platform && typeof this._platform.mustAgreePrivacy === 'function') {
      return this._platform.mustAgreePrivacy()
    }
    return false
  },
  async initialize(init_options) {
    this.init_options = init_options || {}
    if (this._platform && typeof this._platform.initialize === 'function') {
      await this._platform.initialize(this.init_options)
    }
  },
  exitApp() {
    if (this._platform && typeof this._platform.exitApp === 'function') {
      return this._platform.exitApp()
    }
  },
  openUrl(url) {
    if (this._platform && typeof this._platform.openUrl === 'function') {
      return this._platform.openUrl(url)
    }
    if (typeof window !== 'undefined') {
      window.open(url, '_blank')
    }
  },
  getAdPluginInstance(vendor) {
    if (this._platform && typeof this._platform.getAdPluginInstance === 'function') {
      return this._platform.getAdPluginInstance(vendor)
    }
    return undefined
  },
  getWeChatPluginInstance() {
    if (this._platform && typeof this._platform.getWeChatPluginInstance === 'function') {
      return this._platform.getWeChatPluginInstance()
    }
    return undefined
  },
  async setUser(user_id, property) {
    if (this._platform && typeof this._platform.setUser === 'function') {
      await this._platform.setUser(user_id, property)
    }
  },
  async logEvent(name, params) {
    if (this._platform && typeof this._platform.logEvent === 'function') {
      await this._platform.logEvent(name, params)
      return
    }
    // keep behavior similar to legacy webapp host
    if (typeof console !== 'undefined') {
      console.log('AnalyticsEvent', name, params)
    }
  }
}
