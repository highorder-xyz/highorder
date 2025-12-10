import React from 'react'

// Mirror of Vue Carousel component from components.ts
export const Carousel = ({
  items = [],
  autoplay = false,
  autoplayInterval = 3000,
  pauseOnHover = true,
  showIndicators = true,
  showNavigators = true,
  infinite = true,
  effect = "slide", // slide, fade, zoom
  height = "300px",
  width = "100%",
  aspectRatio = "16:9",
  loop = true,
  onChange,
  onSlideChange,
  className = "",
  style = {},
  ...props
}) => {
  const [currentIndex, setCurrentIndex] = React.useState(0)
  const [isHovering, setIsHovering] = React.useState(false)
  const [isPlaying, setIsPlaying] = React.useState(autoplay)
  const intervalRef = React.useRef(null)

  React.useEffect(() => {
    if (autoplay && isPlaying && !isHovering) {
      intervalRef.current = setInterval(() => {
        setCurrentIndex(prev => {
          const nextIndex = infinite || prev < items.length - 1 ? prev + 1 : 0
          return nextIndex
        })
      }, autoplayInterval)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [autoplay, isPlaying, isHovering, autoplayInterval, infinite, items.length])

  const handleMouseEnter = () => {
    setIsHovering(true)
    if (pauseOnHover) {
      setIsPlaying(false)
    }
  }

  const handleMouseLeave = () => {
    setIsHovering(false)
    if (autoplay) {
      setIsPlaying(true)
    }
  }

  const goToSlide = (index) => {
    setCurrentIndex(index)
    if (onChange) {
      onChange(index)
    }
    if (onSlideChange) {
      onSlideChange(index)
    }
  }

  const goToPrevious = () => {
    const newIndex = currentIndex > 0 ? currentIndex - 1 : (infinite ? items.length - 1 : 0)
    goToSlide(newIndex)
  }

  const goToNext = () => {
    const newIndex = currentIndex < items.length - 1 ? currentIndex + 1 : (infinite ? 0 : items.length - 1)
    goToSlide(newIndex)
  }

  const getEffectClass = () => {
    switch (effect) {
      case 'fade':
        return 'carousel-fade'
      case 'zoom':
        return 'carousel-zoom'
      default:
        return 'carousel-slide'
    }
  }

  const getAspectRatioClass = () => {
    switch (aspectRatio) {
      case '1:1':
        return 'aspect-square'
      case '4:3':
        return 'aspect-[4/3]'
      case '21:9':
        return 'aspect-[21/9]'
      default:
        return 'aspect-video' // 16:9
    }
  }

  const renderIndicators = () => {
    if (!showIndicators || items.length <= 1) return null

    return (
      <div className="carousel-indicators">
        {items.map((_, index) => (
          <button
            key={index}
            className={`carousel-indicator ${currentIndex === index ? 'active' : ''}`}
            onClick={() => goToSlide(index)}
          />
        ))}
      </div>
    )
  }

  const renderNavigators = () => {
    if (!showNavigators || items.length <= 1) return null

    return (
      <>
        <button
          className="carousel-nav carousel-prev"
          onClick={goToPrevious}
          disabled={!infinite && currentIndex === 0}
        >
          <span className="material-icons">chevron_left</span>
        </button>
        <button
          className="carousel-nav carousel-next"
          onClick={goToNext}
          disabled={!infinite && currentIndex === items.length - 1}
        >
          <span className="material-icons">chevron_right</span>
        </button>
      </>
    )
  }

  const renderItems = () => {
    return items.map((item, index) => (
      <div
        key={index}
        className={`carousel-item ${currentIndex === index ? 'active' : ''}`}
        style={{
          transform: `translateX(${effect === 'slide' ? (index - currentIndex) * 100 : 0}%)`,
          opacity: effect === 'fade' ? (currentIndex === index ? 1 : 0) : 1,
          transition: 'all 0.5s ease-in-out'
        }}
      >
        {typeof item === 'string' ? (
          <img src={item} alt={`Slide ${index + 1}`} className="w-full h-full object-cover" />
        ) : (
          <div className="carousel-content">
            {item.content || item}
          </div>
        )}
      </div>
    ))
  }

  const containerStyle = {
    width,
    height,
    ...style
  }

  return (
    <div
      className={`carousel ${getEffectClass()} ${getAspectRatioClass()} ${className}`}
      style={containerStyle}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      {...props}
    >
      <div className="carousel-container">
        {renderItems()}
      </div>
      
      {renderNavigators()}
      {renderIndicators()}
      
      {/* Autoplay indicator */}
      {autoplay && (
        <div className="absolute top-4 right-4">
          <button
            className="btn btn-sm btn-circle"
            onClick={() => setIsPlaying(!isPlaying)}
          >
            <span className="material-icons text-sm">
              {isPlaying ? 'pause' : 'play_arrow'}
            </span>
          </button>
        </div>
      )}
    </div>
  )
}

// CarouselItem component for more flexible usage
export const CarouselItem = ({
  image = "",
  title = "",
  subtitle = "",
  content = "",
  link = "",
  children,
  ...props
}) => {
  return (
    <div className="carousel-slide-content" {...props}>
      {image && (
        <img src={image} alt={title} className="w-full h-full object-cover" />
      )}
      {(title || subtitle || content || link) && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-6 text-white">
          {title && <h3 className="text-2xl font-bold mb-2">{title}</h3>}
          {subtitle && <p className="text-lg mb-2">{subtitle}</p>}
          {content && <p className="text-sm mb-4">{content}</p>}
          {link && (
            <a href={link} className="btn btn-primary btn-sm">
              查看更多
            </a>
          )}
        </div>
      )}
      {children}
    </div>
  )
}

export default Carousel
