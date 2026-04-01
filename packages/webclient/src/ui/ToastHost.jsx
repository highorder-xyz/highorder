import React, { useEffect, useRef } from 'react'
import { Toast } from 'primereact/toast'

export function ToastHost({ bus }) {
  const toastRef = useRef(null)

  useEffect(() => {
    if (!bus) return
    const unsub = bus.subscribe((msg) => {
      const life = msg.life ?? msg.duration ?? 3000
      toastRef.current?.show({
        severity: msg.severity || 'info',
        summary: msg.summary || msg.title,
        detail: msg.detail || msg.text,
        life
      })
    })
    return () => unsub()
  }, [bus])

  return <Toast ref={toastRef} />
}
