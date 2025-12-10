import React from 'react'

// Mirror of Vue List component from components.ts
export const List = ({
  items = [],
  variant = "default", // default, hover, clickable
  size = "normal", // small, normal, large
  avatar = false,
  icon = false,
  image = false,
  density = "normal", // compact, normal, comfortable
  className = "",
  style = {},
  onItemClick,
  ...props
}) => {
  const getVariantClass = (variant) => {
    switch (variant) {
      case 'hover':
        return 'list-hover'
      case 'clickable':
        return 'list-clickable'
      default:
        return ''
    }
  }

  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'list-sm'
      case 'large':
        return 'list-lg'
      default:
        return 'list-md'
    }
  }

  const getDensityClass = (density) => {
    switch (density) {
      case 'compact':
        return 'list-compact'
      case 'comfortable':
        return 'list-comfortable'
      default:
        return ''
    }
  }

  const handleItemClick = (item, index) => {
    if (onItemClick && variant !== 'default') {
      onItemClick(item, index)
    }
  }

  const renderListItem = (item, index) => {
    const isClickable = variant === 'clickable'
    
    return (
      <li 
        key={index}
        className={isClickable ? 'cursor-pointer' : ''}
        onClick={() => handleItemClick(item, index)}
      >
        <div className="list-item">
          {avatar && item.avatar && (
            <div className="list-item-avatar">
              <img src={item.avatar} alt={item.title || ''} />
            </div>
          )}
          
          {icon && item.icon && (
            <div className="list-item-icon">
              <span className="material-icons">{item.icon}</span>
            </div>
          )}
          
          {image && item.image && (
            <div className="list-item-image">
              <img src={item.image} alt={item.title || ''} />
            </div>
          )}
          
          <div className="list-item-content">
            {item.title && (
              <div className="list-item-title">{item.title}</div>
            )}
            {item.subtitle && (
              <div className="list-item-subtitle">{item.subtitle}</div>
            )}
            {item.description && (
              <div className="list-item-description">{item.description}</div>
            )}
          </div>
          
          {item.badge && (
            <div className="list-item-badge">
              <span className="badge badge-sm">{item.badge}</span>
            </div>
          )}
          
          {item.actions && (
            <div className="list-item-actions">
              {item.actions.map((action, actionIndex) => (
                <button
                  key={actionIndex}
                  className="btn btn-sm btn-ghost"
                  onClick={(e) => {
                    e.stopPropagation()
                    if (action.onClick) {
                      action.onClick(item, index)
                    }
                  }}
                >
                  {action.icon ? (
                    <span className="material-icons">{action.icon}</span>
                  ) : (
                    action.text
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </li>
    )
  }

  return (
    <ul 
      className={`menu ${getVariantClass()} ${getSizeClass()} ${getDensityClass()} ${className}`}
      style={style}
      {...props}
    >
      {items.map((item, index) => renderListItem(item, index))}
    </ul>
  )
}

export default List
