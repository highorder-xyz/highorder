import i18next from 'i18next'

export async function initI18n({ language, resources }) {
  await i18next.init({
    lng: language,
    debug: false,
    resources
  })
}

export { i18next }
