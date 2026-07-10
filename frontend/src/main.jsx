import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import logo from './assets/logo.png'
import './index.css'
import App from './App.jsx'

document.title = 'EnergyShield AI'

const setBrandIcon = (rel, href) => {
  let link = document.querySelector(`link[rel="${rel}"]`)
  if (!link) {
    link = document.createElement('link')
    link.rel = rel
    document.head.append(link)
  }
  link.href = href
}

setBrandIcon('icon', logo)
setBrandIcon('apple-touch-icon', logo)

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
