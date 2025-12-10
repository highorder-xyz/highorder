import React from 'react'

// Mirror of Vue Tooltip component from components.ts
export const Tooltip = ({
  text = "",
  placement = "top", // top, bottom, left, right
  trigger = "hover", // hover, click, focus
  disabled = false,
  delay = 0,
  children,
  className = "",
  style = {},
  ...props
}) => {
  const [isVisible, setIsVisible] = React.useState(false)
  const [showTooltip, setShowTooltip] = React.useState(false)
  const timeoutRef = React.useRef(null)
  const tooltipRef = React.useRef(null)

  const getPlacementClass = (placement) => {
    switch (placement) {
      case 'top':
        return 'tooltip-top'
      case 'bottom':
        return 'tooltip-bottom'
      case 'left':
        return 'tooltip-left'
      case 'right':
        return 'tooltip-right'
      default:
        return 'tooltip-top'
    }
  }

  const handleMouseEnter = () => {
    if (trigger === 'hover' && !disabled) {
      if (delay > 0) {
        timeoutRef.current = setTimeout(() => {
          setIsVisible(true)
          setShowTooltip(true)
        }, delay)
      } else {
        setIsVisible(true)
        setShowTooltip(true)
      }
    }
  }

  const handleMouseLeave = () => {
    if (trigger === 'hover' && !disabled) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
      setIsVisible(false)
      setTimeout(() => setShowTooltip(false), 150)
    }
  }

  const handleClick = () => {
    if (trigger === 'click' && !disabled) {
      setIsVisible(!isVisible)
      setShowTooltip(!isVisible)
    }
  }

  const handleFocus = () => {
    if (trigger === 'focus' && !disabled) {
      setIsVisible(true)
      setShowTooltip(true)
    }
  }

  const handleBlur = () => {
    if (trigger === 'focus' && !disabled) {
      setIsVisible(false)
      setTimeout(() => setShowTooltip(false), 150)
    }
  }

  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  const childrenArray = React.Children.toArray(children)
  const triggerElement = childrenArray[0]

  return (
    <div 
      className={`tooltip ${getPlacementClass(placement)} ${className}`}
      style={style}
      {...props}
    >
      <div
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        onFocus={handleFocus}
        onBlur={handleBlur}
      >
        {triggerElement}
      </div>
      
      {showTooltip && text && (
        <div ref={tooltipRef} className="tooltip-box">
          {text}
        </div>
      )}
    </div>
  )
}

export default Tooltip
