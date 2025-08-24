import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <main className="relative isolate min-h-[calc(100vh-64px)] w-full overflow-hidden bg-gradient-to-br from-slate-50 via-white to-indigo-50">{/* 64px approx navbar height */}
      {/* Decorative blurred gradients */}
      <div className="pointer-events-none absolute -left-20 -top-20 h-72 w-72 rounded-full bg-indigo-300/20 blur-3xl" />
      <div className="pointer-events-none absolute -right-24 bottom-10 h-80 w-80 rounded-full bg-blue-300/20 blur-3xl" />

      <div className="mx-auto flex h-full max-w-7xl items-center px-6 py-12 lg:px-8">
        <div className="grid w-full items-center gap-12 lg:grid-cols-2">
          {/* Copy */}
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700">
              <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-indigo-500" />
              Real‑time Network Insights
            </div>
            <h1 className="mt-4 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
              Detect anomalies in your network traffic with confidence
            </h1>
            <p className="mt-5 max-w-xl text-base leading-7 text-slate-600 sm:text-lg">
              Unsupervised ensemble of Isolation Forest and Autoencoder, complete with dashboards, metrics, and visualizations.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/upload"
                className="rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
              >
                Upload Dataset
              </Link>
              <Link
                to="/dashboard"
                className="rounded-lg border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-800 shadow-sm transition hover:bg-slate-50"
              >
                View Dashboard
              </Link>
            </div>

            {/* Quick features */}
            <div className="mt-10 grid max-w-xl grid-cols-2 gap-4 text-sm text-slate-700 sm:grid-cols-3">
              <div className="rounded-lg border bg-white/70 p-3 shadow-sm">
                <div className="font-semibold">Isolation Forest</div>
                <div className="mt-1 text-xs text-slate-500">Tree-based outlier detection</div>
              </div>
              <div className="rounded-lg border bg-white/70 p-3 shadow-sm">
                <div className="font-semibold">Autoencoder</div>
                <div className="mt-1 text-xs text-slate-500">Reconstruction error thresholding</div>
              </div>
              <div className="rounded-lg border bg-white/70 p-3 shadow-sm">
                <div className="font-semibold">Ensemble</div>
                <div className="mt-1 text-xs text-slate-500">Majority vote robustness</div>
              </div>
            </div>
          </div>

          {/* Visual placeholder */}
          <div className="relative">
            <div className="mx-auto w-full max-w-xl rounded-2xl border bg-white/80 p-4 shadow-xl backdrop-blur">
              <div className="aspect-[16/10] w-full overflow-hidden rounded-xl border bg-gradient-to-br from-indigo-600 via-blue-500 to-cyan-400">
                {/* Faux chart grid */}
                <div className="h-full w-full bg-[radial-gradient(circle_at_1px_1px,_rgba(255,255,255,0.2)_1px,_transparent_1px)] bg-[length:24px_24px]" />
              </div>
              <div className="mt-4 grid grid-cols-3 gap-3 text-xs">
                <div className="rounded-lg border bg-white p-3 text-center font-medium text-slate-700">IF Scores</div>
                <div className="rounded-lg border bg-white p-3 text-center font-medium text-slate-700">AE Errors</div>
                <div className="rounded-lg border bg-white p-3 text-center font-medium text-slate-700">Comparison</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
