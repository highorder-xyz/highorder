import React from 'react'

// Mirror of Vue Tree component from components.ts
export const Tree = ({
  data = [],
  checkable = false,
  showIcon = true,
  showLine = true,
  selectable = true,
  multiple = false,
  defaultExpandedKeys = [],
  defaultSelectedKeys = [],
  defaultCheckedKeys = [],
  onExpand,
  onSelect,
  onCheck,
  className = "",
  style = {},
  ...props
}) => {
  const [expandedKeys, setExpandedKeys] = React.useState(new Set(defaultExpandedKeys))
  const [selectedKeys, setSelectedKeys] = React.useState(new Set(defaultSelectedKeys))
  const [checkedKeys, setCheckedKeys] = React.useState(new Set(defaultCheckedKeys))

  const handleExpand = (key, node) => {
    const newExpandedKeys = new Set(expandedKeys)
    if (newExpandedKeys.has(key)) {
      newExpandedKeys.delete(key)
    } else {
      newExpandedKeys.add(key)
    }
    setExpandedKeys(newExpandedKeys)
    if (onExpand) {
      onExpand(key, node)
    }
  }

  const handleSelect = (key, node) => {
    let newSelectedKeys
    if (multiple) {
      newSelectedKeys = new Set(selectedKeys)
      if (newSelectedKeys.has(key)) {
        newSelectedKeys.delete(key)
      } else {
        newSelectedKeys.add(key)
      }
    } else {
      newSelectedKeys = new Set([key])
    }
    setSelectedKeys(newSelectedKeys)
    if (onSelect) {
      onSelect(key, node)
    }
  }

  const handleCheck = (key, node, checked) => {
    const newCheckedKeys = new Set(checkedKeys)
    if (checked) {
      newCheckedKeys.add(key)
    } else {
      newCheckedKeys.delete(key)
    }
    setCheckedKeys(newCheckedKeys)
    if (onCheck) {
      onCheck(key, node, checked)
    }
  }

  const renderTreeNode = (node, level = 0) => {
    const hasChildren = node.children && node.children.length > 0
    const isExpanded = expandedKeys.has(node.key)
    const isSelected = selectedKeys.has(node.key)
    const isChecked = checkedKeys.has(node.key)

    return (
      <li key={node.key} className="tree-node">
        <div
          className={`tree-node-content flex items-center py-1 px-2 hover:bg-base-200 cursor-pointer ${
            isSelected ? 'bg-primary text-primary-content' : ''
          }`}
          style={{ paddingLeft: `${level * 20 + 8}px` }}
        >
          {/* Expand/Collapse icon */}
          {hasChildren ? (
            <span
              className="material-icons text-sm mr-1 cursor-pointer"
              onClick={() => handleExpand(node.key, node)}
            >
              {isExpanded ? 'expand_more' : 'chevron_right'}
            </span>
          ) : (
            <span className="w-4 mr-1" />
          )}

          {/* Checkbox */}
          {checkable && (
            <input
              type="checkbox"
              className="checkbox checkbox-sm mr-2"
              checked={isChecked}
              onChange={(e) => handleCheck(node.key, node, e.target.checked)}
            />
          )}

          {/* Icon */}
          {showIcon && node.icon && (
            <span className="material-icons text-sm mr-2">{node.icon}</span>
          )}

          {/* Title */}
          <span className="flex-1" onClick={() => selectable && handleSelect(node.key, node)}>
            {node.title}
          </span>
        </div>

        {/* Children */}
        {hasChildren && isExpanded && (
          <ul className="tree-children">
            {node.children.map(child => renderTreeNode(child, level + 1))}
          </ul>
        )}
      </li>
    )
  }

  return (
    <div className={`tree ${className}`} style={style}>
      <ul className="tree-root">
        {data.map(node => renderTreeNode(node))}
      </ul>
    </div>
  )
}

export default Tree
