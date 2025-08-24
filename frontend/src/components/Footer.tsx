export default function Footer() {
  return (
    <footer className="mt-auto border-t bg-white/80 backdrop-blur dark:bg-slate-900/80 dark:border-slate-800">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-6 py-6 text-sm text-slate-600 dark:text-slate-300 md:flex-row lg:px-8">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-800 dark:text-slate-100">Network Anomaly Detection</span>
          <span className="hidden text-slate-400 md:inline">•</span>
          <span className="text-slate-500 dark:text-slate-400">© {new Date().getFullYear()}</span>
        </div>
        <nav className="flex items-center gap-4">
          <a className="hover:text-slate-900 dark:hover:text-white" href="/" rel="noreferrer">Home</a>
          <a className="hover:text-slate-900 dark:hover:text-white" href="/upload" rel="noreferrer">Upload</a>
          <a className="hover:text-slate-900 dark:hover:text-white" href="/dashboard" rel="noreferrer">Dashboard</a>
          <a className="hover:text-slate-900 dark:hover:text-white" href="/about" rel="noreferrer">About</a>
        </nav>
      </div>
    </footer>
  )
}
