import React from 'react'

// Mirror of Vue Select component from components.ts
export const Select = ({
  value = "",
  options = [],
  placeholder = "请选择",
  disabled = false,
  readonly = false,
  required = false,
  size = "normal", // small, normal, large
  status = "default", // default, success, error, warning
  multiple = false,
  onChange,
  onFocus,
  onBlur,
  className = "",
  style = {},
  ...props
}) => {
  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'select-sm'
      case 'large':
        return 'select-lg'
      default:
        return 'select-md'
    }
  }

  const getStatusClass = (status) => {
    switch (status) {
      case 'success':
        return 'select-success'
      case 'error':
        return 'select-error'
      case 'warning':
        return 'select-warning'
      default:
        return ''
    }
  }

  const handleChange = (e) => {
    if (onChange) {
      if (multiple) {
        const selectedValues = Array.from(e.target.selectedOptions, option => option.value)
        onChange(selectedValues, e)
      } else {
        onChange(e.target.value, e)
      }
    }
  }

  const renderOptions = () => {
    return options.map((option, index) => {
      if (typeof option === 'string') {
        return (
          <option key={index} value={option}>
            {option}
          </option>
        )
      } else {
        return (
          <option key={index} value={option.value} disabled={option.disabled}>
            {option.label}
          </option>
        )
      }
    })
  }

  return (
    <select
      className={`select ${getSizeClass()} ${getStatusClass()} ${className}`}
      style={style}
      value={value}
      disabled={disabled}
      readOnly={readonly}
      required={required}
      multiple={multiple}
      onChange={handleChange}
      onFocus={onFocus}
      onBlur={onBlur}
      {...props}
    >
      {!multiple && placeholder && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      {renderOptions()}
    </select>
  )
}

export default Select
