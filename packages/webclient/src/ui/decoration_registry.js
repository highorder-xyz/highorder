import React from 'react'

const _registry = new Map()

function normalizeName(name) {
  if (!name) return ''
  return String(name)
    .trim()
    .toLowerCase()
    .replace(/_/g, '-')
}

export function registerDecoration(name, Component) {
  if (!name) return
  const key = normalizeName(name)
  if (!key) return
  _registry.set(key, Component)
}

export function getDecoration(name) {
  const key = normalizeName(name)
  if (!key) return undefined
  return _registry.get(key)
}

export function renderDecoration(element, context) {
  const name = element?.name
  const props = element?.properties || {}
  const Component = getDecoration(name)
  if (!Component) return null
  return React.createElement(Component, { ...props, context })
}
