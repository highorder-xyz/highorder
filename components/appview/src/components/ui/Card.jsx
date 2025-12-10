import React from 'react'
import { Column } from './Column'

// Mirror of Vue Card component from components.ts
export const Card = ({
  title = "",
  subtitle = "",
  content = "",
  content_html = "",
  image = "",
  image_alt = "",
  actions = [],
  footer = "",
  footer_html = "",
  variant = "default", // default, outlined, elevated
  size = "normal", // small, normal, large
  className = "",
  style = {},
  children,
  ...props
}) => {
  const getVariantClass = (variant) => {
    switch (variant) {
      case 'outlined':
        return 'card-bordered'
      case 'elevated':
        return 'shadow-xl'
      default:
        return 'shadow-md'
    }
  }

  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'card-compact'
      case 'large':
        return 'card-normal'
      default:
        return 'card-normal'
    }
  }

  return (
    <div className={`card bg-base-100 ${getVariantClass()} ${getSizeClass()} ${className}`} style={style} {...props}>
      {image && (
        <figure>
          <img src={image} alt={image_alt || title} />
        </figure>
      )}
      
      <div className="card-body">
        {title && (
          <h2 className="card-title">
            {title}
            {subtitle && <span className="text-sm text-base-content/70">{subtitle}</span>}
          </h2>
        )}
        
        {content && (
          <p className="text-base-content/80">{content}</p>
        )}
        
        {content_html && (
          <div dangerouslySetInnerHTML={{ __html: content_html }} />
        )}
        
        {children}
        
        {actions.length > 0 && (
          <div className="card-actions justify-end">
            {actions.map((action, index) => (
              <button
                key={index}
                className={`btn ${action.color || 'btn-primary'} ${action.size || ''}`}
                onClick={action.onClick}
                disabled={action.disabled}
              >
                {action.text}
              </button>
            ))}
          </div>
        )}
      </div>
      
      {(footer || footer_html) && (
        <div className="card-footer">
          {footer && <p className="text-sm text-base-content/70">{footer}</p>}
          {footer_html && <div dangerouslySetInnerHTML={{ __html: footer_html }} />}
        </div>
      )}
    </div>
  )
}

export default Card
