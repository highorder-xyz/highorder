import React from 'react'

// Mirror of Vue Radio component from components.ts
export const Radio = ({
  checked = false,
  disabled = false,
  label = "",
  value = "",
  name = "",
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
        return 'radio-sm'
      case 'large':
        return 'radio-lg'
      default:
        return 'radio-md'
    }
  }

  const getColorClass = (color) => {
    switch (color) {
      case 'primary':
        return 'radio-primary'
      case 'secondary':
        return 'radio-secondary'
      case 'accent':
        return 'radio-accent'
      case 'neutral':
        return 'radio-neutral'
      case 'info':
        return 'radio-info'
      case 'success':
        return 'radio-success'
      case 'warning':
        return 'radio-warning'
      case 'error':
        return 'radio-error'
      default:
        return 'radio-primary'
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
        type="radio"
        className={`radio ${getSizeClass()} ${getColorClass()}`}
        checked={checked}
        disabled={disabled}
        value={value}
        name={name}
        onChange={handleChange}
        onClick={handleClick}
      />
    </label>
  )
}

export default Radio
