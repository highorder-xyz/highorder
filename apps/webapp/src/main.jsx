import { createHighOrderApp, app_platform } from '@highorder/webclient'

function getSearchParameters() {
  const paramstr = window.location.search.slice(1)
  return paramstr != null && paramstr !== '' ? transformToObject(paramstr) : {}
}

function transformToObject(paramstr) {
  const params = {}
  const prmarr = paramstr.split('&')
  for (let i = 0; i < prmarr.length; i += 1) {
    const tmparr = prmarr[i].split('=')
    params[tmparr[0].trim()] = decodeURIComponent(tmparr[1] || '').trim()
  }
  return params
}

const options = getSearchParameters()

function loadLastConfig() {
  try {
    const raw = window.localStorage.getItem('HIGHORDER_LAST_CONFIG')
    return raw ? JSON.parse(raw) : undefined
  } catch {
    return undefined
  }
}

function saveLastConfig(config) {
  try {
    window.localStorage.setItem('HIGHORDER_LAST_CONFIG', JSON.stringify(config))
  } catch {
    // ignore
  }
}

const highorder_app_config = {
  appId: options.app_id ?? import.meta.env.VITE_APP_ID ?? '',
  baseUrl: options.base_url ?? import.meta.env.VITE_BASE_URL ?? '',
  privacyUrl: options.privacy_url ?? `/static/APP_${options.app_id}/content/main/privacy.html`,
  assetsUrl: options.assets_url ?? '/assets',
  clientKey: options.client_key ?? import.meta.env.VITE_CLIENT_KEY ?? '',
  clientSecret: options.client_secret ?? import.meta.env.VITE_CLIENT_SECRET ?? ''
}

if (!highorder_app_config.appId) {
  const last = loadLastConfig()
  if (last && last.appId) {
    highorder_app_config.appId = last.appId
    highorder_app_config.baseUrl = highorder_app_config.baseUrl || last.baseUrl || ''
    highorder_app_config.privacyUrl = highorder_app_config.privacyUrl || last.privacyUrl
    highorder_app_config.assetsUrl = highorder_app_config.assetsUrl || last.assetsUrl || '/assets'
    highorder_app_config.clientKey = highorder_app_config.clientKey || last.clientKey || ''
    highorder_app_config.clientSecret = highorder_app_config.clientSecret || last.clientSecret || ''
  }
}

const init_options = {}
if (options.theme !== undefined) {
  init_options.theme = options.theme
}

if (import.meta.env.PROD) {
  console.log = function () {}
}

createHighOrderApp([highorder_app_config], init_options).then((app) => {
  app_platform.init_options = init_options
  if (highorder_app_config.appId) {
    saveLastConfig(highorder_app_config)
  }
  app.mount('#app')
})
