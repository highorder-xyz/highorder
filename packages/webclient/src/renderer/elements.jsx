import React from 'react'
import { Button } from 'primereact/button'
import { InputText } from 'primereact/inputtext'
import { Dropdown } from 'primereact/dropdown'
import { Calendar } from 'primereact/calendar'
import { Checkbox } from 'primereact/checkbox'
import { InputSwitch } from 'primereact/inputswitch'
import { MultiSelect } from 'primereact/multiselect'
import { InputTextarea } from 'primereact/inputtextarea'
import { Tag } from 'primereact/tag'
import { Avatar } from 'primereact/avatar'
import { ProgressBar } from 'primereact/progressbar'
import { DataTable } from 'primereact/datatable'
import { Column } from 'primereact/column'
import { Rating } from 'primereact/rating'
import { Toolbar } from 'primereact/toolbar'
import { Card } from 'primereact/card'
import { Menu as PrimeMenu } from 'primereact/menu'
import { RichText } from '../lib/RichText.jsx'
import { app_platform } from '../platform.js'
import { AppCore, AnalyticsEventKind } from '../core.js'
import { deepSet } from '../common/utils.js'
import QRCode from 'qrcode'

function stripColLocals(locals) {
  const out = {}
  if (!locals || typeof locals !== 'object') return out
  for (const [k, v] of Object.entries(locals)) {
    if (!String(k).startsWith('__col_')) out[k] = v
  }
  return out
}

function styleFrom(element) {
  return element?.style || undefined
}

function toBool(v) {
  if (typeof v === 'boolean') return v
  if (typeof v === 'number') return v !== 0
  if (typeof v === 'string') return v === 'true' || v === '1'
  return !!v
}

function getSizeName(size) {
  if (size == null) return undefined
  const n = Number(size)
  if (Number.isNaN(n)) return undefined
  if (n <= 0) return undefined
  if (n === 1) return 'xs'
  if (n === 2) return 'sm'
  if (n === 3) return 'md'
  if (n === 4) return 'lg'
  return 'xl'
}

function progressWidthSizeToPx(width_size) {
  const n = Number(width_size)
  if (Number.isNaN(n) || n < 0) return undefined
  // legacy uses CSS classes; here we approximate.
  if (n === 0) return 120
  if (n === 1) return 180
  if (n === 2) return 240
  if (n === 3) return 320
  if (n === 4) return 420
  return 520
}

function getHandler(element, keys) {
  const handlers = element?.handlers
  if (!handlers) return undefined
  for (const k of keys) {
    if (handlers[k]) return handlers[k]
  }
  return undefined
}

function renderChildren(list, context, actions) {
  if (!Array.isArray(list) || list.length === 0) return null
  return <ElementsRenderer elements={list} context={context} actions={actions} />
}

function safeJsonStringify(value) {
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

function QRCodeCanvas({ value, size = 150, level = 'H', style }) {
  const canvasRef = React.useRef(null)

  React.useEffect(() => {
    let cancelled = false
    const canvas = canvasRef.current
    if (!canvas) return
    const text = value == null ? '' : String(value)

    ;(async () => {
      try {
        await QRCode.toCanvas(canvas, text, {
          errorCorrectionLevel: level,
          width: size,
          margin: 1
        })
      } catch (err) {
        if (!cancelled) {
          // fallback: clear
          const ctx = canvas.getContext('2d')
          if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height)
          // eslint-disable-next-line no-console
          console.warn('qrcode render failed', err)
        }
      }
    })()

    return () => {
      cancelled = true
    }
  }, [value, size, level])

  return <canvas ref={canvasRef} style={style} />
}

export function ElementRenderer({ element, context, actions }) {
  if (!element) return null

  const type = element.type
  let typeNorm = (type == null ? '' : String(type)).toLowerCase().replace(/-/g, '_')

  // Special legacy aliases
  if (typeNorm === 'navbar') typeNorm = 'nav_bar'
  if (typeNorm === 'side_bar') typeNorm = 'side_bar'
  if (typeNorm === 'card_swiper') typeNorm = 'card_swiper'
  if (typeNorm === 'data_table') typeNorm = 'data_table'
  if (typeNorm === 'nav_menu') typeNorm = 'nav_menu'
  if (typeNorm === 'row') typeNorm = 'row_line'
  if (typeNorm === 'progressbar') typeNorm = 'progress_bar'

  if (typeNorm === 'decoration') {
    if (typeof actions.renderDecoration === 'function') {
      return actions.renderDecoration(element, context)
    }
    return null
  }

  if (typeNorm === 'hero') {
    return (
      <div style={{ ...(styleFrom(element) || {}), padding: 12, borderRadius: 8, background: 'var(--surface-0)' }}>
        {element.image_src ? (
          <img alt="" src={element.image_src} style={{ width: '100%', maxHeight: 280, objectFit: 'cover', borderRadius: 8 }} />
        ) : null}
        {element.title ? <h2 style={{ marginBottom: 6 }}>{element.title}</h2> : null}
        {element.text ? <div style={{ marginBottom: 10 }}>{element.text}</div> : null}
        {renderChildren(element.elements, context, actions)}
      </div>
    )
  }

  if (typeNorm === 'logo') {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, ...(styleFrom(element) || {}) }}>
        {element.image_src ? <img alt="" src={element.image_src} style={{ height: 28 }} /> : null}
        {element.text ? <span style={{ fontWeight: 600 }}>{element.text}</span> : null}
      </div>
    )
  }

  if (typeNorm === 'header') {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, ...(styleFrom(element) || {}) }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {renderChildren(element.start_elements, context, actions)}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, justifyContent: 'center' }}>
          {renderChildren(element.elements, context, actions)}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {renderChildren(element.end_elements, context, actions)}
        </div>
      </div>
    )
  }

  if (typeNorm === 'footer') {
    const footerMain = element.element
    const left = element.left_elements
    const right = element.right_elements
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, ...(styleFrom(element) || {}) }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>{renderChildren(left, context, actions)}</div>
        <div style={{ flex: 1, textAlign: 'center' }}>
          {footerMain ? <ElementRenderer element={footerMain} context={context} actions={actions} /> : null}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'flex-end' }}>
          {renderChildren(right, context, actions)}
        </div>
      </div>
    )
  }

  if (typeNorm === 'action_bar') {
    const core = context?.app_id ? AppCore.getCore(context.app_id) : undefined
    const els = element.elements || []
    const renderAction = (act, idx) => {
      const icon = act.icon && core ? core.full_link(act.icon) : act.icon
      const disabled = !!act.disable
      const onClick = async () => {
        if (disabled) return
        if (act.route) {
          await actions.navigateTo?.(act.route, context)
        } else if (act.open_modal) {
          if (!actions.openModal) return
          const modal_id = actions.modal_new_id?.() || undefined
          const option = {
            title: act.open_modal.title,
            text: act.open_modal.content,
            content_html: act.open_modal.content_html,
            actionConfirmText: act.open_modal.confirm?.text,
            actionCancelText: act.open_modal.cancel?.text,
            onModalConfirmed: async () => {
              if (act.open_modal.confirm?.action && core) {
                const cmds = await core.callAction({ action: act.open_modal.confirm.action, args: act.open_modal.confirm.args || {} })
                await actions.handleCommands?.(cmds, context)
              }
            },
            onModalCancelled: async () => {
              if (act.open_modal.cancel?.action && core) {
                const cmds = await core.callAction({ action: act.open_modal.cancel.action, args: act.open_modal.cancel.args || {} })
                await actions.handleCommands?.(cmds, context)
              }
            }
          }
          const slot_render = () => {
            if (act.open_modal.elements && Array.isArray(act.open_modal.elements) && act.open_modal.elements.length > 0) {
              return <ElementsRenderer elements={act.open_modal.elements} context={{ ...context, modal_id }} actions={actions} />
            }
            return null
          }
          const inplace = !!act?.open_modal_args?.inplace
          actions.openModal(modal_id, option, slot_render, context, inplace)
        } else if (act.action && core) {
          const cmds = await core.callAction({ action: act.action, args: act.args || {} })
          await actions.handleCommands?.(cmds, context)
        }
        if (core) {
          app_platform.logEvent(AnalyticsEventKind.button_event, { route: core.app_page?.route || context?.route, text: act.text })
        }
      }

      return (
        <Button
          key={idx}
          label={act.text}
          icon={icon ? undefined : act.icon}
          disabled={disabled}
          onClick={onClick}
          text
        />
      )
    }

    return <div style={{ display: 'flex', gap: 8, ...(styleFrom(element) || {}) }}>{els.map(renderAction)}</div>
  }

  if (typeNorm === 'table_view') {
    const cols = element.columns || []
    const rows = element.rows || []
    const showHeader = !!element.show?.header
    const showInnerColumn = !!element.show?.inner_column
    const showInnerRow = !!element.show?.inner_row

    return (
      <div style={{ overflowX: 'auto', ...(styleFrom(element) || {}) }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          {showHeader ? (
            <thead>
              <tr>
                {cols.map((c, idx) => (
                  <th key={idx} style={{ textAlign: 'left', padding: 8, borderBottom: '1px solid var(--surface-200)' }}>
                    {c}
                  </th>
                ))}
              </tr>
            </thead>
          ) : null}
          <tbody>
            {rows.map((r, ridx) => (
              <tr
                key={ridx}
                style={{
                  borderBottom: showInnerRow ? '1px solid var(--surface-200)' : undefined
                }}
              >
                {(r || []).map((cell, cidx) => (
                  <td
                    key={cidx}
                    style={{
                      padding: 8,
                      verticalAlign: 'top',
                      borderRight: showInnerColumn ? '1px solid var(--surface-200)' : undefined
                    }}
                  >
                    <ElementRenderer element={cell} context={context} actions={actions} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  if (typeNorm === 'tab_bar') {
    const tabs = element.tabs || []
    return (
      <div style={{ display: 'flex', gap: 8, ...(styleFrom(element) || {}) }}>
        {tabs.map((t, idx) => {
          const checked = !!t.checked
          const onClick = async () => {
            if (t.href) {
              await actions.navigateTo?.(t.href, context)
            }
          }
          return <Button key={idx} label={t.text} onClick={onClick} outlined={!checked} size="small" />
        })}
      </div>
    )
  }

  if (typeNorm === 'popup_menu') {
    const core = context?.app_id ? AppCore.getCore(context.app_id) : undefined
    const ref = React.useRef(null)
    const items = element.elements || []

    const evalVisible = (node) => {
      if (node == null) return true
      if (typeof node === 'boolean') return node
      if (typeof node !== 'object') return true
      if (String(node.type || '') !== 'expr') return true
      const expr = String(node.expr || '').trim()
      const it = context?.locals?.it
      if (!expr) return true
      if (expr === 'it') return !!it
      if (expr.startsWith('it.')) {
        const parts = expr.slice(3).split('.')
        let cur = it
        for (const p of parts) {
          if (cur == null) return false
          cur = cur[p]
        }
        return !!cur
      }
      if (expr.startsWith('not ')) {
        const inner = expr.slice(4).trim()
        if (inner.startsWith('it.')) {
          const parts = inner.slice(3).split('.')
          let cur = it
          for (const p of parts) {
            if (cur == null) return true
            cur = cur[p]
          }
          return !cur
        }
      }
      return true
    }

    const model = items
      .filter((it) => {
        return evalVisible(it?.visible)
      })
      .map((it) => {
        const icon = it.icon ? `pi pi-${it.icon}` : undefined
        return {
          label: it.label || it.text || '',
          icon,
          command: async () => {
            const click = it?.events?.click
            if (!click) return

            // Minimal compatibility for example DSL nodes.
            if (click.type === 'route-to' && click.route) {
              await actions.navigateTo?.(click.route, context)
              return
            }

            if (click.type === 'show-modal' && click.name) {
              if (typeof actions.openInterfaceModal === 'function') {
                await actions.openInterfaceModal(click.name, click.args, context)
                return
              }
              // Fallback to debug modal
              const modal_id = actions.modal_new_id?.() || undefined
              const option = {
                title: String(click.name),
                content_html: `<pre style="white-space:pre-wrap;">${safeJsonStringify(click)}</pre>`,
                actionConfirmText: 'OK'
              }
              actions.openModal?.(modal_id, option, () => null, context)
              return
            }

            if (typeof actions.runDslNode === 'function' && click.type) {
              await actions.runDslNode(click, context)
              return
            }

            if (click.action && core) {
              const cmds = await core.callAction({ action: click.action, args: click.args || {} })
              await actions.handleCommands?.(cmds, context)
              return
            }

            // Fallback: debug modal
            const modal_id = actions.modal_new_id?.() || undefined
            const option = {
              title: 'Action',
              content_html: `<pre style="white-space:pre-wrap;">${safeJsonStringify(click)}</pre>`,
              actionConfirmText: 'OK'
            }
            actions.openModal?.(modal_id, option, () => null, context)
          }
        }
      })

    return (
      <div style={{ display: 'inline-flex', ...(styleFrom(element) || {}) }}>
        <Button icon={element.icon ? `pi pi-${element.icon}` : 'pi pi-ellipsis-v'} text onClick={(e) => ref.current?.toggle?.(e)} />
        <PrimeMenu model={model} popup ref={ref} />
      </div>
    )
  }

  if (typeNorm === 'menu_item') {
    const label = element.label || element.text || ''
    const icon = element.icon ? `pi pi-${element.icon}` : undefined
    const disabled = !!element.disable
    const onClick = async (e) => {
      e?.stopPropagation?.()
      if (disabled) return
      const click = element?.events?.click
      if (!click) return

      if (click.type === 'route-to' && click.route) {
        await actions.navigateTo?.(click.route, context)
        return
      }

      if (click.type === 'show-modal' && click.name) {
        if (typeof actions.openInterfaceModal === 'function') {
          await actions.openInterfaceModal(click.name, click.args, context)
          return
        }
      }

      if (typeof actions.runDslNode === 'function' && click.type) {
        await actions.runDslNode(click, context)
        return
      }
    }

    return <Button label={label} icon={icon} disabled={disabled} onClick={onClick} text style={styleFrom(element)} />
  }

  if (typeNorm === 'page') {
    // Safety: page definitions usually appear inside interfaces; render elements if provided.
    return <ElementsRenderer elements={element.elements || []} context={context} actions={actions} />
  }

  if (typeNorm === 'modal') {
    // Safety: modal definitions usually appear inside interfaces; render its elements if provided.
    return <ElementsRenderer elements={element.elements || []} context={context} actions={actions} />
  }

  // Safety: if a DSL node is accidentally passed to ElementRenderer, don't crash or warn.
  if (
    typeNorm === 'action' ||
    typeNorm === 'attribute' ||
    typeNorm === 'enum' ||
    typeNorm === 'property' ||
    typeNorm === 'resource' ||
    typeNorm === 'config' ||
    typeNorm === 'object_meta' ||
    typeNorm === 'thing_route_config' ||
    typeNorm === 'component' ||
    typeNorm === 'component_use' ||
    typeNorm === 'element_option' ||
    typeNorm === 'text_option' ||
    typeNorm === 'local_value' ||
    typeNorm === 'query' ||
    typeNorm === 'expr' ||
    typeNorm === 'format' ||
    typeNorm === 'locals' ||
    typeNorm === 'foreach' ||
    typeNorm === 'match' ||
    typeNorm === 'case_value' ||
    typeNorm === 'condition_check' ||
    typeNorm === 'validate_locals' ||
    typeNorm === 'data_process' ||
    typeNorm === 'data_extract' ||
    typeNorm === 'data_filter' ||
    typeNorm === 'data_format' ||
    typeNorm === 'datetime_format' ||
    typeNorm === 'refresh' ||
    typeNorm === 'route_to' ||
    typeNorm === 'show_modal' ||
    typeNorm === 'delete_object' ||
    typeNorm === 'create_object' ||
    typeNorm === 'update_object' ||
    typeNorm === 'invoke_action' ||
    typeNorm === 'invoke_service' ||
    typeNorm === 'table_column'
  ) {
    return null
  }

  if (typeNorm === 'clock') {
    const showDate = !!element.show_date
    const now = new Date()
    const hh = String(now.getHours()).padStart(2, '0')
    const mm = String(now.getMinutes()).padStart(2, '0')
    const ss = String(now.getSeconds()).padStart(2, '0')
    const date = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
    return (
      <div style={{ ...(styleFrom(element) || {}) }}>
        {showDate ? <div style={{ opacity: 0.7, fontSize: 12 }}>{date}</div> : null}
        <div style={{ fontVariantNumeric: 'tabular-nums' }}>{`${hh}:${mm}:${ss}`}</div>
      </div>
    )
  }

  if (typeNorm === 'qrcode') {
    const size = element.size || 150
    const level = element.level || 'H'
    return (
      <div style={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'center', gap: 8, ...(styleFrom(element) || {}) }}>
        <QRCodeCanvas value={element.code} size={size} level={level} style={{ width: size, height: size }} />
        {element.text ? <div style={{ marginTop: 2 }}>{element.text}</div> : null}
      </div>
    )
  }

  if (typeNorm === 'nav_menu') {
    const core = context?.app_id ? AppCore.getCore(context.app_id) : undefined
    const items = element.elements || []
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, ...(styleFrom(element) || {}) }}>
        {items.map((it, idx) => {
          const disabled = !!it.disable
          const icon = core ? core.full_link(it.icon) : it.icon
          const onClick = async () => {
            if (disabled) return
            if (it.route !== undefined) {
              await actions.navigateTo?.(it.route, context)
            } else if (it.open_url) {
              app_platform.openUrl(it.open_url)
            } else if (it.open_modal) {
              if (!core || !actions.openModal) return
              const modal = it.open_modal
              const modal_id = actions.modal_new_id?.() || undefined
              const modal_context = { ...context, modal_id, locals: { ...(modal.locals || {}), ...(context?.locals || {}) } }

              const option = {
                title: modal.title,
                text: modal.content,
                content_html: modal.content_html,
                actionConfirmText: modal.confirm?.text,
                actionCancelText: modal.cancel?.text,
                onModalConfirmed: async () => {
                  if (modal.confirm?.action) {
                    const cmds = await core.callAction({ action: modal.confirm.action, args: modal.confirm.args || {} })
                    await actions.handleCommands?.(cmds, modal_context)
                  }
                },
                onModalCancelled: async () => {
                  if (modal.cancel?.action) {
                    const cmds = await core.callAction({ action: modal.cancel.action, args: modal.cancel.args || {} })
                    await actions.handleCommands?.(cmds, modal_context)
                  }
                }
              }

              const slot_render = () => {
                if (modal.elements && Array.isArray(modal.elements) && modal.elements.length > 0) {
                  return <ElementsRenderer elements={modal.elements} context={modal_context} actions={actions} />
                }
                return null
              }

              const inplace = !!it?.open_modal_args?.inplace
              actions.openModal(modal_id, option, slot_render, context, inplace)
            }

            if (core) {
              app_platform.logEvent(AnalyticsEventKind.button_event, {
                route: core.app_page?.route || context?.route,
                text: it.text
              })
            }
          }

          return (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '8px 10px',
                borderRadius: 6,
                cursor: disabled ? 'not-allowed' : 'pointer',
                opacity: disabled ? 0.5 : 1,
                background: 'var(--surface-0)'
              }}
              onClick={onClick}
            >
              {icon ? <img alt="" src={icon} style={{ width: 18, height: 18 }} /> : null}
              <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                <div style={{ fontWeight: 600 }}>{it.text}</div>
                {it.sub_text ? <div style={{ fontSize: 12, opacity: 0.75 }}>{it.sub_text}</div> : null}
                {disabled && it.disable_text ? <div style={{ fontSize: 12 }}>{it.disable_text}</div> : null}
              </div>
              <i className="pi pi-angle-right" />
            </div>
          )
        })}
      </div>
    )
  }

  if (typeNorm === 'nav_bar') {
    const left = () => {
      if (element.show_home) {
        return <Button icon="pi pi-home" text onClick={() => actions.navigateTo?.('/', context)} />
      }
      if (element.show_back) {
        return <Button icon="pi pi-arrow-left" text onClick={() => window.history.back()} />
      }
      return null
    }

    const center = () => <div style={{ fontWeight: 600 }}>{element.title || ''}</div>

    const right = () => {
      const extra = element.elements
      if (Array.isArray(extra) && extra.length > 0) {
        return <ElementsRenderer elements={extra} context={context} actions={actions} />
      }
      if (element.show_profile) {
        return <Button icon="pi pi-user" text onClick={() => actions.onNavigate?.('profile', context)} />
      }
      return null
    }

    return (
      <div style={{ position: 'sticky', top: 0, zIndex: 10, background: 'var(--surface-0)' }}>
        <Toolbar start={left} center={center} end={right} />
      </div>
    )
  }

  if (typeNorm === 'side_bar') {
    const justify = element.style?.justify || 'start'
    const align = element.style?.align || 'center'
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: justify,
          alignItems: align,
          gap: 12,
          ...(styleFrom(element) || {})
        }}
      >
        {renderChildren(element.elements, { ...context, locals: element.locals || context.locals }, actions)}
      </div>
    )
  }

  if (typeNorm === 'menu') {
    const ref = React.useRef(null)
    const model = (element.items || []).map((it) => ({
      label: it.label || '',
      icon: it.icon ? `pi pi-${it.icon}` : undefined,
      command: () => {
        const clickHandler = it.handlers?.click
        if (clickHandler) actions.interact('', 'click', clickHandler, undefined, context)
      }
    }))

    return (
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, ...(styleFrom(element) || {}) }}>
        <Button
          label={element.label || ''}
          icon={element.icon ? `pi pi-${element.icon}` : undefined}
          onClick={(e) => ref.current?.toggle?.(e)}
          outlined
        />
        <PrimeMenu model={model} popup ref={ref} />
      </div>
    )
  }

  if (typeNorm === 'card') {
    const header = element.image_src ? <img alt="" src={element.image_src} style={{ width: '100%', display: 'block' }} /> : null
    const content = (
      <div>
        {element.text ? <p style={{ marginTop: 0 }}>{element.text}</p> : null}
        {renderChildren(element.elements, { ...context, locals: element.locals || context.locals }, actions)}
      </div>
    )

    return (
      <Card
        title={element.title || undefined}
        subTitle={element.sub_title || undefined}
        header={header}
        style={{
          border: element.show_border === false ? 'none' : undefined,
          ...(styleFrom(element) || {})
        }}
      >
        {content}
      </Card>
    )
  }

  if (typeNorm === 'card_swiper') {
    return (
      <div style={{ ...(styleFrom(element) || {}) }}>
        {element.title ? <h3 style={{ marginTop: 0 }}>{element.title}</h3> : null}
        <div style={{ display: 'flex', overflowX: 'auto', gap: 12, paddingBottom: 8 }}>
          {(element.elements || []).map((el, idx) => (
            <div key={idx} style={{ flex: '0 0 auto', minWidth: 280 }}>
              <ElementRenderer element={el} context={context} actions={actions} />
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Container elements
  if (typeNorm === 'header' || typeNorm === 'footer') {
    // Minimal: just render nested elements
    const children = element.elements || element.start_elements || element.end_elements || element.left_elements || element.right_elements
    return <div style={styleFrom(element)}>{renderChildren(children, context, actions)}</div>
  }

  if (typeNorm === 'column' || typeNorm === 'row_line') {
    const isRow = typeNorm === 'row_line'
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: isRow ? 'row' : 'column',
          gap: 12,
          ...(styleFrom(element) || {})
        }}
      >
        {renderChildren(element.elements, { ...context, locals: element.locals || context.locals }, actions)}
      </div>
    )
  }

  if (typeNorm === 'title') {
    const level = element.level || 1
    const Tag = `h${Math.min(6, Math.max(1, level))}`
    return (
      <Tag style={styleFrom(element)}>
        {element.title}
        {element.sub_title ? <small style={{ marginLeft: 8 }}>{element.sub_title}</small> : null}
      </Tag>
    )
  }

  if (typeNorm === 'paragraph') {
    const align = element.align === 'start' ? 'left' : element.align === 'end' ? 'right' : element.align
    const style = { ...(styleFrom(element) || {}), textAlign: align || undefined }
    if (element.isRich === false) {
      const texts = String(element.text || '').split('\n')
      return (
        <div style={style}>
          {texts.map((t, idx) => (
            <div key={idx}>{t}</div>
          ))}
        </div>
      )
    }
    return (
      <div style={style}>
        <RichText text={element.text || ''} />
      </div>
    )
  }

  if (typeNorm === 'plain_text') {
    return (
      <div style={styleFrom(element)}>
        <RichText text={element.text || ''} />
      </div>
    )
  }

  if (typeNorm === 'annotation_text') {
    return (
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, ...(styleFrom(element) || {}) }}>
        <span>{element.text}</span>
        <small style={{ opacity: 0.7 }}>{element.annotation}</small>
      </div>
    )
  }

  if (typeNorm === 'status_text') {
    const label = element.label ? `${element.label}:` : ''
    return (
      <div style={{ display: 'flex', gap: 8, ...(styleFrom(element) || {}) }}>
        <span style={{ fontWeight: 600 }}>{label}</span>
        <span>{element.text}</span>
      </div>
    )
  }

  if (typeNorm === 'bulleted_list') {
    const texts = element.texts || []
    return (
      <div style={styleFrom(element)}>
        <ul style={{ marginTop: 0 }}>
          {texts.map((t, idx) => (
            <li key={idx}>{t}</li>
          ))}
        </ul>
      </div>
    )
  }

  if (typeNorm === 'link') {
    const url = element.target_url
    const open_mode = element.open_mode || 'new'
    const onClick = (e) => {
      e.preventDefault()
      if (open_mode === 'new') {
        app_platform.openUrl(url)
      }
    }
    return (
      <a href={url} onClick={onClick} style={styleFrom(element)}>
        {element.text}
      </a>
    )
  }

  if (typeNorm === 'image') {
    const sizeName = getSizeName(element.size)
    const maxH = sizeName === 'xs' ? 80 : sizeName === 'sm' ? 120 : sizeName === 'lg' ? 240 : sizeName === 'xl' ? 360 : undefined
    return (
      <img
        alt=""
        src={element.image_url}
        style={{ maxWidth: '100%', maxHeight: maxH, objectFit: 'cover', ...(styleFrom(element) || {}) }}
        crossOrigin="anonymous"
      />
    )
  }

  if (typeNorm === 'video') {
    const muted = element.muted == null ? true : !!element.muted
    const autoplay = element.autoplay == null ? false : !!element.autoplay
    const w = element.width
    const h = element.height
    return (
      <video
        poster={element.poster_url}
        controls
        autoPlay={autoplay}
        muted={muted}
        width={w}
        height={h}
        style={{ width: w ? undefined : '100%', ...(styleFrom(element) || {}) }}
        crossOrigin="anonymous"
      >
        <source src={element.video_url} type={element.video_type || 'video/mp4'} />
      </video>
    )
  }

  if (typeNorm === 'star_rating') {
    return <Rating value={element.rating} readOnly cancel={false} />
  }

  if (typeNorm === 'icon') {
    const core = context?.app_id ? AppCore.getCore(context.app_id) : undefined
    const src = core ? core.full_link(element.icon) : element.icon
    return <img alt="" src={src} style={{ height: '1.5em', ...(element.style || {}) }} />
  }

  if (typeNorm === 'icon_text') {
    const core = context?.app_id ? AppCore.getCore(context.app_id) : undefined
    const src = core ? core.full_link(element.icon) : element.icon
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, ...(element.style || {}) }}>
        {src ? <img alt="" src={src} style={{ height: '1.5em' }} /> : null}
        <span>{element.text}</span>
      </div>
    )
  }

  if (typeNorm === 'icon_number') {
    const core = context?.app_id ? AppCore.getCore(context.app_id) : undefined
    const src = core ? core.full_link(element.icon) : element.icon
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {src ? <img alt="" src={src} style={{ height: '1.5em' }} /> : null}
        <span style={{ fontWeight: 600 }}>{element.number}</span>
      </div>
    )
  }

  if (typeNorm === 'icon_title') {
    const core = context?.app_id ? AppCore.getCore(context.app_id) : undefined
    const src = core ? core.full_link(element.icon) : element.icon
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {src ? <img alt="" src={src} style={{ height: '1.5em' }} /> : null}
        <span style={{ fontWeight: 600 }}>{element.count}</span>
      </div>
    )
  }

  if (typeNorm === 'icon_number_text') {
    const maxDigits = element.maxDigits ?? element.max_digits ?? 6
    const maxNumber = Math.pow(10, maxDigits) - 1
    const number = Number(element.number ?? 0)
    const numberText = number <= maxNumber ? String(number) : `${maxNumber}+`
    const icon = element.icon || ''
    const isUrlIcon = icon.includes('/') || icon.includes('.') || icon.startsWith('http')
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, ...(styleFrom(element) || {}) }}>
        {isUrlIcon ? <img alt="" src={icon} width={24} height={24} /> : icon ? <i className={icon} /> : null}
        <div>{numberText}</div>
      </div>
    )
  }

  if (typeNorm === 'icon_number_button') {
    const number = Number(element.number ?? 0)
    const maxDigits = element.maxDigits ?? element.max_digits ?? 2
    const maxNumber = Math.pow(10, maxDigits) - 1
    const numberText = number < 0 ? '0' : number <= maxNumber ? String(number) : `${maxNumber}+`
    const icon = element.icon || ''
    const size = element.size || 24
    const minClickDuration = element.minClickDuration ?? element.min_click_duration ?? 500
    const lastClickRef = React.useRef(0)
    const isUrlIcon = icon.includes('/') || icon.includes('.') || icon.startsWith('http')

    return (
      <button
        type="button"
        data-badge={numberText}
        style={{
          position: 'relative',
          border: 'none',
          background: 'transparent',
          padding: 0,
          cursor: 'pointer',
          ...(styleFrom(element) || {})
        }}
        onClick={(e) => {
          e.stopPropagation?.()
          const now = Date.now()
          if (now - lastClickRef.current > minClickDuration) {
            lastClickRef.current = now
            actions.onButtonClick?.(element, context)
          }
        }}
      >
        {isUrlIcon ? <img alt="" src={icon} width={size} height={size} /> : icon ? <i className={icon} /> : null}
        {number > 0 ? (
          <span
            style={{
              position: 'absolute',
              top: -6,
              right: -6,
              minWidth: 16,
              height: 16,
              padding: '0 4px',
              borderRadius: 999,
              background: 'crimson',
              color: 'white',
              fontSize: 10,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              lineHeight: 1
            }}
          >
            {numberText}
          </span>
        ) : null}
      </button>
    )
  }

  if (typeNorm === 'icon_button') {
    const disabled = !!element.disable
    const size = element.size || 24
    const icon = element.icon || ''
    const isUrlIcon = icon.includes('/') || icon.includes('.') || icon.startsWith('http')
    return (
      <Button
        icon={isUrlIcon ? undefined : icon}
        disabled={disabled}
        rounded
        text
        onClick={(e) => {
          e.stopPropagation?.()
          actions.onButtonClick(element, context)
        }}
      >
        {isUrlIcon ? <img alt="" src={icon} width={size} height={size} /> : null}
      </Button>
    )
  }

  if (typeNorm === 'button') {
    const disabled = !!element.disable
    const clickHandlersRaw = element?.events?.click
    const clickHandlers =
      clickHandlersRaw == null ? [] : Array.isArray(clickHandlersRaw) ? clickHandlersRaw : [clickHandlersRaw]
    const openMenuHandler = clickHandlers.find((h) => h && h.type === 'open-menu')

    const menuRef = React.useRef(null)
    const core = context?.app_id ? AppCore.getCore(context.app_id) : undefined
    const menuModel = openMenuHandler?.menu?.items
      ? (openMenuHandler.menu.items || []).map((it) => {
          const handler = getHandler(it, ['clicked', 'click'])
          const icon = it.icon && core ? core.full_link(it.icon) : it.icon
          return {
            label: it.label,
            icon,
            disabled: !!it.disable,
            command: () => {
              if (handler) actions.interact('', 'click', handler, undefined, context)
            }
          }
        })
      : null

    return (
      <>
        {menuModel ? <PrimeMenu model={menuModel} popup ref={menuRef} /> : null}
        <Button
          label={element.text}
          icon={element.icon}
          disabled={disabled}
          onClick={(e) => {
            if (menuModel && menuRef.current) {
              menuRef.current.toggle(e)
              return
            }
            actions.onButtonClick(element, context)
          }}
        />
      </>
    )
  }

  if (typeNorm === 'input') {
    const handler = getHandler(element, ['changed', 'change', 'input'])
    return (
      <span className="p-float-label" style={{ width: '100%', ...(styleFrom(element) || {}) }}>
        <InputText
          id={element.name || element.label}
          value={element.value ?? ''}
          type={element.password ? 'password' : 'text'}
          onChange={(e) => handler && actions.interact(element.name || element.label || 'input', 'change', handler, e.target.value, context)}
          style={{ width: '100%' }}
        />
        {element.label ? <label htmlFor={element.name || element.label}>{element.label}</label> : null}
      </span>
    )
  }

  if (typeNorm === 'textarea') {
    const handler = getHandler(element, ['changed', 'change', 'input'])
    return (
      <span style={{ width: '100%', ...(styleFrom(element) || {}) }}>
        {element.label ? <div style={{ marginBottom: 6 }}>{element.label}</div> : null}
        <InputTextarea
          value={element.value ?? ''}
          rows={element.rows || 4}
          cols={element.cols}
          onChange={(e) => handler && actions.interact(element.name || element.label || 'textarea', 'change', handler, e.target.value, context)}
          style={{ width: '100%' }}
        />
      </span>
    )
  }

  if (typeNorm === 'dropdown') {
    const handler = getHandler(element, ['changed', 'change', 'select'])
    return (
      <span style={{ width: '100%', ...(styleFrom(element) || {}) }}>
        {element.label ? <div style={{ marginBottom: 6 }}>{element.label}</div> : null}
        <Dropdown
          value={element.value}
          options={element.options || []}
          optionLabel="label"
          optionValue="value"
          onChange={(e) => handler && actions.interact(element.name || element.label || 'dropdown', 'change', handler, e.value, context)}
          style={{ width: '100%' }}
        />
      </span>
    )
  }

  if (typeNorm === 'calendar') {
    const handler = getHandler(element, ['changed', 'change', 'select'])
    return (
      <span style={{ width: '100%', ...(styleFrom(element) || {}) }}>
        {element.label ? <div style={{ marginBottom: 6 }}>{element.label}</div> : null}
        <Calendar
          value={element.value ? new Date(element.value) : null}
          onChange={(e) => handler && actions.interact(element.name || element.label || 'calendar', 'change', handler, e.value, context)}
          showIcon={toBool(element.icon)}
          selectionMode={toBool(element.range) ? 'range' : 'single'}
          showTime={toBool(element.show_time)}
          dateFormat={element.value_format || undefined}
          style={{ width: '100%' }}
        />
      </span>
    )
  }

  if (typeNorm === 'checkbox') {
    const handler = getHandler(element, ['changed', 'change', 'toggle'])
    const checkHandler = element?.handlers?.check
    const checked = toBool(element.value)
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, ...(styleFrom(element) || {}) }}>
        <Checkbox
          inputId={element.name || element.text}
          checked={checked}
          onChange={(e) => {
            const next = !!e.checked
            const trigger = checked !== next
            const locals = { ...(context?.locals || {}) }
            if (element.name) {
              deepSet(locals, element.name, next)
            }

            if (checkHandler && trigger) {
              actions.interact('', 'check', checkHandler, next, { ...context, locals })
              return
            }

            if (handler) {
              actions.interact(element.name || element.text || 'checkbox', 'change', handler, next, { ...context, locals })
            }
          }}
        />
        {element.text ? <label htmlFor={element.name || element.text}>{element.text}</label> : null}
      </div>
    )
  }

  if (typeNorm === 'input_switch') {
    const handler = getHandler(element, ['changed', 'change', 'toggle'])
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, ...(styleFrom(element) || {}) }}>
        <InputSwitch
          checked={toBool(element.value)}
          onChange={(e) => handler && actions.interact(element.name || 'input_switch', 'change', handler, e.value, context)}
        />
        {element.text ? <span>{element.text}</span> : null}
      </div>
    )
  }

  if (typeNorm === 'multi_select') {
    const handler = getHandler(element, ['changed', 'change', 'select'])
    return (
      <span style={{ width: '100%', ...(styleFrom(element) || {}) }}>
        {element.label ? <div style={{ marginBottom: 6 }}>{element.label}</div> : null}
        <MultiSelect
          value={element.values || []}
          options={element.options || []}
          optionLabel="label"
          optionValue="value"
          onChange={(e) => handler && actions.interact(element.name || element.label || 'multi_select', 'change', handler, e.value, context)}
          display={toBool(element.chips) ? 'chip' : 'comma'}
          style={{ width: '100%' }}
        />
      </span>
    )
  }

  if (typeNorm === 'tag') {
    return <Tag value={element.text} severity={element.color} style={styleFrom(element)} />
  }

  if (typeNorm === 'avatar') {
    return <Avatar image={element.image_src} icon={element.icon} style={styleFrom(element)} />
  }

  if (typeNorm === 'progressbar' || typeNorm === 'progress_bar') {
    // Legacy has two widgets: Progressbar (Prime) and ProgressBar (custom bar with text).
    // We render a custom bar when percent/value/total are provided; otherwise fallback to PrimeReact ProgressBar.
    let percentValue = undefined
    let progressText = ''

    if (typeof element.value === 'number' && typeof element.total === 'number' && element.total > 0) {
      percentValue = Math.floor((element.value * 100) / element.total)
      if (percentValue > 100) percentValue = 100
      if (percentValue < 0) percentValue = 0
      progressText = `${element.value}/${element.total}`
    } else if (typeof element.percent === 'number' && element.percent >= 0) {
      percentValue = Math.floor(element.percent)
      if (percentValue > 100) percentValue = 100
      if (percentValue < 0) percentValue = 0
      progressText = `${percentValue}%`
    }

    const widthPx = progressWidthSizeToPx(element.width_size)
    if (percentValue == null) {
      const value = element.percent ?? (element.total ? (100 * (element.value || 0)) / element.total : undefined)
      return <ProgressBar value={value} style={styleFrom(element)} />
    }

    const wrapperStyle = {
      width: widthPx ? `${widthPx}px` : '100%',
      maxWidth: '100%',
      height: 18,
      borderRadius: 999,
      overflow: 'hidden',
      background: 'var(--surface-200)',
      ...(styleFrom(element) || {})
    }

    return (
      <div style={wrapperStyle}>
        <div
          style={{
            width: `${percentValue}%`,
            height: '100%',
            background: 'var(--primary-color, #3B82F6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--primary-color-text, white)',
            fontSize: 12,
            whiteSpace: 'nowrap'
          }}
        >
          {progressText}
        </div>
      </div>
    )
  }

  if (typeNorm === 'toolbar') {
    const start = () => renderChildren(element.start_elements, context, actions)
    const center = () => renderChildren(element.elements, context, actions)
    const end = () => renderChildren(element.end_elements, context, actions)
    return <Toolbar start={start} center={center} end={end} style={styleFrom(element)} />
  }

  if (typeNorm === 'data_table') {
    const cols = element.columns || []
    const value = element.data || []
    return (
      <DataTable value={value} paginator={!!element.paginator} {...(element.paginator || {})} style={styleFrom(element)}>
        {cols.map((c, idx) => {
          const isTableColumn = (c?.type || '').toLowerCase() === 'table-column'
          const colField = isTableColumn ? c.field : c.field || c['field']
          const field = colField

          if (isTableColumn) {
            const header = c.label
            const colStyle = c.style
            const elements = c.elements
            if (Array.isArray(elements) && elements.length > 0) {
              const body = (rowData) => {
                const locals = { ...stripColLocals(rowData), it: rowData }
                return <ElementsRenderer elements={elements} context={{ ...context, locals }} actions={actions} />
              }
              return <Column key={idx} field={field} header={header} style={colStyle} body={body} />
            }
            return <Column key={idx} field={field} header={header} style={colStyle} />
          }

          if (typeof field === 'string' && field.startsWith('__col_')) {
            const body = (rowData) => {
              const cellEl = rowData?.[field]
              const locals = { ...stripColLocals(rowData), it: rowData }
              return <ElementRenderer element={cellEl} context={{ ...context, locals }} actions={actions} />
            }
            const newCol = { ...c }
            delete newCol.field
            return <Column key={idx} {...newCol} body={body} />
          }
          return <Column key={idx} {...c} />
        })}
      </DataTable>
    )
  }

  if (typeNorm === 'separator' || typeNorm === 'divider') {
    return <hr />
  }

  // Explicitly skip excluded types
  if (type === 'motion' || type === 'playable') {
    return null
  }

  return <div style={{ color: 'crimson' }}>Unsupported element: {type}</div>
}

export function ElementsRenderer({ elements, context, actions }) {
  if (!elements || elements.length === 0) return null
  return (
    <div>
      {elements.map((el, idx) => (
        <div key={idx} style={{ marginBottom: 12 }}>
          <ElementRenderer element={el} context={context} actions={actions} />
        </div>
      ))}
    </div>
  )
}
