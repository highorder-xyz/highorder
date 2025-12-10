import React from 'react'

// Mirror of Vue Badge component from components.ts
export const Badge = ({
  text = "",
  color = "primary", // primary, secondary, accent, neutral, info, success, warning, error
  variant = "filled", // filled, outline, ghost
  size = "normal", // small, normal, large
  className = "",
  style = {},
  ...props
}) => {
  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'badge-sm'
      case 'large':
        return 'badge-lg'
      default:
        return 'badge-md'
    }
  }

  const getColorClass = (color, variant) => {
    const baseClass = 'badge'
    
    switch (variant) {
      case 'outline':
        return `${baseClass} badge-outline badge-${color}`
      case 'ghost':
        return `${baseClass} badge-ghost badge-${color}`
      default:
        return `${baseClass} badge-${color}`
    }
  }

  return (
    <div 
      className={`${getColorClass(color, variant)} ${getSizeClass(size)} ${className}`}
      style={style}
      {...props}
    >
      {text}
    </div>
  )
}

export default Badge
