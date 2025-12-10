import React from 'react'

// Mirror of Vue Breadcrumb component from components.ts
export const Breadcrumb = ({
  items = [],
  separator = "/", // "/", ">", "→", "»"
  className = "",
  style = {},
  ...props
}) => {
  const getSeparatorIcon = (separator) => {
    switch (separator) {
      case '>':
        return 'chevron_right'
      case '→':
        return 'arrow_forward'
      case '»':
        return 'chevron_right'
      default:
        return '/'
    }
  }

  const renderSeparator = (index) => {
    const isIcon = typeof getSeparatorIcon(separator) === 'string' && !['/', '>', '→', '»'].includes(separator)
    
    if (isIcon) {
      return (
        <span className="material-icons text-base-content/50 mx-2" style={{ fontSize: '16px' }}>
          {getSeparatorIcon(separator)}
        </span>
      )
    }
    
    return (
      <span className="text-base-content/50 mx-2">
        {separator}
      </span>
    )
  }

  return (
    <nav 
      className={`breadcrumbs text-sm ${className}`}
      style={style}
      {...props}
    >
      <ul>
        {items.map((item, index) => (
          <li key={index}>
            {item.href ? (
              <a 
                href={item.href}
                onClick={item.onClick}
                className={item.disabled ? 'cursor-not-allowed opacity-50' : ''}
              >
                {item.icon && (
                  <span className="material-icons mr-1" style={{ fontSize: '16px' }}>
                    {item.icon}
                  </span>
                )}
                {item.label}
              </a>
            ) : (
              <span className={item.active ? 'font-medium' : ''}>
                {item.icon && (
                  <span className="material-icons mr-1" style={{ fontSize: '16px' }}>
                    {item.icon}
                  </span>
                )}
                {item.label}
              </span>
            )}
          </li>
        ))}
      </ul>
    </nav>
  )
}

export default Breadcrumb
