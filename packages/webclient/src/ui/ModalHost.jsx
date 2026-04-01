import React, { useMemo } from 'react'
import { Dialog } from 'primereact/dialog'

export function ModalHost({ modal_helper }) {
  const useStore = modal_helper?.__useStore
  const state = useStore ? useStore() : { current: undefined }
  const current = state.current

  const footer = useMemo(() => {
    if (!current?.option) return undefined
    const confirmText = current.option.actionConfirmText || current.option.confirmText || 'OK'
    const cancelText = current.option.actionCancelText || current.option.cancelText || 'Cancel'

    const showCancel = !!current.option.onModalCancelled || !!current.option.actionCancelText
    const showConfirm = !!current.option.onModalConfirmed || !!current.option.actionConfirmText || true

    return (
      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        {showCancel ? (
          <button
            className="p-button p-component p-button-text"
            onClick={() => current.option.onModalCancelled?.()}
            type="button"
          >
            <span className="p-button-label">{cancelText}</span>
          </button>
        ) : null}
        {showConfirm ? (
          <button
            className="p-button p-component"
            onClick={() => current.option.onModalConfirmed?.()}
            type="button"
          >
            <span className="p-button-label">{confirmText}</span>
          </button>
        ) : null}
      </div>
    )
  }, [current])

  return (
    <Dialog
      visible={!!current}
      header={current?.option?.title}
      onHide={() => current?.option?.onModalClosed?.()}
      footer={footer}
      style={{ width: current?.option?.width ? `${current.option.width}px` : '32rem' }}
      modal
    >
      {current?.option?.content_html ? (
        <div dangerouslySetInnerHTML={{ __html: current.option.content_html }} />
      ) : null}
      {current?.option?.text ? <div>{current.option.text}</div> : null}
      {typeof current?.slot_render === 'function' ? current.slot_render() : null}
    </Dialog>
  )
}
