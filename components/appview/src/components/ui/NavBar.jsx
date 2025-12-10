import React from 'react'
import { Button } from './Button'

// Mirror of Vue NavBar component from components.ts
export const NavBar = ({
  title = "",
  showHome = false,
  showBack = false,
  showPerson = false,
  onHomeClicked,
  onBackClicked,
  onPersonClicked,
  children,
  ...props
}) => {
  return (
    <div className="navbar bg-base-100 shadow-sm">
      <div className="flex-1">
        {showBack && (
          <Button
            icon="arrow_back"
            onClick={onBackClicked}
            className="btn-ghost btn-circle"
          />
        )}
        
        {title && (
          <span className="text-xl font-bold px-2">{title}</span>
        )}
        
        {children}
      </div>
      
      <div className="flex-none">
        {showHome && (
          <Button
            icon="home"
            onClick={onHomeClicked}
            className="btn-ghost btn-circle"
          />
        )}
        
        {showPerson && (
          <Button
            icon="person"
            onClick={onPersonClicked}
            className="btn-ghost btn-circle"
          />
        )}
      </div>
    </div>
  )
}

export default NavBar
