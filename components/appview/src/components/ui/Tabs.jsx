import React from 'react'

// Mirror of Vue Tabs component from components.ts
export const Tabs = ({
  value = 0,
  onChange,
  variant = "default", // default, bordered, lifted
  size = "normal", // small, normal, large
  className = "",
  style = {},
  children,
  ...props
}) => {
  const [activeTab, setActiveTab] = React.useState(value)
  const tabsRef = React.useRef(null)

  React.useEffect(() => {
    setActiveTab(value)
  }, [value])

  const handleTabChange = (index) => {
    setActiveTab(index)
    if (onChange) {
      onChange(index)
    }
  }

  const getVariantClass = (variant) => {
    switch (variant) {
      case 'bordered':
        return 'tabs-bordered'
      case 'lifted':
        return 'tabs-lifted'
      default:
        return 'tabs-boxed'
    }
  }

  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'tabs-sm'
      case 'large':
        return 'tabs-lg'
      default:
        return 'tabs-md'
    }
  }

  const childrenArray = React.Children.toArray(children)
  const tabLabels = []
  const tabContents = []

  childrenArray.forEach((child, index) => {
    if (child.type === Tab) {
      tabLabels.push(
        <a
          key={index}
          className={`tab ${activeTab === index ? 'tab-active' : ''}`}
          onClick={() => handleTabChange(index)}
        >
          {child.props.label}
        </a>
      )
      tabContents.push(
        <div
          key={index}
          className={`tab-content ${activeTab === index ? 'tab-content-active' : ''}`}
        >
          {child.props.children}
        </div>
      )
    }
  })

  return (
    <div 
      ref={tabsRef}
      className={`tabs ${getVariantClass()} ${getSizeClass()} ${className}`}
      style={style}
      {...props}
    >
      <div className="tab-list">
        {tabLabels}
      </div>
      <div className="tab-panels">
        {tabContents}
      </div>
    </div>
  )
}

// Tab Panel Component
export const Tab = ({
  label = "",
  disabled = false,
  children,
  ...props
}) => {
  return (
    <div {...props}>
      {children}
    </div>
  )
}

export default Tabs
