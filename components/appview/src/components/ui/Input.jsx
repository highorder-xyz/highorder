import React from 'react'

// Mirror of Vue Input component from components.ts
export const Input = ({
  type = "text",
  value = "",
  placeholder = "",
  disabled = false,
  readonly = false,
  required = false,
  maxLength = null,
  minLength = null,
  pattern = "",
  size = "normal", // small, normal, large
  status = "default", // default, success, error, warning
  prefix = "",
  suffix = "",
  icon = "",
  onChange,
  onInput,
  onFocus,
  onBlur,
  className = "",
  style = {},
  ...props
}) => {
  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'input-sm'
      case 'large':
        return 'input-lg'
      default:
        return 'input-md'
    }
  }

  const getStatusClass = (status) => {
    switch (status) {
      case 'success':
        return 'input-success'
      case 'error':
        return 'input-error'
      case 'warning':
        return 'input-warning'
      default:
        return ''
    }
  }

  const inputProps = {
    type,
    value,
    placeholder,
    disabled,
    readOnly: readonly,
    required,
    maxLength,
    minLength,
    pattern,
    className: `input ${getSizeClass()} ${getStatusClass()} ${className}`,
    style,
    onChange,
    onInput,
    onFocus,
    onBlur,
    ...props
  }

  const renderInput = () => {
    if (prefix || suffix || icon) {
      return (
        <div className="input-group">
          {prefix && <span>{prefix}</span>}
          {icon && <span className="material-icons">{icon}</span>}
          <input {...inputProps} />
          {suffix && <span>{suffix}</span>}
        </div>
      )
    }

    return <input {...inputProps} />
  }

  return renderInput()
}

export default Input
