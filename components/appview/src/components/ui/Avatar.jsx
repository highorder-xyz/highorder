import React from 'react'

// Mirror of Vue Avatar component from components.ts
export const Avatar = ({
  src = "",
  alt = "",
  size = "normal", // small, normal, large, xlarge
  shape = "circle", // circle, square, rounded
  status = "", // online, offline, away, busy
  badge = "",
  badgeColor = "primary",
  className = "",
  style = {},
  ...props
}) => {
  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'avatar-sm'
      case 'large':
        return 'avatar-lg'
      case 'xlarge':
        return 'avatar-xl'
      default:
        return 'avatar-md'
    }
  }

  const getShapeClass = (shape) => {
    switch (shape) {
      case 'square':
        return 'avatar-square'
      case 'rounded':
        return 'avatar-rounded'
      default:
        return 'avatar-circle'
    }
  }

  const getStatusClass = (status) => {
    switch (status) {
      case 'online':
        return 'avatar-online'
      case 'offline':
        return 'avatar-offline'
      case 'away':
        return 'avatar-away'
      case 'busy':
        return 'avatar-busy'
      default:
        return ''
    }
  }

  const getBadgeColorClass = (badgeColor) => {
    switch (badgeColor) {
      case 'primary':
        return 'badge-primary'
      case 'secondary':
        return 'badge-secondary'
      case 'accent':
        return 'badge-accent'
      case 'neutral':
        return 'badge-neutral'
      case 'info':
        return 'badge-info'
      case 'success':
        return 'badge-success'
      case 'warning':
        return 'badge-warning'
      case 'error':
        return 'badge-error'
      default:
        return 'badge-primary'
    }
  }

  return (
    <div 
      className={`avatar ${getSizeClass()} ${getShapeClass()} ${getStatusClass()} ${className}`}
      style={style}
      {...props}
    >
      <div className="w-24 rounded-full">
        {src ? (
          <img src={src} alt={alt} />
        ) : (
          <div className="bg-neutral text-neutral-content rounded-full w-24 flex items-center justify-center">
            <span className="text-xl">{alt || '?'}</span>
          </div>
        )}
      </div>
      
      {status && (
        <div className={`absolute bottom-0 right-0 w-6 h-6 rounded-full ${getStatusClass(status)} border-2 border-base-100`} />
      )}
      
      {badge && (
        <div className={`absolute -top-1 -right-1 w-6 h-6 rounded-full ${getBadgeColorClass(badgeColor)} flex items-center justify-center text-xs text-white`}>
          {badge}
        </div>
      )}
    </div>
  )
}

export default Avatar
