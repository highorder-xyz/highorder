import React from 'react'
import { Button } from './Button'

// Mirror of Vue Link component from components.ts
export const Link = ({
  text = "",
  open_mode = "new", // new, self
  target_url = "",
  onClick,
  ...props
}) => {
  const handleClick = (e) => {
    if (onClick) {
      onClick(target_url, open_mode)
    }
  }

  return (
    <Button
      text={text}
      onClick={handleClick}
      className="btn-link"
      {...props}
    />
  )
}

export default Link
