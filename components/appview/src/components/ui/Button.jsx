import React from 'react'

// Mirror of Vue Button component from components.ts
export const Button = ({
  text = "",
  icon = "",
  href = "",
  open_new = false,
  sub_text = "",
  disable = false,
  disable_text = "",
  style = {},
  color = "surface",
  size_hint = true,
  h_size = 3,
  v_size = 3,
  text_size = 3,
  icon_size = 3,
  icon_pos = "left",
  onClick,
  children,
  ...props
}) => {
  const getSizeName = (size) => {
    const names = ['xxlarge', 'xlarge', 'large', 'medium', 'small', 'xsmall', 'xxsmall']
    if (size < 0 || size > 6) return ''
    return names[size] || ''
  }

  const getSizeRatio = (size) => {
    const sizeRatio = {
      0: 1.95, 1: 1.56, 2: 1.25, 3: 1,
      4: 0.8, 5: 0.64, 6: 0.51
    }
    const clampedSize = Math.max(0, Math.min(6, size))
    return sizeRatio[clampedSize] || 1
  }

  const iconSize = 24 * getSizeRatio(text_size)

  const baseClasses = [
    "btn",
    color === "primary" ? "btn-primary" : "",
    size_hint ? `btn-${getSizeName(v_size)}` : "",
    icon_pos === "top" || icon_pos === "bottom" ? "btn-block" : "",
    disable ? "btn-disabled" : ""
  ].filter(Boolean).join(" ")

  const handleClick = (e) => {
    if (disable) return
    if (onClick) onClick(e)
  }

  const renderIcon = () => {
    if (!icon) return null
    
    if (icon.includes('/') || icon.includes('.')) {
      // Image icon
      return <img 
        src={icon} 
        style={{ maxHeight: `${iconSize}px`, maxWidth: "100%" }} 
        alt="icon" 
      />
    } else {
      // Text/icon class
      return <span className="material-icons" style={{ fontSize: iconSize }}>{icon}</span>
    }
  }

  const renderContent = () => {
    const content = []
    
    if (icon && (icon_pos === "left" || icon_pos === "top")) {
      content.push(renderIcon())
    }
    
    if (text) {
      content.push(<span key="text">{text}</span>)
    }
    
    if (children) {
      content.push(children)
    }
    
    if (icon && (icon_pos === "right" || icon_pos === "bottom")) {
      content.push(renderIcon())
    }
    
    return content
  }

  const buttonContent = (
    <button
      className={baseClasses}
      disabled={disable}
      onClick={handleClick}
      {...props}
    >
      {renderContent()}
    </button>
  )

  if (href) {
    return (
      <a 
        href={href} 
        target={open_new ? '_blank' : '_self'}
        onClick={(e) => {
          if (disable) e.preventDefault()
        }}
      >
        {buttonContent}
      </a>
    )
  }

  return buttonContent
}

export default Button
