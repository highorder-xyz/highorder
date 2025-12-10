import React from 'react'

// Mirror of Vue Switch component from components.ts
export const Switch = ({
  checked = false,
  disabled = false,
  label = "",
  onChange,
  onClick,
  size = "normal", // small, normal, large
  color = "primary", // primary, secondary, accent, neutral, info, success, warning, error
  className = "",
  style = {},
  ...props
}) => {
  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'toggle-sm'
      case 'large':
        return 'toggle-lg'
      default:
        return 'toggle-md'
    }
  }

  const getColorClass = (color) => {
    switch (color) {
      case 'primary':
        return 'toggle-primary'
      case 'secondary':
        return 'toggle-secondary'
      case 'accent':
        return 'toggle-accent'
      case 'neutral':
        return 'toggle-neutral'
      case 'info':
        return 'toggle-info'
      case 'success':
        return 'toggle-success'
      case 'warning':
        return 'toggle-warning'
      case 'error':
        return 'toggle-error'
      default:
        return 'toggle-primary'
    }
  }

  const handleChange = (e) => {
    if (onChange) {
      onChange(e.target.checked, e)
    }
  }

  const handleClick = (e) => {
    if (onClick) {
      onClick(e)
    }
  }

  return (
    <label className={`label cursor-pointer ${className}`} style={style} {...props}>
      <span className="label-text">{label}</span>
      <input
        type="checkbox"
        className={`toggle ${getSizeClass()} ${getColorClass()}`}
        checked={checked}
        disabled={disabled}
        onChange={handleChange}
        onClick={handleClick}
      />
    </label>
  )
}

export default Switch
