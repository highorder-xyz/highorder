import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import i18next from 'i18next'
import { initReactI18next } from 'react-i18next'
import './App.css'

function App() {
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    // Initialize i18next
    i18next
      .use(initReactI18next)
      .init({
        resources: {
          en: {
            translation: {
              // Add translations here
            }
          }
        },
        lng: "en",
        fallbackLng: "en",
        interpolation: {
          escapeValue: false
        }
      })
      .then(() => {
        setIsLoading(false)
      })
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        <div className="flex flex-1">
          <main className="flex-1 p-4">
            <Routes>
              <Route path="/" element={<h1>Home</h1>} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App