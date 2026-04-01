import './style.css'

import resources from './locales.json'
import { initI18n } from './i18n.js'
import { AppCore } from './core.js'
import { app_platform } from './platform.js'
import { createModalHelper } from './ui/modal_helper.js'
import { HighOrderApp } from './app/HighOrderApp.jsx'
import { registerDecoration, getDecoration } from './ui/decoration_registry.js'
import { registerInterfaces } from './ui/interface_registry.js'

export { app_platform }
export { HighOrderApp }
export { HButton } from './lib/HButton.jsx'
export { registerDecoration, getDecoration }

export const helpers = {
  modal_helper: createModalHelper()
}

export const modal_helper = helpers.modal_helper

export async function bootup(app_configs, init_options) {
  for (const config of app_configs) {
    AppCore.addAppConfig(config)
    if (config?.interfaces) {
      registerInterfaces(config.appId, config.interfaces)
    }
  }

  const platform_info = app_platform.getPlatform()
  const language = init_options.language || platform_info.language || 'en'

  await initI18n({ language, resources })
  await AppCore.init()

  const app_id = app_configs[0].appId
  await AppCore.switchTo(app_id)

  const app_core = AppCore.getCore(app_id)
  if (app_platform.mustAgreePrivacy() && !app_core.privacy_agreed) {
    app_platform.init_options = init_options
  } else {
    await app_platform.initialize(init_options)
  }
}

export async function createHighOrderApp(app_configs, init_options = {}) {
  await bootup(app_configs, init_options)

  return {
    mount(target) {
      const el =
        typeof target === 'string'
          ? document.querySelector(target)
          : target

      if (!el) {
        throw new Error(`mount target not found: ${String(target)}`)
      }

      // Lazy import to avoid hard dependency during library init
      Promise.all([import('react'), import('react-dom/client')]).then(
        ([React, ReactDomClient]) => {
          const root = ReactDomClient.createRoot(el)
          root.render(
            React.createElement(React.StrictMode, null,
              React.createElement(
                'div',
                { className: 'hc-root' },
                React.createElement(HighOrderApp, {
                  init_options,
                  modal_helper
                })
              )
            )
          )
        }
      )
    }
  }
}
