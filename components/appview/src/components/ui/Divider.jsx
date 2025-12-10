import React from 'react'

// Mirror of Vue Divider component from components.ts
export const Divider = ({
  widthHint = 100,
  orientation = "horizontal", // horizontal, vertical
  ...props
}) => {
  if (orientation === "vertical") {
    return (
      <div className="divider divider-vertical" />
    )
  }

  return (
    <div className="divider" />
  )
}

export default Divider
