import React from 'react'
import { Icon } from './Icon'

// Mirror of Vue IconTitle component from components.ts
export const IconTitle = ({
  title = "",
  icon = "",
  level = 2,
  icon_size = 24,
  color = "currentColor",
  className = "",
  style = {},
  ...props
}) => {
  const getTitleClass = (level) => {
    switch (level) {
      case 1:
        return "text-4xl font-bold"
      case 2:
        return "text-3xl font-bold"
      case 3:
        return "text-2xl font-semibold"
      case 4:
        return "text-xl font-medium"
      case 5:
        return "text-lg font-medium"
      case 6:
        return "text-base font-medium"
      default:
        return "text-3xl font-bold"
    }
  }

  const TitleTag = `h${Math.min(Math.max(level, 1), 6)}`

  const containerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    ...style
  }

  return (
    <div className={`icon-title ${className}`} style={containerStyle} {...props}>
      {icon && (
        <Icon
          icon={icon}
          size={icon_size}
          color={color}
        />
      )}
      <TitleTag className={getTitleClass(level)}>
        {title}
      </TitleTag>
    </div>
  )
}

export default IconTitle
