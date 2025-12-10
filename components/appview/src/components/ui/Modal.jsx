import React from 'react'
import { Button } from './Button'

// Mirror of Vue Modal component from components.ts
export const Modal = ({
  show = false,
  title = "",
  text = "",
  content_html = "",
  actions = [],
  actionsVertical = false,
  actionConfirmText = "",
  actionCancelText = "",
  onModalConfirmed,
  onModalCancelled,
  onModalClosed,
  children,
  ...props
}) => {
  if (!show) return null

  const handleConfirm = () => {
    if (onModalConfirmed) onModalConfirmed()
    if (onModalClosed) onModalClosed()
  }

  const handleCancel = () => {
    if (onModalCancelled) onModalCancelled()
    if (onModalClosed) onModalClosed()
  }

  const renderActions = () => {
    const allActions = [...actions]
    
    if (actionConfirmText) {
      allActions.push({
        text: actionConfirmText,
        onClick: handleConfirm,
        color: 'primary'
      })
    }
    
    if (actionCancelText) {
      allActions.push({
        text: actionCancelText,
        onClick: handleCancel,
        color: 'secondary'
      })
    }

    if (allActions.length === 0) {
      allActions.push({
        text: "点击这里关闭",
        onClick: handleCancel
      })
    }

    return (
      <div className={`flex ${actionsVertical ? 'flex-col' : 'flex-row'} gap-2 justify-center`}>
        {allActions.map((action, index) => (
          <Button
            key={index}
            text={action.text}
            color={action.color || 'surface'}
            onClick={action.onClick}
            {...action.props}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="modal modal-open">
      <div className="modal-box">
        {title && (
          <h3 className="font-bold text-lg mb-4">{title}</h3>
        )}
        
        {text && (
          <p className="py-4 whitespace-pre-wrap">{text}</p>
        )}
        
        {content_html && (
          <div 
            className="py-4"
            dangerouslySetInnerHTML={{ __html: content_html }}
          />
        )}
        
        {children && (
          <div className="py-4">
            {children}
          </div>
        )}
        
        <div className="modal-action">
          {renderActions()}
        </div>
      </div>
      
      <div 
        className="modal-backdrop"
        onClick={handleCancel}
      >
        <span>close</span>
      </div>
    </div>
  )
}

export default Modal
