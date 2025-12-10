import React from 'react'

// Mirror of Vue Checkbox component from components.ts
export const Checkbox = ({
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
        return 'checkbox-sm'
      case 'large':
        return 'checkbox-lg'
      default:
        return 'checkbox-md'
    }
  }

  const getColorClass = (color) => {
    switch (color) {
      case 'primary':
        return 'checkbox-primary'
      case 'secondary':
        return 'checkbox-secondary'
      case 'accent':
        return 'checkbox-accent'
      case 'neutral':
        return 'checkbox-neutral'
      case 'info':
        return 'checkbox-info'
      case 'success':
        return 'checkbox-success'
      case 'warning':
        return 'checkbox-warning'
      case 'error':
        return 'checkbox-error'
      default:
        return 'checkbox-primary'
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
        className={`checkbox ${getSizeClass()} ${getColorClass()}`}
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

export default Checkbox
