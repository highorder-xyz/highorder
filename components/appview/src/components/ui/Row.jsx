import React from 'react'

// Mirror of Vue Row component from components.ts
export const Row = ({
  children,
  gap = 2,
  align = "start", // start, center, end, stretch
  justify = "start", // start, center, end, between, around, evenly
  wrap = true,
  className = "",
  style = {},
  ...props
}) => {
  const getAlignClass = (align) => {
    switch (align) {
      case 'start':
        return 'items-start'
      case 'center':
        return 'items-center'
      case 'end':
        return 'items-end'
      case 'stretch':
        return 'items-stretch'
      default:
        return 'items-start'
    }
  }

  const getJustifyClass = (justify) => {
    switch (justify) {
      case 'start':
        return 'justify-start'
      case 'center':
        return 'justify-center'
      case 'end':
        return 'justify-end'
      case 'between':
        return 'justify-between'
      case 'around':
        return 'justify-around'
      case 'evenly':
        return 'justify-evenly'
      default:
        return 'justify-start'
    }
  }

  const getGapClass = (gap) => {
    const gapMap = {
      0: 'gap-0',
      1: 'gap-1',
      2: 'gap-2',
      3: 'gap-3',
      4: 'gap-4',
      5: 'gap-5'
    }
    return gapMap[gap] || 'gap-2'
  }

  const containerStyle = {
    display: 'flex',
    flexDirection: 'row',
    flexWrap: wrap ? 'wrap' : 'nowrap',
    ...style
  }

  return (
    <div 
      className={`row flex ${getAlignClass()} ${getJustifyClass()} ${getGapClass(gap)} ${className}`}
      style={containerStyle}
      {...props}
    >
      {children}
    </div>
  )
}

export default Row
