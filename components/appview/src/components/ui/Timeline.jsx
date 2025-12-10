import React from 'react'

// Mirror of Vue Timeline component from components.ts
export const Timeline = ({
  items = [],
  mode = "vertical", // vertical, horizontal
  align = "left", // left, right, alternate
  color = "primary", // primary, secondary, accent, neutral, info, success, warning, error
  size = "normal", // small, normal, large
  showDate = true,
  showTime = false,
  showIcon = true,
  className = "",
  style = {},
  ...props
}) => {
  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'timeline-sm'
      case 'large':
        return 'timeline-lg'
      default:
        return 'timeline-md'
    }
  }

  const getColorClass = (color) => {
    switch (color) {
      case 'primary':
        return 'timeline-primary'
      case 'secondary':
        return 'timeline-secondary'
      case 'accent':
        return 'timeline-accent'
      case 'neutral':
        return 'timeline-neutral'
      case 'info':
        return 'timeline-info'
      case 'success':
        return 'timeline-success'
      case 'warning':
        return 'timeline-warning'
      case 'error':
        return 'timeline-error'
      default:
        return 'timeline-primary'
    }
  }

  const formatDate = (date) => {
    if (!date) return ''
    
    const d = new Date(date)
    return d.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  }

  const formatTime = (date) => {
    if (!date || !showTime) return ''
    
    const d = new Date(date)
    return d.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getAlignClass = (index) => {
    if (mode === 'horizontal') return ''
    
    switch (align) {
      case 'right':
        return 'timeline-end'
      case 'alternate':
        return index % 2 === 0 ? 'timeline-start' : 'timeline-end'
      default:
        return 'timeline-start'
    }
  }

  const renderTimelineItem = (item, index) => {
    const isLast = index === items.length - 1
    const alignClass = getAlignClass(index)

    return (
      <li key={index} className={`timeline-item ${alignClass} ${isLast ? 'timeline-end' : ''}`}>
        {/* Timeline line */}
        {!isLast && <hr />}
        
        {/* Timeline marker */}
        <div className="timeline-marker">
          {item.icon ? (
            <span className="material-icons text-sm">{item.icon}</span>
          ) : (
            <div className={`w-4 h-4 rounded-full bg-${color} border-2 border-base-100`} />
          )}
        </div>
        
        {/* Timeline content */}
        <div className="timeline-content">
          {/* Header */}
          <div className="timeline-header">
            {item.title && (
              <h3 className="timeline-title">{item.title}</h3>
            )}
            {(showDate || showTime) && (item.date || item.time) && (
              <div className="timeline-time">
                {showDate && item.date && (
                  <span className="text-sm text-base-content/60">
                    {formatDate(item.date)}
                  </span>
                )}
                {showTime && (item.time || item.date) && (
                  <span className="text-sm text-base-content/60 ml-2">
                    {formatTime(item.time || item.date)}
                  </span>
                )}
              </div>
            )}
          </div>
          
          {/* Content */}
          {item.content && (
            <div className="timeline-description">
              {typeof item.content === 'string' ? (
                <p className="text-base-content/80">{item.content}</p>
              ) : (
                item.content
              )}
            </div>
          )}
          
          {/* Actions */}
          {item.actions && item.actions.length > 0 && (
            <div className="timeline-actions">
              {item.actions.map((action, actionIndex) => (
                <button
                  key={actionIndex}
                  className={`btn btn-sm ${action.color || 'btn-ghost'}`}
                  onClick={action.onClick}
                >
                  {action.icon && (
                    <span className="material-icons text-sm mr-1">
                      {action.icon}
                    </span>
                  )}
                  {action.text}
                </button>
              ))}
            </div>
          )}
          
          {/* Custom children */}
          {item.children}
        </div>
      </li>
    )
  }

  const timelineClasses = [
    'timeline',
    mode === 'horizontal' ? 'timeline-horizontal' : 'timeline-vertical',
    getSizeClass(size),
    getColorClass(color),
    className
  ].filter(Boolean).join(' ')

  if (mode === 'horizontal') {
    return (
      <div className={`${timelineClasses} overflow-x-auto`} style={style} {...props}>
        <ul className="timeline timeline-horizontal">
          {items.map((item, index) => renderTimelineItem(item, index))}
        </ul>
      </div>
    )
  }

  return (
    <div className={timelineClasses} style={style} {...props}>
      <ul>
        {items.map((item, index) => renderTimelineItem(item, index))}
      </ul>
    </div>
  )
}

// TimelineItem component for more flexible usage
export const TimelineItem = ({
  date,
  time,
  title,
  content,
  icon,
  actions = [],
  children,
  ...props
}) => {
  return {
    date,
    time,
    title,
    content,
    icon,
    actions,
    children,
    ...props
  }
}

export default Timeline
