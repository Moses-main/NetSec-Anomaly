export default function About() {
  return (
    <div className="mx-auto max-w-6xl p-6 space-y-4">
      <h1 className="text-2xl font-bold">About This Project</h1>
      <p className="text-gray-700">
        This system detects anomalous network behavior using unsupervised learning. It combines
        Isolation Forest (tree-based outlier detection) and an Autoencoder (neural reconstruction error)
        into an ensemble for robust detection.
      </p>
      <ul className="list-disc space-y-1 pl-6 text-gray-700">
        <li><span className="font-semibold">Backend:</span> Python, scikit-learn, TensorFlow/Keras, Flask</li>
        <li><span className="font-semibold">Frontend:</span> React (Vite), Tailwind CSS</li>
        <li><span className="font-semibold">Outputs:</span> JSON report and plots served under <code>/api/*</code> and <code>/results/*</code></li>
      </ul>
      <p className="text-gray-600">
        To view results, run the backend pipeline to generate the <code>results/detection_report.json</code>
        and images, then start the Flask API and the Vite dev server.
      </p>
    </div>
  )
}
