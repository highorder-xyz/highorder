import React from 'react'

// Mirror of Vue Menu component from components.ts
export const Menu = ({
  items = [],
  mode = "vertical", // vertical, horizontal, inline
  theme = "light", // light, dark
  collapsed = false,
  accordion = false,
  openKeys = [],
  selectedKeys = [],
  onOpenChange,
  onSelect,
  className = "",
  style = {},
  ...props
}) => {
  const [internalOpenKeys, setInternalOpenKeys] = React.useState(openKeys)
  const [internalSelectedKeys, setInternalSelectedKeys] = React.useState(selectedKeys)

  React.useEffect(() => {
    setInternalOpenKeys(openKeys)
  }, [openKeys])

  React.useEffect(() => {
    setInternalSelectedKeys(selectedKeys)
  }, [selectedKeys])

  const handleOpenChange = (keys) => {
    setInternalOpenKeys(keys)
    if (onOpenChange) {
      onOpenChange(keys)
    }
  }

  const handleSelect = (key, item) => {
    setInternalSelectedKeys([key])
    if (onSelect) {
      onSelect(key, item)
    }
  }

  const handleSubMenuClick = (key) => {
    if (accordion) {
      const newKeys = internalOpenKeys.includes(key)
        ? internalOpenKeys.filter(k => k !== key)
        : [key]
      handleOpenChange(newKeys)
    } else {
      const newKeys = internalOpenKeys.includes(key)
        ? internalOpenKeys.filter(k => k !== key)
        : [...internalOpenKeys, key]
      handleOpenChange(newKeys)
    }
  }

  const isOpen = (key) => internalOpenKeys.includes(key)
  const isSelected = (key) => internalSelectedKeys.includes(key)

  const renderMenuItem = (item, level = 0) => {
    const hasChildren = item.children && item.children.length > 0
    const itemKey = item.key || item.label
    const isItemOpen = isOpen(itemKey)
    const isItemSelected = isSelected(itemKey)

    const itemClasses = [
      'menu-item',
      'flex items-center',
      level > 0 ? 'ml-4' : '',
      isItemSelected ? 'bg-primary text-primary-content' : 'hover:bg-base-200',
      hasChildren ? 'cursor-pointer' : ''
    ].filter(Boolean).join(' ')

    const iconSize = level === 0 ? 'text-lg' : 'text-base'

    return (
      <li key={itemKey}>
        <div
          className={itemClasses}
          onClick={() => {
            if (hasChildren) {
              handleSubMenuClick(itemKey)
            } else {
              handleSelect(itemKey, item)
            }
          }}
        >
          {item.icon && (
            <span className={`material-icons ${iconSize} mr-2`}>
              {item.icon}
            </span>
          )}
          
          {!collapsed && (
            <span className="flex-1">{item.label}</span>
          )}
          
          {hasChildren && !collapsed && (
            <span className={`material-icons ${iconSize} transition-transform ${
              isItemOpen ? 'rotate-180' : ''
            }`}>
              expand_more
            </span>
          )}
        </div>
        
        {hasChildren && isItemOpen && !collapsed && (
          <ul className="submenu">
            {item.children.map(child => renderMenuItem(child, level + 1))}
          </ul>
        )}
      </li>
    )
  }

  const menuClasses = [
    'menu',
    mode === 'horizontal' ? 'menu-horizontal' : 'menu-vertical',
    theme === 'dark' ? 'bg-base-300' : 'bg-base-100',
    collapsed ? 'w-16' : 'w-64',
    className
  ].filter(Boolean).join(' ')

  return (
    <div className={`menu-container ${className}`} style={style}>
      <ul className={menuClasses} {...props}>
        {items.map(item => renderMenuItem(item))}
      </ul>
    </div>
  )
}

// MenuItem component for more flexible usage
export const MenuItem = ({
  key,
  label,
  icon,
  disabled = false,
  children,
  ...props
}) => {
  return {
    key,
    label,
    icon,
    disabled,
    children
  }
}

// SubMenu component for more flexible usage
export const SubMenu = ({
  key,
  title,
  icon,
  children,
  ...props
}) => {
  return {
    key,
    label: title,
    icon,
    children: children.map((child, index) => ({
      ...child,
      key: child.key || `${key}-${index}`
    }))
  }
}

export default Menu
