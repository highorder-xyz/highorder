import React from 'react'

// Mirror of Vue Dropdown component from components.ts
export const Dropdown = ({
  trigger = "hover", // hover, click
  placement = "bottom", // top, bottom, left, right
  disabled = false,
  children,
  className = "",
  style = {},
  ...props
}) => {
  const [isOpen, setIsOpen] = React.useState(false)
  const dropdownRef = React.useRef(null)

  const getPlacementClass = (placement) => {
    switch (placement) {
      case 'top':
        return 'dropdown-top'
      case 'bottom':
        return 'dropdown-bottom'
      case 'left':
        return 'dropdown-left'
      case 'right':
        return 'dropdown-right'
      default:
        return 'dropdown-bottom'
    }
  }

  const handleToggle = () => {
    if (!disabled) {
      setIsOpen(!isOpen)
    }
  }

  const handleMouseEnter = () => {
    if (trigger === 'hover' && !disabled) {
      setIsOpen(true)
    }
  }

  const handleMouseLeave = () => {
    if (trigger === 'hover' && !disabled) {
      setIsOpen(false)
    }
  }

  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const childrenArray = React.Children.toArray(children)
  const triggerElement = childrenArray[0]
  const dropdownContent = childrenArray.slice(1)

  return (
    <div 
      ref={dropdownRef}
      className={`dropdown ${getPlacementClass(placement)} ${className}`}
      style={style}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      {...props}
    >
      <div 
        tabIndex={0}
        role="button"
        onClick={trigger === 'click' ? handleToggle : undefined}
        className={disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
      >
        {triggerElement}
      </div>
      
      {isOpen && (
        <ul 
          tabIndex={0} 
          className="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52"
        >
          {dropdownContent}
        </ul>
      )}
    </div>
  )
}

export default Dropdown
