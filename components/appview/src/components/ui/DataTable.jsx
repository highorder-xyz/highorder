import React from 'react'

// Mirror of Vue DataTable component from components.ts
export const DataTable = ({
  data = [],
  columns = [],
  sortable = true,
  filterable = true,
  paginator = false,
  pageSize = 10,
  loading = false,
  emptyMessage = "暂无数据",
  className = "",
  style = {},
  onSort,
  onFilter,
  onPageChange,
  ...props
}) => {
  const [sortField, setSortField] = React.useState('')
  const [sortOrder, setSortOrder] = React.useState(1) // 1: asc, -1: desc
  const [filters, setFilters] = React.useState({})
  const [currentPage, setCurrentPage] = React.useState(1)

  const handleSort = (field) => {
    if (!sortable) return
    
    let newSortOrder = 1
    if (sortField === field && sortOrder === 1) {
      newSortOrder = -1
    }
    
    setSortField(field)
    setSortOrder(newSortOrder)
    
    if (onSort) {
      onSort(field, newSortOrder)
    }
  }

  const handleFilter = (field, value) => {
    const newFilters = { ...filters, [field]: value }
    setFilters(newFilters)
    
    if (onFilter) {
      onFilter(newFilters)
    }
  }

  const getSortIcon = (field) => {
    if (sortField !== field) {
      return 'swap_vert'
    }
    return sortOrder === 1 ? 'expand_less' : 'expand_more'
  }

  const filteredData = React.useMemo(() => {
    let filtered = [...data]
    
    // Apply filters
    Object.entries(filters).forEach(([field, value]) => {
      if (value) {
        filtered = filtered.filter(item => 
          String(item[field]).toLowerCase().includes(String(value).toLowerCase())
        )
      }
    })
    
    // Apply sorting
    if (sortField) {
      filtered.sort((a, b) => {
        const aVal = a[sortField]
        const bVal = b[sortField]
        
        if (aVal < bVal) return sortOrder === 1 ? -1 : 1
        if (aVal > bVal) return sortOrder === 1 ? 1 : -1
        return 0
      })
    }
    
    return filtered
  }, [data, filters, sortField, sortOrder])

  const paginatedData = React.useMemo(() => {
    if (!paginator) return filteredData
    
    const startIndex = (currentPage - 1) * pageSize
    return filteredData.slice(startIndex, startIndex + pageSize)
  }, [filteredData, paginator, currentPage, pageSize])

  const totalPages = Math.ceil(filteredData.length / pageSize)

  const renderHeader = () => (
    <thead>
      <tr>
        {columns.map((column, index) => (
          <th key={index} className={sortable ? 'cursor-pointer' : ''}>
            <div className="flex items-center gap-2">
              <span>{column.header}</span>
              {sortable && (
                <button
                  className="btn btn-xs btn-ghost"
                  onClick={() => handleSort(column.field)}
                >
                  <span className="material-icons text-sm">
                    {getSortIcon(column.field)}
                  </span>
                </button>
              )}
            </div>
            {filterable && column.filterable !== false && (
              <input
                type="text"
                className="input input-xs input-bordered w-full mt-1"
                placeholder={`筛选${column.header}`}
                value={filters[column.field] || ''}
                onChange={(e) => handleFilter(column.field, e.target.value)}
              />
            )}
          </th>
        ))}
      </tr>
    </thead>
  )

  const renderBody = () => {
    if (loading) {
      return (
        <tbody>
          <tr>
            <td colSpan={columns.length} className="text-center py-8">
              <div className="loading loading-spinner loading-md"></div>
            </td>
          </tr>
        </tbody>
      )
    }

    if (paginatedData.length === 0) {
      return (
        <tbody>
          <tr>
            <td colSpan={columns.length} className="text-center py-8 text-base-content/60">
              {emptyMessage}
            </td>
          </tr>
        </tbody>
      )
    }

    return (
      <tbody>
        {paginatedData.map((row, rowIndex) => (
          <tr key={rowIndex}>
            {columns.map((column, colIndex) => (
              <td key={colIndex}>
                {column.render ? column.render(row[column.field], row) : row[column.field]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    )
  }

  const renderPaginator = () => {
    if (!paginator || totalPages <= 1) return null

    return (
      <div className="flex justify-between items-center mt-4">
        <div className="text-sm text-base-content/60">
          显示 {((currentPage - 1) * pageSize) + 1} - {Math.min(currentPage * pageSize, filteredData.length)} / {filteredData.length} 条记录
        </div>
        <div className="join">
          <button
            className="join-item btn btn-sm"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            上一页
          </button>
          <button className="join-item btn btn-sm btn-active">
            {currentPage} / {totalPages}
          </button>
          <button
            className="join-item btn btn-sm"
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            下一页
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`data-table ${className}`} style={style} {...props}>
      <div className="overflow-x-auto">
        <table className="table table-zebra">
          {renderHeader()}
          {renderBody()}
        </table>
      </div>
      {renderPaginator()}
    </div>
  )
}

export default DataTable
