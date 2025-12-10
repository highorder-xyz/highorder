import React from 'react'

// Mirror of Vue TextArea component from components.ts
export const TextArea = ({
  value = "",
  placeholder = "",
  disabled = false,
  readonly = false,
  required = false,
  rows = 4,
  cols = null,
  maxLength = null,
  minLength = null,
  resize = "vertical", // none, vertical, horizontal, both
  size = "normal", // small, normal, large
  status = "default", // default, success, error, warning
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
        return 'textarea-sm'
      case 'large':
        return 'textarea-lg'
      default:
        return 'textarea-md'
    }
  }

  const getStatusClass = (status) => {
    switch (status) {
      case 'success':
        return 'textarea-success'
      case 'error':
        return 'textarea-error'
      case 'warning':
        return 'textarea-warning'
      default:
        return ''
    }
  }

  const getResizeClass = (resize) => {
    switch (resize) {
      case 'none':
        return 'resize-none'
      case 'vertical':
        return 'resize-y'
      case 'horizontal':
        return 'resize-x'
      case 'both':
        return 'resize'
      default:
        return 'resize-y'
    }
  }

  const textareaProps = {
    value,
    placeholder,
    disabled,
    readOnly: readonly,
    required,
    rows,
    cols,
    maxLength,
    minLength,
    className: `textarea ${getSizeClass()} ${getStatusClass()} ${getResizeClass()} ${className}`,
    style,
    onChange,
    onInput,
    onFocus,
    onBlur,
    ...props
  }

  return <textarea {...textareaProps} />
}

export default TextArea
