import React from 'react'

// Mirror of Vue Paragraph component from components.ts
export const Paragraph = ({
  text = "",
  align = "start", // start, center, end
  isRich = true,
  ...props
}) => {
  const getAlignClass = (align) => {
    switch (align) {
      case 'start':
        return 'text-left'
      case 'center':
        return 'text-center'
      case 'end':
        return 'text-right'
      default:
        return 'text-left'
    }
  }

  if (isRich) {
    // For now, treat as plain text - can be enhanced with rich text parsing later
    const lines = text.split('\n')
    return (
      <div className={`paragraph ${getAlignClass(align)}`}>
        {lines.map((line, index) => (
          line.trim() && (
            <p key={index} className="mb-2 last:mb-0">
              {line}
            </p>
          )
        ))}
      </div>
    )
  } else {
    const lines = text.split('\n')
    return (
      <div className={`paragraph ${getAlignClass(align)}`}>
        {lines.map((line, index) => (
          <div key={index}>
            {line}
          </div>
        ))}
      </div>
    )
  }
}

export default Paragraph
