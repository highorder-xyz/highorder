import React from 'react'
import { Icon } from './Icon'

// Mirror of Vue IconText component from components.ts
export const IconText = ({
  text = "",
  icon = "",
  size = 24,
  color = "currentColor",
  className = "",
  style = {},
  ...props
}) => {
  const containerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    ...style
  }

  return (
    <div className={`icon-text ${className}`} style={containerStyle} {...props}>
      {icon && (
        <Icon
          icon={icon}
          size={size}
          color={color}
        />
      )}
      <span>{text}</span>
    </div>
  )
}

export default IconText
