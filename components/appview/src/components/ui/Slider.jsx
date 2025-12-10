import React from 'react'

// Mirror of Vue Slider component from components.ts
export const Slider = ({
  value = 0,
  min = 0,
  max = 100,
  step = 1,
  disabled = false,
  showTooltip = true,
  showValue = true,
  vertical = false,
  range = false,
  marks = [],
  color = "primary", // primary, secondary, accent, neutral, info, success, warning, error
  size = "normal", // small, normal, large
  onChange,
  onChangeComplete,
  className = "",
  style = {},
  ...props
}) => {
  const [internalValue, setInternalValue] = React.useState(value)
  const [isDragging, setIsDragging] = React.useState(false)
  const sliderRef = React.useRef(null)

  React.useEffect(() => {
    setInternalValue(value)
  }, [value])

  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'range-sm'
      case 'large':
        return 'range-lg'
      default:
        return 'range-md'
    }
  }

  const getColorClass = (color) => {
    switch (color) {
      case 'primary':
        return 'range-primary'
      case 'secondary':
        return 'range-secondary'
      case 'accent':
        return 'range-accent'
      case 'neutral':
        return 'range-neutral'
      case 'info':
        return 'range-info'
      case 'success':
        return 'range-success'
      case 'warning':
        return 'range-warning'
      case 'error':
        return 'range-error'
      default:
        return 'range-primary'
    }
  }

  const getPercentage = (val) => {
    return ((val - min) / (max - min)) * 100
  }

  const getValueFromPercentage = (percentage) => {
    return min + (percentage / 100) * (max - min)
  }

  const handleChange = (e) => {
    const newValue = parseFloat(e.target.value)
    setInternalValue(newValue)
    
    if (onChange && !isDragging) {
      onChange(newValue)
    }
  }

  const handleMouseDown = () => {
    setIsDragging(true)
  }

  const handleMouseUp = () => {
    setIsDragging(false)
    if (onChangeComplete) {
      onChangeComplete(internalValue)
    }
  }

  const handleClick = (e) => {
    if (disabled || !sliderRef.current) return
    
    const rect = sliderRef.current.getBoundingClientRect()
    const percentage = vertical 
      ? ((rect.bottom - e.clientY) / rect.height) * 100
      : ((e.clientX - rect.left) / rect.width) * 100
    
    const newValue = Math.round(getValueFromPercentage(percentage) / step) * step
    const clampedValue = Math.max(min, Math.min(max, newValue))
    
    setInternalValue(clampedValue)
    if (onChange) {
      onChange(clampedValue)
    }
    if (onChangeComplete) {
      onChangeComplete(clampedValue)
    }
  }

  const renderMarks = () => {
    if (!marks.length) return null
    
    return (
      <div className={`flex ${vertical ? 'flex-col' : 'justify-between'} w-full mt-2`}>
        {marks.map((mark, index) => (
          <div 
            key={index}
            className={`flex ${vertical ? 'flex-col' : 'flex-col'} items-center`}
          >
            <div 
              className={`w-1 h-1 bg-base-content/50 rounded-full`}
              style={{
                [vertical ? 'height' : 'width']: '4px'
              }}
            />
            <span className="text-xs text-base-content/60 mt-1">{mark}</span>
          </div>
        ))}
      </div>
    )
  }

  const sliderClasses = [
    'range',
    getSizeClass(size),
    getColorClass(color),
    disabled ? 'range-disabled' : '',
    vertical ? 'rotate-90' : '',
    className
  ].filter(Boolean).join(' ')

  return (
    <div 
      className={`slider-container ${className}`} 
      style={style}
      {...props}
    >
      <div className="flex items-center gap-4">
        {showValue && (
          <div className="text-sm font-medium min-w-[3rem]">
            {internalValue}
          </div>
        )}
        
        <div className="flex-1">
          <input
            ref={sliderRef}
            type="range"
            min={min}
            max={max}
            step={step}
            value={internalValue}
            disabled={disabled}
            className={sliderClasses}
            onChange={handleChange}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            onClick={handleClick}
          />
          
          {renderMarks()}
        </div>
      </div>
      
      {showTooltip && !disabled && (
        <div 
          className="tooltip tooltip-primary"
          data-tip={`当前值: ${internalValue}`}
        >
          <div 
            className="absolute w-4 h-4 bg-primary rounded-full -top-2 transition-all duration-150"
            style={{
              left: `${getPercentage(internalValue)}%`,
              transform: 'translateX(-50%)'
            }}
          />
        </div>
      )}
    </div>
  )
}

export default Slider
