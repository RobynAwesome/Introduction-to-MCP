import React from 'react'
import { MotionConfig } from 'framer-motion'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { initClientTelemetry } from './telemetry'
import { OperatorProvider } from './operator/OperatorProvider'

initClientTelemetry()

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MotionConfig reducedMotion="user">
      <OperatorProvider>
        <App />
      </OperatorProvider>
    </MotionConfig>
  </React.StrictMode>,
)
