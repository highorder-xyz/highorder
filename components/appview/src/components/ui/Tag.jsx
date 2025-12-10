import React from 'react'

// Mirror of Vue Tag component from components.ts
export const Tag = ({
  text = "",
  color = "primary", // primary, secondary, accent, neutral, info, success, warning, error
  variant = "filled", // filled, outline, ghost
  size = "normal", // small, normal, large
  closable = false,
  onClose,
  className = "",
  style = {},
  ...props
}) => {
  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'tag-sm'
      case 'large':
        return 'tag-lg'
      default:
        return 'tag-md'
    }
  }

  const getColorClass = (color, variant) => {
    const baseClass = 'tag'
    
    switch (variant) {
      case 'outline':
        return `${baseClass} tag-outline tag-${color}`
      case 'ghost':
        return `${baseClass} tag-ghost tag-${color}`
      default:
        return `${baseClass} tag-${color}`
    }
  }

  const handleClose = (e) => {
    e.stopPropagation()
    if (onClose) {
      onClose(e)
    }
  }

  return (
    <span 
      className={`${getColorClass(color, variant)} ${getSizeClass(size)} ${className}`}
      style={style}
      {...props}
    >
      {text}
      {closable && (
        <button
          className="tag-remove"
          onClick={handleClose}
          aria-label="Remove tag"
        >
          ×
        </button>
      )}
    </span>
  )
}

export default Tag
