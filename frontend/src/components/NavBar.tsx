import { Link, NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'

export default function NavBar() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-slate-800 ${isActive ? 'text-blue-600 dark:text-blue-400 font-semibold' : 'text-gray-700 dark:text-slate-200'}`

  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('theme') as 'light' | 'dark' | null
    if (saved) return saved
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    return prefersDark ? 'dark' : 'light'
  })

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') root.classList.add('dark')
    else root.classList.remove('dark')
    localStorage.setItem('theme', theme)
  }, [theme])

  return (
    <nav className="border-b bg-white dark:bg-slate-900 dark:border-slate-800">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="text-lg font-bold text-slate-900 dark:text-slate-100">NetSec Anomaly</Link>
        <div className="flex items-center gap-2 text-sm">
          <NavLink to="/" className={linkClass} end>Home</NavLink>
          <NavLink to="/dashboard" className={linkClass}>Dashboard</NavLink>
          <NavLink to="/upload" className={linkClass}>Upload</NavLink>
          <NavLink to="/about" className={linkClass}>About</NavLink>
          <button
            aria-label="Toggle dark mode"
            onClick={() => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))}
            className="ml-2 rounded px-2 py-2 hover:bg-gray-100 dark:hover:bg-slate-800"
            title={theme === 'dark' ? 'Switch to light' : 'Switch to dark'}
          >
            {theme === 'dark' ? (
              <span className="text-yellow-300">☀️</span>
            ) : (
              <span className="text-slate-700">🌙</span>
            )}
          </button>
        </div>
      </div>
    </nav>
  )
}
