import { create } from 'zustand'

function randomString(length) {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let out = ''
  for (let i = 0; i < length; i += 1) {
    out += chars[Math.floor(Math.random() * chars.length)]
  }
  return out
}

export function createModalHelper() {
  const useStore = create((set, get) => ({
    current: undefined,
    stack: [],
    open(modal_id, option, slot_render) {
      const state = get()
      if (state.current) {
        // When a modal is already open, behave like legacy: open a new one on top.
        const next_stack = [...(state.stack || []), state.current]
        set({ stack: next_stack })
      }
      const param = {
        modal_id,
        option: { ...option },
        slot_render,
        close_listeners: []
      }
      param.option.onModalClosed = () => get().close()
      set({ current: param })
      return { update: (next) => get().update(modal_id, next) }
    },

    open_sub(param, context, inplace = false) {
      const state = get()
      if (!state.current) {
        // no active modal: fallback to normal open
        return get().open(param.modal_id, param.option, param.slot_render)
      }

      if (inplace) {
        // Replace current modal in place (keep same stack)
        const next = {
          ...param,
          option: { ...param.option },
          close_listeners: param.close_listeners || []
        }
        next.option.onModalClosed = () => get().close()
        set({ current: next })
        return { update: (nextOpt) => get().update(param.modal_id, nextOpt) }
      }

      // Push current and open as stacked modal.
      const next_stack = [...(state.stack || []), state.current]
      const next = {
        ...param,
        option: { ...param.option },
        close_listeners: param.close_listeners || []
      }
      next.option.onModalClosed = () => get().close()
      set({ current: next, stack: next_stack })
      return { update: (nextOpt) => get().update(param.modal_id, nextOpt) }
    },

    open_any(option, slot_render) {
      const modal_id = get().new_modal_id()
      return get().open(modal_id, option, slot_render)
    },
    update(modal_id, option) {
      const state = get()
      if (state.current && state.current.modal_id === modal_id) {
        set({ current: { ...state.current, option: { ...state.current.option, ...option } } })
      }
    },
    popup(modal_id) {
      const state = get()
      if (!modal_id) return

      // Close top if matches.
      if (state.current && state.current.modal_id === modal_id) {
        get().close()
        return
      }

      // If the modal is in stack, remove it.
      const stack = state.stack || []
      const idx = stack.findIndex((m) => m && m.modal_id === modal_id)
      if (idx >= 0) {
        const next_stack = [...stack]
        const removed = next_stack.splice(idx, 1)[0]
        set({ stack: next_stack })
        if (removed) {
          for (const listener of removed.close_listeners || []) {
            listener(removed)
          }
        }
      }
    },
    close() {
      const state = get()
      const root = state.current
      if (state.stack && state.stack.length > 0) {
        const next_stack = [...state.stack]
        const prev = next_stack.pop()
        set({ current: prev, stack: next_stack })
      } else {
        set({ current: undefined, stack: [] })
      }
      if (root) {
        for (const listener of root.close_listeners) {
          listener(root)
        }
      }
    },
    reset() {
      set({ current: undefined, stack: [] })
    },
    new_modal_id() {
      return randomString(10)
    }
  }))

  return {
    new_modal_id: () => useStore.getState().new_modal_id(),
    open_any: (option, slot_render) => useStore.getState().open_any(option, slot_render),
    open: (modal_id, option, slot_render) => useStore.getState().open(modal_id, option, slot_render),
    open_sub: (param, context, inplace) => useStore.getState().open_sub(param, context, inplace),
    open_wait: async (modal_id, option, context, slot_render) => {
      // minimal compatibility: open and resolve on close
      return await new Promise((resolve) => {
        const state = useStore.getState()
        const inplace = !!context?.inplace

        let updater
        if (context?.modal_id && typeof state.open_sub === 'function') {
          updater = state.open_sub(
            {
              modal_id,
              option,
              slot_render,
              close_listeners: []
            },
            context,
            inplace
          )
        } else {
          updater = state.open(modal_id, option, slot_render)
        }

        const current = useStore.getState().current
        if (current && current.modal_id === modal_id) {
          current.close_listeners.push(() => resolve())
        } else {
          // Fallback: resolve on any close (should be rare)
          if (current) current.close_listeners.push(() => resolve())
        }

        return updater
      })
    },
    update: (modal_id, option) => useStore.getState().update(modal_id, option),
    popup: async (modal_id) => useStore.getState().popup(modal_id),
    close: () => useStore.getState().close(),
    reset: () => useStore.getState().reset(),
    __useStore: useStore
  }
}
