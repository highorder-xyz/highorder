import React from 'react'

// Mirror of Vue Title component from components.ts
export const Title = ({
  title = "",
  level = 1,
  sub_title = "",
  ...props
}) => {
  const getTitleClass = (level) => {
    switch (level) {
      case 1:
        return "text-4xl font-bold"
      case 2:
        return "text-3xl font-bold"
      case 3:
        return "text-2xl font-semibold"
      case 4:
        return "text-xl font-medium"
      case 5:
        return "text-lg font-medium"
      case 6:
        return "text-base font-medium"
      default:
        return "text-4xl font-bold"
    }
  }

  const getSubTitleClass = (level) => {
    switch (level) {
      case 1:
        return "text-lg text-base-content/70"
      case 2:
        return "text-base text-base-content/70"
      case 3:
        return "text-sm text-base-content/70"
      default:
        return "text-base text-base-content/70"
    }
  }

  const TitleTag = `h${Math.min(Math.max(level, 1), 6)}`

  return (
    <div className="title">
      <TitleTag className={getTitleClass(level)}>
        {title}
      </TitleTag>
      {sub_title && (
        <span className={getSubTitleClass(level)}>
          {sub_title}
        </span>
      )}
    </div>
  )
}

export default Title
