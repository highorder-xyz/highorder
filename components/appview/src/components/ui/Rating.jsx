import React from 'react'

// Mirror of Vue Rating component from components.ts
export const Rating = ({
  value = 0,
  max = 5,
  disabled = false,
  readonly = false,
  allowHalf = false,
  showValue = true,
  size = "normal", // small, normal, large
  color = "primary", // primary, secondary, accent, neutral, info, success, warning, error
  onChange,
  onHoverChange,
  className = "",
  style = {},
  ...props
}) => {
  const [hoverValue, setHoverValue] = React.useState(0)
  const [isHovering, setIsHovering] = React.useState(false)

  React.useEffect(() => {
    if (!isHovering) {
      setHoverValue(value)
    }
  }, [value, isHovering])

  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'rating-sm'
      case 'large':
        return 'rating-lg'
      default:
        return 'rating-md'
    }
  }

  const getColorClass = (color) => {
    switch (color) {
      case 'primary':
        return 'rating-primary'
      case 'secondary':
        return 'rating-secondary'
      case 'accent':
        return 'rating-accent'
      case 'neutral':
        return 'rating-neutral'
      case 'info':
        return 'rating-info'
      case 'success':
        return 'rating-success'
      case 'warning':
        return 'rating-warning'
      case 'error':
        return 'rating-error'
      default:
        return 'rating-primary'
    }
  }

  const handleMouseEnter = (index) => {
    if (disabled || readonly) return
    
    setIsHovering(true)
    setHoverValue(index + 1)
    if (onHoverChange) {
      onHoverChange(index + 1)
    }
  }

  const handleMouseLeave = () => {
    if (disabled || readonly) return
    
    setIsHovering(false)
    setHoverValue(value)
  }

  const handleClick = (index) => {
    if (disabled || readonly) return
    
    const newValue = index + 1
    setHoverValue(newValue)
    if (onChange) {
      onChange(newValue)
    }
  }

  const renderStar = (index) => {
    const currentValue = isHovering ? hoverValue : value
    const isFilled = index < currentValue
    const isHalfFilled = allowHalf && index < currentValue - 0.5 && index >= currentValue - 1
    
    const starClasses = [
      'mask mask-star-2',
      getColorClass(color),
      isFilled ? 'bg-current' : 'bg-base-300',
      disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'
    ].filter(Boolean).join(' ')

    return (
      <div
        key={index}
        className="mask mask-star-2 bg-current"
        style={{
          width: '20px',
          height: '20px'
        }}
        onMouseEnter={() => handleMouseEnter(index)}
        onMouseLeave={handleMouseLeave}
        onClick={() => handleClick(index)}
      >
        <div 
          className={`w-full h-full ${isFilled ? 'bg-current' : 'bg-base-300'}`}
          style={{
            clipPath: isHalfFilled 
              ? 'polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)'
              : undefined
          }}
        />
      </div>
    )
  }

  const renderStars = () => {
    const stars = []
    for (let i = 0; i < max; i++) {
      stars.push(renderStar(i))
    }
    return stars
  }

  return (
    <div 
      className={`rating ${getSizeClass()} ${getColorClass()} ${className}`}
      style={style}
      {...props}
    >
      {renderStars()}
      {showValue && (
        <span className="ml-2 text-sm text-base-content/60">
          ({isHovering ? hoverValue : value})
        </span>
      )}
    </div>
  )
}

export default Rating
