import { useEffect, useState } from "react";

interface Report {
  summary: {
    timestamp: string;
    total_samples: number;
    anomalies_detected: {
      isolation_forest: number | string;
      autoencoder: number | string;
      ensemble: number | string;
    };
    detection_rates: {
      isolation_forest: number;
      autoencoder: number;
      ensemble: number;
    };
  };
  performance_metrics: any;
}

function StatCard({
  label,
  value,
  subtitle,
}: {
  label: string;
  value: string | number;
  subtitle?: string;
}) {
  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div className="text-sm text-gray-500 dark:text-slate-400">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
      {subtitle && (
        <div className="text-xs text-gray-400 dark:text-slate-500">
          {subtitle}
        </div>
      )}
    </div>
  );
}

export default function Dashboard() {
  const [report, setReport] = useState<Report | null>(null);
  const [images, setImages] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch("/api/report");
        if (!r.ok)
          throw new Error(
            "Report not found. Run backend pipeline to generate results."
          );
        const data = await r.json();
        setReport(data);
      } catch (e: any) {
        setError(e.message);
      }

      try {
        const r2 = await fetch("/api/images");
        if (r2.ok) setImages(await r2.json());
      } catch {}
    })();
  }, []);

  return (
    <div className="mx-auto max-w-6xl p-6 space-y-6 text-slate-900 dark:text-slate-100">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Network Anomaly Dashboard</h1>
        <span className="text-sm text-gray-500 dark:text-slate-400">
          Frontend: React + Vite + Tailwind
        </span>
      </header>

      {error && (
        <div className="rounded border border-red-200 bg-red-50 p-3 text-red-700 dark:border-red-800/40 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </div>
      )}

      {report && (
        <section className="space-y-4">
          <div className="text-sm text-gray-500 dark:text-slate-400">
            Last updated: {new Date(report.summary.timestamp).toLocaleString()}
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Total Samples"
              value={report.summary.total_samples}
            />
            <StatCard
              label="IF Anomalies"
              value={report.summary.anomalies_detected.isolation_forest}
              subtitle={
                (report.summary.detection_rates.isolation_forest * 100).toFixed(
                  2
                ) + "%"
              }
            />
            <StatCard
              label="AE Anomalies"
              value={report.summary.anomalies_detected.autoencoder}
              subtitle={
                (report.summary.detection_rates.autoencoder * 100).toFixed(2) +
                "%"
              }
            />
            <StatCard
              label="Ensemble Anomalies"
              value={report.summary.anomalies_detected.ensemble}
              subtitle={
                (report.summary.detection_rates.ensemble * 100).toFixed(2) + "%"
              }
            />
          </div>

          <div className="rounded-lg border bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <h2 className="mb-3 text-lg font-semibold">Performance Metrics</h2>
            {(() => {
              const m: any = report.performance_metrics || {};
              const toPct = (v: any) =>
                typeof v === "number" && isFinite(v)
                  ? (v * 100).toFixed(2) + "%"
                  : String(v);
              const toNum = (v: any) =>
                typeof v === "number" && isFinite(v) ? v.toFixed(3) : String(v);

              // Supervised case: metrics per model
              if (m.isolation_forest && m.autoencoder && m.ensemble) {
                const rows = [
                  { name: "Isolation Forest", k: "isolation_forest" },
                  { name: "Autoencoder", k: "autoencoder" },
                  { name: "Ensemble", k: "ensemble" },
                ];
                return (
                  <div className="overflow-auto">
                    <table className="min-w-full border-separate border-spacing-0 text-sm">
                      <thead>
                        <tr className="text-left text-gray-600 dark:text-slate-400">
                          <th className="border-b px-3 py-2 dark:border-slate-800">
                            Model
                          </th>
                          <th className="border-b px-3 py-2 dark:border-slate-800">
                            Precision
                          </th>
                          <th className="border-b px-3 py-2 dark:border-slate-800">
                            Recall
                          </th>
                          <th className="border-b px-3 py-2 dark:border-slate-800">
                            F1 Score
                          </th>
                          <th className="border-b px-3 py-2 dark:border-slate-800">
                            Accuracy
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {rows.map((r) => (
                          <tr key={r.k}>
                            <td className="border-b px-3 py-2 dark:border-slate-800">
                              {r.name}
                            </td>
                            <td className="border-b px-3 py-2 dark:border-slate-800">
                              {toNum(m[r.k]?.precision)}
                            </td>
                            <td className="border-b px-3 py-2 dark:border-slate-800">
                              {toNum(m[r.k]?.recall)}
                            </td>
                            <td className="border-b px-3 py-2 dark:border-slate-800">
                              {toNum(m[r.k]?.f1_score)}
                            </td>
                            <td className="border-b px-3 py-2 dark:border-slate-800">
                              {toNum(m[r.k]?.accuracy)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                );
              }

              // Unsupervised case: detection_rates + method_agreement
              const dr = m.detection_rates || {};
              return (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                    <div className="rounded bg-gray-50 p-3 dark:bg-slate-800">
                      <div className="text-xs text-gray-500 dark:text-slate-400">
                        IF Detection Rate
                      </div>
                      <div className="text-lg font-semibold">
                        {toPct(dr.isolation_forest)}
                      </div>
                    </div>
                    <div className="rounded bg-gray-50 p-3 dark:bg-slate-800">
                      <div className="text-xs text-gray-500 dark:text-slate-400">
                        AE Detection Rate
                      </div>
                      <div className="text-lg font-semibold">
                        {toPct(dr.autoencoder)}
                      </div>
                    </div>
                    <div className="rounded bg-gray-50 p-3 dark:bg-slate-800">
                      <div className="text-xs text-gray-500 dark:text-slate-400">
                        Ensemble Detection Rate
                      </div>
                      <div className="text-lg font-semibold">
                        {toPct(dr.ensemble)}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div className="rounded bg-gray-50 p-3 dark:bg-slate-800">
                      <div className="text-xs text-gray-500 dark:text-slate-400">
                        Method Agreement (IF vs AE)
                      </div>
                      <div className="text-lg font-semibold">
                        {toPct(m.method_agreement)}
                      </div>
                    </div>
                    <div className="rounded bg-gray-50 p-3 dark:bg-slate-800">
                      <div className="text-xs text-gray-500 dark:text-slate-400">
                        Total Samples (metrics)
                      </div>
                      <div className="text-lg font-semibold">
                        {m.total_samples ?? report.summary.total_samples}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        </section>
      )}

      <section className="rounded-lg border bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <h2 className="mb-3 text-lg font-semibold">Visualizations</h2>
        {images.length === 0 ? (
          <div className="text-sm text-gray-500 dark:text-slate-400">
            No images found in results/. Generate visualizations via the
            backend.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {images.map((img) => (
              <figure
                key={img}
                className="rounded border p-2 dark:border-slate-800"
              >
                <img
                  className="w-full rounded border dark:border-slate-800"
                  src={`/results/${img}`}
                  alt={img}
                />
                <figcaption className="mt-2 text-center text-sm text-gray-600 dark:text-slate-400">
                  {img}
                </figcaption>
              </figure>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
