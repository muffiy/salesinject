import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { WebAppProvider } from '@telegram-apps/sdk-react'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WebAppProvider options={{ acceptCustomStyles: true }}>
      <App />
    </WebAppProvider>
  </React.StrictMode>,
)
