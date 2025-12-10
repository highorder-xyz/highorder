import React from 'react'

// Mirror of Vue ColorPicker component from components.ts
export const ColorPicker = ({
  value = "#000000",
  onChange,
  disabled = false,
  showAlpha = true,
  showColorPalette = true,
  presetColors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'],
  size = "normal", // small, normal, large
  className = "",
  style = {},
  ...props
}) => {
  const [isOpen, setIsOpen] = React.useState(false)
  const [color, setColor] = React.useState(value)
  const [hue, setHue] = React.useState(0)
  const [saturation, setSaturation] = React.useState(100)
  const [lightness, setLightness] = React.useState(50)
  const [alpha, setAlpha] = React.useState(100)

  React.useEffect(() => {
    setColor(value)
  }, [value])

  const handleColorChange = (newColor) => {
    setColor(newColor)
    if (onChange) {
      onChange(newColor)
    }
  }

  const handlePresetColorClick = (presetColor) => {
    handleColorChange(presetColor)
    setIsOpen(false)
  }

  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'w-8 h-8'
      case 'large':
        return 'w-12 h-12'
      default:
        return 'w-10 h-10'
    }
  }

  return (
    <div className={`color-picker ${className}`} style={style}>
      <div
        className={`color-preview rounded border-2 border-base-300 cursor-pointer ${getSizeClass()}`}
        style={{ backgroundColor: color }}
        onClick={() => !disabled && setIsOpen(!isOpen)}
      />
      
      {isOpen && (
        <div className="color-picker-panel absolute top-full left-0 z-50 bg-base-100 border rounded-lg shadow-lg p-4 w-64">
          <div className="color-palette grid grid-cols-6 gap-2 mb-4">
            {presetColors.map((presetColor, index) => (
              <div
                key={index}
                className="w-8 h-8 rounded cursor-pointer border-2 border-base-300 hover:border-primary"
                style={{ backgroundColor: presetColor }}
                onClick={() => handlePresetColorClick(presetColor)}
              />
            ))}
          </div>
          
          <div className="color-input">
            <input
              type="text"
              className="input input-bordered input-sm w-full"
              value={color}
              onChange={(e) => handleColorChange(e.target.value)}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default ColorPicker
