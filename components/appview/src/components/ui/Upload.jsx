import React from 'react'

// Mirror of Vue Upload component from components.ts
export const Upload = ({
  accept = "*/*",
  multiple = false,
  disabled = false,
  readonly = false,
  maxSize = 5 * 1024 * 1024, // 5MB default
  maxCount = 1,
  fileList = [],
  uploadText = "点击上传",
  dragText = "或拖拽文件到此区域",
  listType = "text", // text, picture, picture-card
  showUploadList = true,
  onChange,
  onPreview,
  onRemove,
  onSuccess,
  onError,
  className = "",
  style = {},
  ...props
}) => {
  const [files, setFiles] = React.useState(fileList)
  const [isDragging, setIsDragging] = React.useState(false)
  const fileInputRef = React.useRef(null)

  React.useEffect(() => {
    setFiles(fileList)
  }, [fileList])

  const handleFileSelect = (selectedFiles) => {
    const fileArray = Array.from(selectedFiles)
    
    // Validate file count
    if (files.length + fileArray.length > maxCount) {
      alert(`最多只能上传 ${maxCount} 个文件`)
      return
    }

    // Validate file size
    const oversizedFiles = fileArray.filter(file => file.size > maxSize)
    if (oversizedFiles.length > 0) {
      alert(`文件大小不能超过 ${Math.round(maxSize / 1024 / 1024)}MB`)
      return
    }

    // Process files
    const newFiles = fileArray.map(file => ({
      uid: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploading',
      file: file,
      url: URL.createObjectURL(file)
    }))

    const updatedFiles = [...files, ...newFiles]
    setFiles(updatedFiles)

    // Trigger onChange
    if (onChange) {
      onChange(updatedFiles)
    }

    // Simulate upload success
    setTimeout(() => {
      const successFiles = updatedFiles.map(f => ({
        ...f,
        status: 'done'
      }))
      setFiles(successFiles)
      
      if (onChange) {
        onChange(successFiles)
      }
      if (onSuccess) {
        onSuccess(newFiles)
      }
    }, 1000)
  }

  const handleFileInputChange = (e) => {
    if (disabled || readonly) return
    
    const selectedFiles = e.target.files
    if (selectedFiles && selectedFiles.length > 0) {
      handleFileSelect(selectedFiles)
    }
    
    // Clear input value to allow selecting the same file again
    e.target.value = ''
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    if (disabled || readonly) return
    
    const droppedFiles = e.dataTransfer.files
    if (droppedFiles && droppedFiles.length > 0) {
      handleFileSelect(droppedFiles)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    if (!disabled && !readonly) {
      setIsDragging(true)
    }
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleRemove = (file) => {
    const updatedFiles = files.filter(f => f.uid !== file.uid)
    setFiles(updatedFiles)
    
    if (onChange) {
      onChange(updatedFiles)
    }
    if (onRemove) {
      onRemove(file)
    }
  }

  const handlePreview = (file) => {
    if (onPreview) {
      onPreview(file)
    } else {
      // Default preview behavior
      window.open(file.url, '_blank')
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFileIcon = (file) => {
    if (file.type.startsWith('image/')) {
      return <img src={file.url} alt={file.name} className="w-full h-full object-cover" />
    }
    
    const extension = file.name.split('.').pop()?.toLowerCase()
    const iconMap = {
      pdf: 'picture_as_pdf',
      doc: 'description',
      docx: 'description',
      xls: 'table_chart',
      xlsx: 'table_chart',
      ppt: 'slideshow',
      pptx: 'slideshow',
      txt: 'text_snippet',
      zip: 'archive',
      rar: 'archive'
    }
    
    return (
      <span className="material-icons text-4xl text-base-content/60">
        {iconMap[extension] || 'insert_drive_file'}
      </span>
    )
  }

  const renderUploadButton = () => {
    if (files.length >= maxCount) return null

    const buttonClasses = [
      'upload-button',
      'border-2 border-dashed border-base-300',
      'rounded-lg',
      'p-8',
      'text-center',
      'cursor-pointer',
      'transition-colors',
      isDragging ? 'border-primary bg-primary/10' : 'hover:border-primary/50',
      disabled || readonly ? 'cursor-not-allowed opacity-50' : ''
    ].filter(Boolean).join(' ')

    return (
      <div
        className={buttonClasses}
        onClick={() => !disabled && !readonly && fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          disabled={disabled || readonly}
          onChange={handleFileInputChange}
          className="hidden"
          {...props}
        />
        
        <div className="flex flex-col items-center gap-2">
          <span className="material-icons text-4xl text-base-content/60">
            cloud_upload
          </span>
          <div>
            <p className="text-base-content/80">{uploadText}</p>
            <p className="text-sm text-base-content/60">{dragText}</p>
            <p className="text-xs text-base-content/50 mt-1">
              支持 {accept} 格式，单个文件不超过 {Math.round(maxSize / 1024 / 1024)}MB
            </p>
          </div>
        </div>
      </div>
    )
  }

  const renderFileList = () => {
    if (!showUploadList || files.length === 0) return null

    return (
      <div className="file-list mt-4 space-y-2">
        {files.map((file) => (
          <div
            key={file.uid}
            className={`file-item flex items-center gap-3 p-3 border rounded-lg ${
              file.status === 'uploading' ? 'border-info' : 
              file.status === 'done' ? 'border-success' : 'border-error'
            }`}
          >
            {listType === 'picture' || listType === 'picture-card' ? (
              <div className="w-12 h-12 flex-shrink-0">
                {getFileIcon(file)}
              </div>
            ) : (
              <span className="material-icons text-2xl text-base-content/60">
                insert_drive_file
              </span>
            )}
            
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{file.name}</p>
              <p className="text-xs text-base-content/60">
                {formatFileSize(file.size)}
                {file.status === 'uploading' && ' • 上传中...'}
                {file.status === 'done' && ' • 上传成功'}
                {file.status === 'error' && ' • 上传失败'}
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              {file.status === 'done' && (
                <button
                  className="btn btn-sm btn-ghost"
                  onClick={() => handlePreview(file)}
                >
                  <span className="material-icons text-sm">visibility</span>
                </button>
              )}
              
              <button
                className="btn btn-sm btn-ghost text-error"
                onClick={() => handleRemove(file)}
                disabled={disabled || readonly}
              >
                <span className="material-icons text-sm">delete</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className={`upload-container ${className}`} style={style}>
      {renderUploadButton()}
      {renderFileList()}
    </div>
  )
}

export default Upload
