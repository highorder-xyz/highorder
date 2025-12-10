import React from 'react'

// Mirror of Vue Calendar component from components.ts
export const Calendar = ({
  value = null,
  mode = "single", // single, range, multiple
  format = "YYYY-MM-DD",
  placeholder = "选择日期",
  disabled = false,
  readonly = false,
  showTime = false,
  showToday = true,
  showOtherMonths = false,
  firstDayOfWeek = 1, // 0: Sunday, 1: Monday
  minDate = null,
  maxDate = null,
  disabledDates = [],
  size = "normal", // small, normal, large
  onChange,
  onSelect,
  className = "",
  style = {},
  ...props
}) => {
  const [isOpen, setIsOpen] = React.useState(false)
  const [currentDate, setCurrentDate] = React.useState(new Date())
  const [selectedDate, setSelectedDate] = React.useState(value)
  const [selectedRange, setSelectedRange] = React.useState({ start: null, end: null })
  const [selectedDates, setSelectedDates] = React.useState(value || [])
  const calendarRef = React.useRef(null)

  React.useEffect(() => {
    setSelectedDate(value)
    setSelectedDates(value || [])
  }, [value])

  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (calendarRef.current && !calendarRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const formatDate = (date, fmt = format) => {
    if (!date) return ''
    
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hour = String(date.getHours()).padStart(2, '0')
    const minute = String(date.getMinutes()).padStart(2, '0')
    
    return fmt
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hour)
      .replace('mm', minute)
  }

  const parseDate = (dateStr) => {
    if (!dateStr) return null
    
    // Simple date parsing - can be enhanced for more formats
    const parts = dateStr.split('-')
    if (parts.length >= 3) {
      return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]))
    }
    return null
  }

  const isDateDisabled = (date) => {
    if (minDate && date < minDate) return true
    if (maxDate && date > maxDate) return true
    
    return disabledDates.some(disabledDate => {
      if (disabledDate instanceof Date) {
        return date.toDateString() === disabledDate.toDateString()
      }
      return false
    })
  }

  const isDateSelected = (date) => {
    const dateStr = date.toDateString()
    
    if (mode === 'single') {
      return selectedDate && selectedDate.toDateString() === dateStr
    }
    
    if (mode === 'range') {
      return (selectedRange.start && selectedRange.start.toDateString() === dateStr) ||
             (selectedRange.end && selectedRange.end.toDateString() === dateStr)
    }
    
    if (mode === 'multiple') {
      return selectedDates.some(d => d.toDateString() === dateStr)
    }
    
    return false
  }

  const isDateInRange = (date) => {
    if (mode !== 'range' || !selectedRange.start || !selectedRange.end) return false
    
    return date >= selectedRange.start && date <= selectedRange.end
  }

  const handleDateClick = (date) => {
    if (disabled || readonly || isDateDisabled(date)) return

    if (mode === 'single') {
      setSelectedDate(date)
      if (onChange) onChange(date)
      if (onSelect) onSelect(date)
      setIsOpen(false)
    } else if (mode === 'range') {
      if (!selectedRange.start || (selectedRange.start && selectedRange.end)) {
        setSelectedRange({ start: date, end: null })
      } else if (date < selectedRange.start) {
        setSelectedRange({ start: date, end: selectedRange.start })
      } else {
        setSelectedRange({ ...selectedRange, end: date })
        if (onChange) onChange(selectedRange)
        setIsOpen(false)
      }
    } else if (mode === 'multiple') {
      const newSelectedDates = selectedDates.some(d => d.toDateString() === date.toDateString())
        ? selectedDates.filter(d => d.toDateString() !== date.toDateString())
        : [...selectedDates, date]
      
      setSelectedDates(newSelectedDates)
      if (onChange) onChange(newSelectedDates)
    }
  }

  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate)
    newDate.setMonth(newDate.getMonth() + direction)
    setCurrentDate(newDate)
  }

  const goToToday = () => {
    setCurrentDate(new Date())
  }

  const getDaysInMonth = (date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDayOfWeek = (firstDay.getDay() - firstDayOfWeek + 7) % 7

    const days = []
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null)
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day))
    }
    
    return days
  }

  const getWeekdayNames = () => {
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    if (firstDayOfWeek === 1) {
      return [...weekdays.slice(1), weekdays[0]]
    }
    return weekdays
  }

  const renderCalendar = () => {
    const days = getDaysInMonth(currentDate)
    const weekdays = getWeekdayNames()
    const monthNames = [
      '一月', '二月', '三月', '四月', '五月', '六月',
      '七月', '八月', '九月', '十月', '十一月', '十二月'
    ]

    return (
      <div className="calendar bg-base-100 border rounded-lg shadow-lg p-4 w-80">
        {/* Header */}
        <div className="calendar-header flex items-center justify-between mb-4">
          <button
            className="btn btn-sm btn-ghost"
            onClick={() => navigateMonth(-1)}
          >
            <span className="material-icons">chevron_left</span>
          </button>
          
          <div className="text-lg font-semibold">
            {currentDate.getFullYear()}年 {monthNames[currentDate.getMonth()]}
          </div>
          
          <button
            className="btn btn-sm btn-ghost"
            onClick={() => navigateMonth(1)}
          >
            <span className="material-icons">chevron_right</span>
          </button>
        </div>

        {/* Weekday Headers */}
        <div className="calendar-weekdays grid grid-cols-7 gap-1 mb-2">
          {weekdays.map(day => (
            <div key={day} className="text-center text-sm font-medium text-base-content/60 py-1">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="calendar-days grid grid-cols-7 gap-1">
          {days.map((date, index) => {
            if (!date) {
              return <div key={index} className="calendar-day p-2" />
            }

            const isDisabled = isDateDisabled(date)
            const isSelected = isDateSelected(date)
            const isInRange = isDateInRange(date)
            const isToday = date.toDateString() === new Date().toDateString()
            const isOtherMonth = date.getMonth() !== currentDate.getMonth()

            const dayClasses = [
              'calendar-day',
              'p-2 text-center cursor-pointer rounded',
              isSelected ? 'bg-primary text-primary-content' : '',
              isInRange && !isSelected ? 'bg-primary/20' : '',
              isDisabled ? 'text-base-content/30 cursor-not-allowed' : 'hover:bg-base-200',
              isToday && !isSelected ? 'border border-primary' : '',
              isOtherMonth && !showOtherMonths ? 'text-base-content/30' : ''
            ].filter(Boolean).join(' ')

            return (
              <div
                key={index}
                className={dayClasses}
                onClick={() => handleDateClick(date)}
              >
                {date.getDate()}
              </div>
            )
          })}
        </div>

        {/* Footer */}
        {showToday && (
          <div className="calendar-footer mt-4 text-center">
            <button
              className="btn btn-sm btn-ghost"
              onClick={goToToday}
            >
              今天
            </button>
          </div>
        )}
      </div>
    )
  }

  const getDisplayValue = () => {
    if (mode === 'single') {
      return selectedDate ? formatDate(selectedDate) : ''
    } else if (mode === 'range') {
      if (selectedRange.start && selectedRange.end) {
        return `${formatDate(selectedRange.start)} - ${formatDate(selectedRange.end)}`
      } else if (selectedRange.start) {
        return `${formatDate(selectedRange.start)} -`
      }
      return ''
    } else if (mode === 'multiple') {
      return selectedDates.map(date => formatDate(date)).join(', ')
    }
    return ''
  }

  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'input-sm'
      case 'large':
        return 'input-lg'
      default:
        return 'input-md'
    }
  }

  return (
    <div ref={calendarRef} className={`calendar-container ${className}`} style={style}>
      <div className="relative">
        <input
          type="text"
          className={`input input-bordered ${getSizeClass(size)} w-full`}
          value={getDisplayValue()}
          placeholder={placeholder}
          disabled={disabled}
          readOnly={readonly}
          onClick={() => !disabled && !readonly && setIsOpen(!isOpen)}
          {...props}
        />
        
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
          <span className="material-icons text-base-content/60">calendar_today</span>
        </div>
      </div>
      
      {isOpen && (
        <div className="absolute top-full left-0 z-50 mt-1">
          {renderCalendar()}
        </div>
      )}
    </div>
  )
}

export default Calendar
