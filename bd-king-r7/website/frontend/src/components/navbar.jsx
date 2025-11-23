import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, Brain, MessageSquare, Star, User, Code, Book, Mail } from 'lucide-react'
import './Navbar.css'

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Home', icon: Brain },
    { path: '/chat', label: 'Chat', icon: MessageSquare },
    { path: '/features', label: 'Features', icon: Star },
    { path: '/about', label: 'About', icon: User },
    { path: '/api-docs', label: 'API', icon: Code },
    { path: '/blog', label: 'Blog', icon: Book },
    { path: '/contact', label: 'Contact', icon: Mail }
  ]

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <Brain className="brand-icon" />
          <span>BD-King-R7</span>
        </Link>

        <div className={`navbar-menu ${isMobileMenuOpen ? 'active' : ''}`}>
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`navbar-item ${location.pathname === item.path ? 'active' : ''}`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </div>

        <button
          className="navbar-toggle"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        >
          {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
    </nav>
  )
}

export default Navbar