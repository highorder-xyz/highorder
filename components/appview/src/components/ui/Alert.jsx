import React from 'react'

// Mirror of Vue Alert component from components.ts
export const Alert = ({
  message = "",
  header = "",
  show = false,
  severity = "info", // info, success, warning, error
  position = "top", // top, bottom
  duration = 3000,
  onHide,
  ...props
}) => {
  React.useEffect(() => {
    if (show && duration > 0) {
      const timer = setTimeout(() => {
        if (onHide) onHide()
      }, duration)
      
      return () => clearTimeout(timer)
    }
  }, [show, duration, onHide])

  if (!show) return null

  const getAlertClass = () => {
    const baseClass = "alert"
    switch (severity) {
      case 'success':
        return `${baseClass} alert-success`
      case 'warning':
        return `${baseClass} alert-warning`
      case 'error':
        return `${baseClass} alert-error`
      default:
        return `${baseClass} alert-info`
    }
  }

  const getPositionClass = () => {
    switch (position) {
      case 'top':
        return "fixed top-4 left-1/2 transform -translate-x-1/2 z-50"
      case 'bottom':
        return "fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50"
      default:
        return "fixed top-4 left-1/2 transform -translate-x-1/2 z-50"
    }
  }

  return (
    <div className={`${getAlertClass()} ${getPositionClass()} shadow-lg`}>
      {header && <span className="font-bold">{header}: </span>}
      <span>{message}</span>
      <div>
        <button 
          className="btn btn-sm btn-ghost btn-circle"
          onClick={onHide}
        >
          ✕
        </button>
      </div>
    </div>
  )
}

export default Alert
