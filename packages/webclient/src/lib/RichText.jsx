import React, { useMemo } from 'react'
import { RichTextCompiler } from '../common/richtext.js'

function getSizeRatio(size) {
  const s = Number(size)
  if (Number.isNaN(s)) return 1
  if (s <= 1) return 0.75
  if (s === 2) return 0.875
  if (s === 3) return 1
  if (s === 4) return 1.125
  if (s === 5) return 1.25
  if (s === 6) return 1.375
  return 1.5
}

function getTextColor(name) {
  const map = {
    primary: '#3B82F6',
    success: '#22C55E',
    warn: '#F59E0B',
    warning: '#F59E0B',
    danger: '#EF4444',
    error: '#EF4444',
    info: '#06B6D4',
    gray: '#6B7280'
  }
  return map[name] || undefined
}

function renderPart(part, idx) {
  if (part.text === '\n') {
    return <br key={idx} />
  }

  const style = {
    lineHeight: 1.5
  }

  let node = part.text

  for (const tag of part.tags || []) {
    if (tag.name === 'b') {
      style.fontWeight = 'bold'
    } else if (tag.name === 'i') {
      style.fontStyle = 'italic'
    } else if (tag.name === 'u') {
      node = <u>{node}</u>
    } else if (tag.name === 's') {
      node = <s>{node}</s>
    } else if (tag.name === 'color') {
      const colorAttr = tag.attributes?.color
      const c = getTextColor(colorAttr)
      style.color = c || colorAttr
    } else if (tag.name === 'size') {
      const size = tag.attributes?.size
      style.fontSize = `${getSizeRatio(size)}em`
    } else if (tag.name === 'icon') {
      const src = tag.attributes?.src
      return (
        <span key={idx}>
          <img style={{ height: '1.1em', verticalAlign: 'middle' }} src={src} />
        </span>
      )
    } else if (tag.name === 'link') {
      const href = tag.attributes?.href || tag.attributes?.url
      if (href) {
        node = (
          <a href={href} target="_blank" rel="noreferrer">
            {node}
          </a>
        )
      }
    }
  }

  return (
    <span key={idx} style={style}>
      {node}
    </span>
  )
}

export function RichText({ text = '' }) {
  const parts = useMemo(() => new RichTextCompiler().compile(text || ''), [text])

  return <div>{parts.map((p, idx) => renderPart(p, idx))}</div>
}
