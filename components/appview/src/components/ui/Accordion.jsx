import React from 'react'

// Mirror of Vue Accordion component from components.ts
export const Accordion = ({
  items = [],
  allowMultiple = false,
  defaultOpen = [],
  size = "normal", // small, normal, large
  variant = "default", // default, bordered, ghost
  onChange,
  className = "",
  style = {},
  ...props
}) => {
  const [openItems, setOpenItems] = React.useState(defaultOpen)

  const handleToggle = (index) => {
    let newOpenItems
    
    if (allowMultiple) {
      if (openItems.includes(index)) {
        newOpenItems = openItems.filter(i => i !== index)
      } else {
        newOpenItems = [...openItems, index]
      }
    } else {
      newOpenItems = openItems.includes(index) ? [] : [index]
    }
    
    setOpenItems(newOpenItems)
    if (onChange) {
      onChange(newOpenItems, index)
    }
  }

  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'collapse-sm'
      case 'large':
        return 'collapse-lg'
      default:
        return 'collapse-md'
    }
  }

  const getVariantClass = (variant) => {
    switch (variant) {
      case 'bordered':
        return 'collapse-border'
      case 'ghost':
        return 'collapse-ghost'
      default:
        return ''
    }
  }

  return (
    <div className={`accordion ${getSizeClass()} ${getVariantClass()} ${className}`} style={style} {...props}>
      {items.map((item, index) => (
        <div key={index} className={`collapse ${getSizeClass()} ${getVariantClass()}`}>
          <input 
            type="checkbox" 
            checked={openItems.includes(index)}
            onChange={() => handleToggle(index)}
          />
          <div className="collapse-title text-xl font-medium">
            {item.icon && (
              <span className="material-icons mr-2">{item.icon}</span>
            )}
            {item.title}
          </div>
          <div className="collapse-content">
            {item.content && (
              <p className="text-base-content/80">{item.content}</p>
            )}
            {item.content_html && (
              <div dangerouslySetInnerHTML={{ __html: item.content_html }} />
            )}
            {item.children}
          </div>
        </div>
      ))}
    </div>
  )
}

export default Accordion
