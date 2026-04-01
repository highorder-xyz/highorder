import React, { useEffect, useMemo, useRef, useState } from 'react'
import { createToastBus } from '../ui/toast_bus.js'
import { AppCore, AnalyticsEventKind, Page } from '../core.js'
import { toastBus } from '../ui/toast_bus.js'
import { ElementsRenderer } from '../renderer/elements.jsx'
import { renderDecoration } from '../ui/decoration_registry.js'
import { getInterfaceModal } from '../ui/interface_registry.js'

export function HighOrderApp({ init_options = {}, modal_helper }) {
  const [tick, setTick] = useState(0)
  const [bootState, setBootState] = useState({ status: 'booting' })
  const toastBus = useMemo(() => createToastBus(), [])
  const appIdRef = useRef(() => appGlobal.app_id)

  // subscribe to page updates by polling version changes (minimal; can be improved later)
  useEffect(() => {
    const timer = setInterval(() => setTick((v) => v + 1), 200)
    return () => clearInterval(timer)
  }, [])

  const app_id = appIdRef.current()
  const page = app_id ? Page.getPage(app_id) : undefined

  const pageVersion = page?.version ?? -1

  const context = useMemo(
    () => ({ app_id, route: page?.route || '/', modal_id: undefined, locals: page?.locals || {} }),
    [page?.route, pageVersion]
  )

  const actions = useMemo(
    () => ({
      toastBus,
      renderDecoration,
      modal_new_id: () => modal_helper.new_modal_id(),
      openModal: (modal_id, option, slot_render, ctx, inplace = false) => {
        const id = modal_id || modal_helper.new_modal_id()
        if (ctx?.modal_id && typeof modal_helper.open_sub === 'function') {
          return modal_helper.open_sub(
            {
              modal_id: id,
              option,
              slot_render,
              close_listeners: []
            },
            ctx,
            inplace
          )
        }
        return modal_helper.open(id, option, slot_render)
      },
      handleCommands: async (commands, ctx) => {
        await handleImmediateCommands(commands, ctx)
      },
      navigateTo: async (route, ctx) => {
        const core = AppCore.getCore(app_id)
        if (!core) return
        const commands = await core.navigateTo(route)
        await handleImmediateCommands(commands, ctx)
      },
      interact: async (name, event, handler, value, ctx) => {
        const core = AppCore.getCore(app_id)
        if (!core) return
        const locals = { ...(ctx?.locals || {}), value }
        const commands = ctx?.modal_id
          ? await core.dialogInteract(ctx.modal_id, name, event, handler, locals)
          : await core.pageInteract(name, event, handler, locals)
        await handleImmediateCommands(commands, ctx)
      },
      runDslNode: async (node, ctx) => {
        const core = AppCore.getCore(app_id)
        if (!core) return
        if (!node || typeof node !== 'object') return
        const locals = { ...(ctx?.locals || {}) }
        const commands = ctx?.modal_id
          ? await core.dialogInteract(ctx.modal_id, '', 'click', node, locals)
          : await core.pageInteract('', 'click', node, locals)
        await handleImmediateCommands(commands, ctx)
      },
      onButtonClick: async (buttonElement, ctx) => {
        const core = AppCore.getCore(app_id)
        if (!core) return

        // legacy-compatible fields
        if (buttonElement.href) {
          window.open(buttonElement.href, buttonElement.open_new ? '_blank' : '_self')
          return
        }

        if (buttonElement.open_modal) {
          // server-driven open_modal is usually a ModalElement; we handle it as a show_modal command
          await core.handleCommand({ type: 'command', name: 'show_modal', args: buttonElement.open_modal })
          return
        }

        if (buttonElement.action) {
          const commands = await core.callAction({ action: buttonElement.action, args: buttonElement.args || {} })
          await handleImmediateCommands(commands, ctx)
          return
        }

        if (buttonElement.handlers) {
          // page_interact style (name/event/handler). We only support one handler for now.
          const handler = buttonElement.handlers.clicked || buttonElement.handlers.click
          if (handler) {
            const commands = await core.pageInteract(buttonElement.name || buttonElement.text, 'click', handler, page?.locals || {})
            await handleImmediateCommands(commands, ctx)
          }
        }

        // analytics
        core.platform?.logEvent?.(AnalyticsEventKind.button_event, {
          route: page?.route,
          text: buttonElement.text
        })
      }
      ,
      openInterfaceModal: async (name, argsNode, ctx) => {
        const modalDef = getInterfaceModal(app_id, name)
        if (!modalDef) {
          const modal_id = modal_helper.new_modal_id()
          const option = {
            title: `Modal not found: ${String(name)}`,
            content_html: `<pre style="white-space:pre-wrap;">${JSON.stringify({ name, args: argsNode }, null, 2)}</pre>`,
            actionConfirmText: 'OK'
          }
          actions.openModal?.(modal_id, option, () => null, ctx)
          return
        }

        const it = ctx?.locals?.it

        const evalNode = (node) => {
          if (node == null) return undefined
          if (typeof node !== 'object') return node
          const t = String(node.type || '')
          if (t === 'expr') {
            const expr = String(node.expr || '').trim()
            if (expr === 'it') return it
            if (expr.startsWith('it.')) {
              const parts = expr.slice(3).split('.')
              let cur = it
              for (const p of parts) {
                if (cur == null) return undefined
                cur = cur[p]
              }
              return cur
            }
            return undefined
          }
          if (t === 'format') {
            const fmt = String(node.format || '')
            return fmt.replace(/\{([^}]+)\}/g, (_, key) => {
              const k = String(key || '').trim()
              if (k === 'it') return it == null ? '' : String(it)
              if (k.startsWith('it.')) {
                const parts = k.slice(3).split('.')
                let cur = it
                for (const p of parts) {
                  if (cur == null) return ''
                  cur = cur[p]
                }
                return cur == null ? '' : String(cur)
              }
              return ''
            })
          }
          return node
        }

        const evalArgs = (args) => {
          if (args == null) return undefined
          if (typeof args !== 'object') return args
          if (args.type) {
            return evalNode(args)
          }
          const out = {}
          for (const [k, v] of Object.entries(args)) {
            out[k] = evalNode(v)
          }
          return out
        }

        const evaluated = evalArgs(argsNode)
        const modal = { ...modalDef }
        const modal_id = modal_helper.new_modal_id()
        const dlg_context = { ...ctx, modal_id, locals: { ...(modal.locals || {}), ...(evaluated || {}), ...(ctx?.locals || {}) } }

        const option = {
          title: modal.title,
          text: modal.content,
          content_html: modal.content_html,
          actionConfirmText: modal.confirm?.text,
          actionCancelText: modal.cancel?.text,
          onModalConfirmed: async () => {
            if (modal.confirm?.action) {
              const core = AppCore.getCore(app_id)
              const cmds = await core.callAction({ action: modal.confirm.action, args: modal.confirm.args || {} })
              await handleImmediateCommands(cmds, ctx)
            }
          },
          onModalCancelled: async () => {
            if (modal.cancel?.action) {
              const core = AppCore.getCore(app_id)
              const cmds = await core.callAction({ action: modal.cancel.action, args: modal.cancel.args || {} })
              await handleImmediateCommands(cmds, ctx)
            }
          }
        }

        const slot_render = () => {
          if (modal.elements && Array.isArray(modal.elements) && modal.elements.length > 0) {
            return <ElementsRenderer elements={modal.elements} context={dlg_context} actions={actions} />
          }
          return null
        }

        actions.openModal?.(modal_id, option, slot_render, ctx)
      }
    }),
    [app_id, page, toastBus]
  )

  async function handleImmediateCommands(commands, ctx) {
    for (const command of commands || []) {
      if (command.name === 'start_new_session') {
        const core = AppCore.getCore(app_id)
        const cmds = await core.sessionStart()
        await handleImmediateCommands(cmds, ctx)
      } else if (command.name === 'show_alert') {
        const args = command.args
        let severity = 'info'
        for (const tag of args.tags || []) {
          if (['info', 'success', 'warn', 'error'].includes(tag)) severity = tag
        }
        toastBus.emit({ severity, title: args.title, text: args.text, duration: args.duration })
      } else if (command.name === 'show_modal') {
        const modal = command.args
        const modal_id = modal_helper.new_modal_id()
        const dlg_context = { ...ctx, modal_id, locals: { ...(modal.locals || {}), ...(ctx?.locals || {}) } }
        const option = {
          title: modal.title,
          text: modal.content,
          content_html: modal.content_html,
          actionConfirmText: modal.confirm?.text,
          actionCancelText: modal.cancel?.text,
          onModalConfirmed: async () => {
            if (modal.confirm?.action) {
              const core = AppCore.getCore(app_id)
              const cmds = await core.callAction({ action: modal.confirm.action, args: modal.confirm.args || {} })
              await handleImmediateCommands(cmds, ctx)
            }
            modal_helper.popup(modal_id)
          },
          onModalCancelled: async () => {
            if (modal.cancel?.action) {
              const core = AppCore.getCore(app_id)
              const cmds = await core.callAction({ action: modal.cancel.action, args: modal.cancel.args || {} })
              await handleImmediateCommands(cmds, ctx)
            }
            modal_helper.popup(modal_id)
          }
        }
        const slot_render = () => {
          if (modal.elements && Array.isArray(modal.elements) && modal.elements.length > 0) {
            return <ElementsRenderer elements={modal.elements} context={dlg_context} actions={actions} />
          }
          return null
        }
        actions.openModal(modal_id, option, slot_render, ctx)
      } else {
        // allow core to process show_page/update_page/set_session/clear_session
        const core = AppCore.getCore(app_id)
        if (core) await core.handleCommand(command)
      }
    }
  }

  useEffect(() => {
    // on mount: session start
    ;(async () => {
      if (!app_id) {
        setBootState({ status: 'missing_app_id' })
        return
      }
      const core = AppCore.getCore(app_id)
      if (!core) {
        setBootState({ status: 'missing_core', app_id })
        return
      }
      setBootState({ status: 'starting_session', app_id })
      try {
        const commands = await core.sessionStart()
        await handleImmediateCommands(commands, context)
        setBootState({ status: 'running', app_id })
      } catch (err) {
        console.error('sessionStart failed', err)
        toastBus.emit({ severity: 'error', title: 'Error', text: String(err?.message || err) })
        setBootState({ status: 'error', app_id, error: String(err?.message || err) })
      }
    })()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [app_id])

  return (
    <div>
      <ToastHost bus={toastBus} />
      <ModalHost modal_helper={modal_helper} />
      <div style={{ padding: 16 }}>
        <div style={{ fontSize: 12, opacity: 0.6, marginBottom: 12 }}>
          <div>boot: {bootState.status}</div>
          <div>app_id: {app_id || '(empty)'}</div>
          <div>route: {page?.route || '(none)'}</div>
          <div>page.version: {pageVersion}</div>
          <div>elements: {(page?.elements || []).length}</div>
        </div>
        {(page?.elements || []).length === 0 ? (
          <div style={{ opacity: 0.8 }}>Waiting for server page...</div>
        ) : null}
        <ElementsRenderer elements={page?.elements || []} context={context} actions={actions} />
      </div>
      <div style={{ display: 'none' }}>{tick}</div>
    </div>
  )
}
