export function createToastBus() {
  const listeners = new Set()
  return {
    subscribe(cb) {
      listeners.add(cb)
      return () => listeners.delete(cb)
    },
    emit(msg) {
      for (const cb of listeners) cb(msg)
    }
  }
}
