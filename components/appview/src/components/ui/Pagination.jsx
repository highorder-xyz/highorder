import React from 'react'

// Mirror of Vue Pagination component from components.ts
export const Pagination = ({
  current = 1,
  total = 1,
  pageSize = 10,
  showSizeChanger = false,
  showQuickJumper = false,
  showTotal = false,
  size = "normal", // small, normal, large
  onChange,
  onPageSizeChange,
  className = "",
  style = {},
  ...props
}) => {
  const [currentPage, setCurrentPage] = React.useState(current)
  const [pageSizeState, setPageSizeState] = React.useState(pageSize)
  const [quickJumperValue, setQuickJumperValue] = React.useState('')

  React.useEffect(() => {
    setCurrentPage(current)
  }, [current])

  const totalPages = Math.ceil(total / pageSizeState)
  const startItem = (currentPage - 1) * pageSizeState + 1
  const endItem = Math.min(currentPage * pageSizeState, total)

  const handlePageChange = (page) => {
    if (page < 1 || page > totalPages || page === currentPage) return
    
    setCurrentPage(page)
    if (onChange) {
      onChange(page, pageSizeState)
    }
  }

  const handlePageSizeChange = (newSize) => {
    setPageSizeState(newSize)
    const newTotalPages = Math.ceil(total / newSize)
    if (currentPage > newTotalPages) {
      setCurrentPage(newTotalPages)
    }
    if (onPageSizeChange) {
      onPageSizeChange(newSize)
    }
  }

  const handleQuickJumper = () => {
    const page = parseInt(quickJumperValue)
    if (page && page >= 1 && page <= totalPages) {
      handlePageChange(page)
      setQuickJumperValue('')
    }
  }

  const getSizeClass = (size) => {
    switch (size) {
      case 'small':
        return 'pagination-sm'
      case 'large':
        return 'pagination-lg'
      default:
        return 'pagination-md'
    }
  }

  const renderPageNumbers = () => {
    const pages = []
    const maxVisiblePages = 7
    
    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(
          <button
            key={i}
            className={`join-item btn ${currentPage === i ? 'btn-active' : ''}`}
            onClick={() => handlePageChange(i)}
          >
            {i}
          </button>
        )
      }
    } else {
      // Show with ellipsis
      const start = Math.max(1, currentPage - 2)
      const end = Math.min(totalPages, currentPage + 2)
      
      if (start > 1) {
        pages.push(
          <button
            key={1}
            className={`join-item btn ${currentPage === 1 ? 'btn-active' : ''}`}
            onClick={() => handlePageChange(1)}
          >
            1
          </button>
        )
        if (start > 2) {
          pages.push(
            <span key="ellipsis1" className="join-item btn btn-disabled">
              ...
            </span>
          )
        }
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(
          <button
            key={i}
            className={`join-item btn ${currentPage === i ? 'btn-active' : ''}`}
            onClick={() => handlePageChange(i)}
          >
            {i}
          </button>
        )
      }
      
      if (end < totalPages) {
        if (end < totalPages - 1) {
          pages.push(
            <span key="ellipsis2" className="join-item btn btn-disabled">
              ...
            </span>
          )
        }
        pages.push(
          <button
            key={totalPages}
            className={`join-item btn ${currentPage === totalPages ? 'btn-active' : ''}`}
            onClick={() => handlePageChange(totalPages)}
          >
            {totalPages}
          </button>
        )
      }
    }
    
    return pages
  }

  return (
    <div className={`pagination ${getSizeClass()} ${className}`} style={style} {...props}>
      {/* Previous Button */}
      <button
        className="join-item btn"
        disabled={currentPage === 1}
        onClick={() => handlePageChange(currentPage - 1)}
      >
        上一页
      </button>
      
      {/* Page Numbers */}
      <div className="join">
        {renderPageNumbers()}
      </div>
      
      {/* Next Button */}
      <button
        className="join-item btn"
        disabled={currentPage === totalPages}
        onClick={() => handlePageChange(currentPage + 1)}
      >
        下一页
      </button>
      
      {/* Page Size Changer */}
      {showSizeChanger && (
        <select
          className="select select-bordered select-sm ml-4"
          value={pageSizeState}
          onChange={(e) => handlePageSizeChange(parseInt(e.target.value))}
        >
          <option value={10}>10 条/页</option>
          <option value={20}>20 条/页</option>
          <option value={50}>50 条/页</option>
          <option value={100}>100 条/页</option>
        </select>
      )}
      
      {/* Quick Jumper */}
      {showQuickJumper && (
        <div className="flex items-center gap-2 ml-4">
          <span>跳至</span>
          <input
            type="number"
            className="input input-bordered input-sm w-16"
            value={quickJumperValue}
            onChange={(e) => setQuickJumperValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleQuickJumper()}
            placeholder="页码"
          />
          <span>页</span>
          <button className="btn btn-sm" onClick={handleQuickJumper}>
            确定
          </button>
        </div>
      )}
      
      {/* Total Info */}
      {showTotal && (
        <div className="text-sm text-base-content/60 ml-4">
          共 {total} 条记录，第 {currentPage}/{totalPages} 页
        </div>
      )}
    </div>
  )
}

export default Pagination
