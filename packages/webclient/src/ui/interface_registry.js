const registry = {
  byApp: {}
}

export function registerInterfaces(app_id, interfaces) {
  if (!app_id) return
  if (!Array.isArray(interfaces)) return
  if (!registry.byApp[app_id]) {
    registry.byApp[app_id] = { modals: {}, pages: {}, raw: [] }
  }
  const store = registry.byApp[app_id]
  store.raw = interfaces
  for (const it of interfaces) {
    if (!it || typeof it !== 'object') continue
    const type = String(it.type || '').toLowerCase()
    if (type === 'modal' && it.name) {
      store.modals[String(it.name)] = it
    } else if (type === 'page' && it.route) {
      store.pages[String(it.route)] = it
    }
  }
}

export function getInterfaceModal(app_id, name) {
  if (!app_id || !name) return undefined
  return registry.byApp?.[app_id]?.modals?.[String(name)]
}

export function getInterfacePage(app_id, route) {
  if (!app_id || !route) return undefined
  return registry.byApp?.[app_id]?.pages?.[String(route)]
}
