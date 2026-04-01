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

const highorder_app_config = {
  appId: options.app_id ?? import.meta.env.VITE_APP_ID ?? '',
  baseUrl: options.base_url ?? import.meta.env.VITE_BASE_URL ?? '',
  privacyUrl: options.privacy_url ?? `/static/APP_${options.app_id}/content/main/privacy.html`,
  assetsUrl: options.assets_url ?? '/assets',
  clientKey: options.client_key ?? import.meta.env.VITE_CLIENT_KEY ?? '',
  clientSecret: options.client_secret ?? import.meta.env.VITE_CLIENT_SECRET ?? ''
}

const init_options = {
  simulator: true
}

createHighOrderApp([highorder_app_config], init_options).then((app) => {
  app_platform.init_options = init_options
  app.mount('#app')
})
