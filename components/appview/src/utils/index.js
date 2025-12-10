// Mirror of Vue utils - Common utility functions

// Deep set utility - mirrors Vue deepSet from common/utils
export const deepSet = (obj, path, value) => {
  const keys = path.split('.')
  const lastKey = keys.pop()
  let target = obj
  
  for (const key of keys) {
    if (!(key in target) || typeof target[key] !== 'object') {
      target[key] = {}
    }
    target = target[key]
  }
  
  target[lastKey] = value
  return obj
}

// Random string generator - mirrors Vue randomString from db
export const randomString = (length, charset) => {
  let result = ''
  const chars = charset || 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  const charLength = chars.length
  
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * charLength))
  }
  
  return result
}

// Pascal case conversion - mirrors Vue toPascalCase from app.ts
export const toPascalCase = (name) => {
  return `-${name}`.replace(/-./g, match => match[1].toUpperCase())
}

// Replace all occurrences - mirrors Vue replaceAll from components.ts
export const replaceAll = (string, search, replace) => {
  return string.split(search).join(replace)
}

// Array push utility - mirrors Vue array_push from components.ts
export const arrayPush = (arr, element) => {
  if (Array.isArray(element)) {
    arr.push(...element)
  } else if (element !== undefined && element !== null) {
    arr.push(element)
  }
}
