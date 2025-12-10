import React from 'react'

// Mirror of Vue Icon component from components.ts
export const Icon = ({
  icon = "",
  size = 24,
  color = "currentColor",
  className = "",
  style = {},
  ...props
}) => {
  const iconStyle = {
    width: size,
    height: size,
    color,
    ...style
  }

  // Check if it's an image URL
  if (icon.includes('/') || icon.includes('.') || icon.startsWith('data:')) {
    return (
      <img
        src={icon}
        alt="icon"
        style={iconStyle}
        className={className}
        {...props}
      />
    )
  }

  // Check if it's a CSS class (like material-icons)
  if (icon.includes(' ') || icon.includes('-')) {
    return (
      <i
        className={`${icon} ${className}`}
        style={iconStyle}
        {...props}
      />
    )
  }

  // Default to material icon
  return (
    <span
      className={`material-icons ${className}`}
      style={iconStyle}
      {...props}
    >
      {icon}
    </span>
  )
}

export default Icon
