import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

export default function Upload() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [logError, setLogError] = useState<string | null>(null)
  const navigate = useNavigate()
  const pollRef = useRef<number | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    if (!file) {
      setError('Please choose a CSV file')
      return
    }
    const isCsv = file && (file.name.toLowerCase().endsWith('.csv') || file.type === 'text/csv')
    if (!isCsv) {
      setError('Only .csv files are accepted')
      return
    }
    const form = new FormData()
    form.append('file', file)
    setLoading(true)
    startLogPolling()
    try {
      const res = await fetch('/api/upload', { method: 'POST', body: form })
      const ct = res.headers.get('content-type') || ''
      let data: any = null
      if (ct.includes('application/json')) {
        data = await res.json()
        if (!res.ok) throw new Error(data?.error || `Upload failed (${res.status})`)
        setResult(data)
        // Redirect to dashboard after brief delay so user sees success briefly
        setTimeout(() => navigate('/dashboard'), 600)
      } else {
        // Likely an HTML error page (e.g., Vite index.html when backend is down)
        const text = await res.text()
        const snippet = text.slice(0, 200).replace(/\s+/g, ' ')
        throw new Error(`Unexpected non-JSON response (${res.status}). Is the backend running at 127.0.0.1:5000? Details: ${snippet}`)
      }
    } catch (err: any) {
      setError(err.message || 'Upload failed')
    } finally {
      setLoading(false)
      stopLogPolling()
    }
  }

  const fetchLogs = async () => {
    try {
      setLogError(null)
      const r = await fetch('/api/logs?tail=300')
      if (!r.ok) throw new Error('Failed to fetch logs')
      const data = await r.json()
      if (Array.isArray(data.lines)) setLogs(data.lines)
    } catch (e: any) {
      setLogError(e.message)
    }
  }

  const startLogPolling = () => {
    stopLogPolling()
    // Fetch immediately and then poll
    fetchLogs()
    pollRef.current = window.setInterval(fetchLogs, 1500)
  }

  const stopLogPolling = () => {
    if (pollRef.current) {
      window.clearInterval(pollRef.current)
      pollRef.current = null
    }
  }

  useEffect(() => {
    return () => stopLogPolling()
  }, [])

  return (
    <div className="mx-auto max-w-3xl p-6 text-slate-900 dark:text-slate-100">
      <h1 className="mb-2 text-2xl font-bold tracking-tight">Upload Dataset</h1>
      <p className="mb-4 text-sm text-gray-600 dark:text-slate-400">Upload a CSV with the expected columns. After processing, view results on the Dashboard.</p>

      <form onSubmit={onSubmit} className="rounded-lg border bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <input
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="mb-3 block w-full text-sm"
        />
        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={loading}
            className="rounded bg-indigo-600 px-4 py-2 text-white shadow-sm transition hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Processing…' : 'Upload & Run'}
          </button>
          <Link to="/dashboard" className="text-indigo-700 underline dark:text-indigo-400">Go to Dashboard</Link>
        </div>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </form>

      {result && (
        <div className="mt-6 rounded-lg border bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h2 className="mb-2 text-lg font-semibold">Result</h2>
          <p className="text-sm text-gray-600 dark:text-slate-400">File: <span className="font-mono">{result.filename}</span></p>
          {result.report?.summary && (
            <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded bg-gray-50 p-3 dark:bg-slate-800">
                <div className="text-xs text-gray-500 dark:text-slate-400">Total Samples</div>
                <div className="text-lg font-semibold">{result.report?.summary?.total_samples}</div>
              </div>
              <div className="rounded bg-gray-50 p-3 dark:bg-slate-800">
                <div className="text-xs text-gray-500 dark:text-slate-400">Anomalies</div>
                <div className="text-lg font-semibold">{result.report?.summary?.anomalies_detected?.ensemble}</div>
              </div>
              <div className="rounded bg-gray-50 p-3 dark:bg-slate-800">
                <div className="text-xs text-gray-500 dark:text-slate-400">Timestamp</div>
                <div className="text-sm">{result.report?.summary?.timestamp}</div>
              </div>
            </div>
          )}

          {Array.isArray(result.images) && result.images.length > 0 && (
            <div className="mt-4">
              <h3 className="mb-2 font-medium">Generated Charts</h3>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {result.images.map((name: string) => (
                  <img key={name} src={`/results/${name}`} alt={name} className="h-auto w-full rounded border bg-gray-50 dark:bg-slate-800 dark:border-slate-700" />
                ))}
              </div>
            </div>
          )}

          <details className="mt-4">
            <summary className="cursor-pointer text-sm text-gray-700 dark:text-slate-300">Raw response</summary>
            <pre className="mt-2 overflow-auto rounded bg-gray-900 p-3 text-xs text-gray-100">{JSON.stringify(result, null, 2)}</pre>
          </details>
        </div>
      )}

      <div className="mt-6 rounded-lg border bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Processing Logs</h2>
          <div className="flex items-center gap-2">
            <button onClick={fetchLogs} className="rounded border px-3 py-1 text-sm dark:border-slate-700">Refresh</button>
            {loading && <span className="text-xs text-indigo-600 dark:text-indigo-400">Live…</span>}
          </div>
        </div>
        {logError && <div className="mb-2 text-sm text-red-600">{logError}</div>}
        <pre className="max-h-72 overflow-auto rounded bg-gray-900 p-3 text-xs leading-5 text-green-100">
{logs.join('\n') || 'No logs yet.'}
        </pre>
      </div>
    </div>
  )
}
