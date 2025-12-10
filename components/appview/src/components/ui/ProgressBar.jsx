import React from 'react'

// Mirror of Vue ProgressBar component from components.ts
export const ProgressBar = ({
  value = 0,
  max = 100,
  showText = true,
  color = "primary", // primary, secondary, accent, neutral, info, success, warning, error
  size = "normal", // normal, large, small
  className = "",
  style = {},
  ...props
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)
  
  const getSizeClass = (size) => {
    switch (size) {
      case 'large':
        return 'progress-lg'
      case 'small':
        return 'progress-sm'
      default:
        return ''
    }
  }

  const getColorClass = (color) => {
    switch (color) {
      case 'primary':
        return 'progress-primary'
      case 'secondary':
        return 'progress-secondary'
      case 'accent':
        return 'progress-accent'
      case 'neutral':
        return 'progress-neutral'
      case 'info':
        return 'progress-info'
      case 'success':
        return 'progress-success'
      case 'warning':
        return 'progress-warning'
      case 'error':
        return 'progress-error'
      default:
        return 'progress-primary'
    }
  }

  return (
    <div className={`progress ${getSizeClass()} ${getColorClass()} ${className}`} style={style} {...props}>
      <div 
        className="progress-bar"
        style={{ width: `${percentage}%` }}
      />
      {showText && (
        <div className="text-center mt-1 text-sm text-base-content/70">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  )
}

export default ProgressBar
