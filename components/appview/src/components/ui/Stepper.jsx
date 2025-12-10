import React from 'react'

// Mirror of Vue Stepper component from components.ts
export const Stepper = ({
  steps = [],
  current = 0,
  direction = "horizontal", // horizontal, vertical
  size = "normal", // small, normal, large
  color = "primary", // primary, secondary, accent, neutral, info, success, warning, error
  showNumbers = true,
  showLabels = true,
  showDescriptions = true,
  allowClick = true,
  linear = true,
  onChange,
  onStepClick,
  className = "",
  style = {},
  ...props
}) => {
  const [activeStep, setActiveStep] = React.useState(current)

  React.useEffect(() => {
    setActiveStep(current)
  }, [current])

  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'stepper-sm'
      case 'large':
        return 'stepper-lg'
      default:
        return 'stepper-md'
    }
  }

  const getColorClass = (color) => {
    switch (color) {
      case 'primary':
        return 'stepper-primary'
      case 'secondary':
        return 'stepper-secondary'
      case 'accent':
        return 'stepper-accent'
      case 'neutral':
        return 'stepper-neutral'
      case 'info':
        return 'stepper-info'
      case 'success':
        return 'stepper-success'
      case 'warning':
        return 'stepper-warning'
      case 'error':
        return 'stepper-error'
      default:
        return 'stepper-primary'
    }
  }

  const getStepStatus = (index) => {
    if (index < activeStep) return 'completed'
    if (index === activeStep) return 'active'
    return 'pending'
  }

  const handleStepClick = (index) => {
    if (!allowClick) return
    
    // Check if we can go to this step (linear mode)
    if (linear && index > activeStep + 1) return
    
    setActiveStep(index)
    if (onChange) {
      onChange(index)
    }
    if (onStepClick) {
      onStepClick(index)
    }
  }

  const handleNext = () => {
    if (activeStep < steps.length - 1) {
      const newStep = activeStep + 1
      setActiveStep(newStep)
      if (onChange) {
        onChange(newStep)
      }
    }
  }

  const handlePrevious = () => {
    if (activeStep > 0) {
      const newStep = activeStep - 1
      setActiveStep(newStep)
      if (onChange) {
        onChange(newStep)
      }
    }
  }

  const renderStep = (step, index) => {
    const status = getStepStatus(index)
    const isClickable = allowClick && (!linear || index <= activeStep + 1)
    
    const stepClasses = [
      'step',
      `step-${color}`,
      status === 'completed' ? 'step-primary' : '',
      status === 'active' ? 'step-primary' : '',
      isClickable ? 'cursor-pointer' : 'cursor-default',
      getSizeClass(size)
    ].filter(Boolean).join(' ')

    return (
      <div
        key={index}
        className={stepClasses}
        onClick={() => handleStepClick(index)}
      >
        {/* Step indicator */}
        <div className="step-indicator">
          {showNumbers ? (
            <span className="step-number">{index + 1}</span>
          ) : step.icon ? (
            <span className="material-icons">{step.icon}</span>
          ) : (
            <span className="material-icons">
              {status === 'completed' ? 'check' : 'radio_button_unchecked'}
            </span>
          )}
        </div>
        
        {/* Step content */}
        {showLabels && (step.title || step.label) && (
          <div className="step-content">
            <div className="step-title">
              {step.title || step.label}
            </div>
            {showDescriptions && step.description && (
              <div className="step-description">
                {step.description}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  const stepperClasses = [
    'steps',
    direction === 'vertical' ? 'steps-vertical' : 'steps-horizontal',
    getSizeClass(size),
    getColorClass(color),
    className
  ].filter(Boolean).join(' ')

  return (
    <div className="stepper-container" style={style}>
      {/* Steps */}
      <div className={stepperClasses} {...props}>
        {steps.map((step, index) => renderStep(step, index))}
      </div>
      
      {/* Step content */}
      {steps[activeStep] && (
        <div className="step-content-area mt-6">
          {steps[activeStep].content && (
            <div className="step-content-body">
              {steps[activeStep].content}
            </div>
          )}
          {steps[activeStep].children}
        </div>
      )}
      
      {/* Navigation controls */}
      <div className="stepper-navigation flex justify-between mt-6">
        <button
          className="btn btn-outline"
          onClick={handlePrevious}
          disabled={activeStep === 0}
        >
          <span className="material-icons mr-2">chevron_left</span>
          上一步
        </button>
        
        <div className="stepper-info text-sm text-base-content/60">
          第 {activeStep + 1} 步，共 {steps.length} 步
        </div>
        
        <button
          className="btn btn-primary"
          onClick={handleNext}
          disabled={activeStep === steps.length - 1}
        >
          下一步
          <span className="material-icons ml-2">chevron_right</span>
        </button>
      </div>
    </div>
  )
}

// Step component for more flexible usage
export const Step = ({
  title,
  description,
  icon,
  content,
  children,
  ...props
}) => {
  return {
    title,
    description,
    icon,
    content,
    children,
    ...props
  }
}

export default Stepper
