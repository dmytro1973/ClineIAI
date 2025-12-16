import StatusIndicator from '../components/Features/StatusIndicator'

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-medical-dark">Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="card">
          <h3 className="font-semibold mb-2">Backend Status</h3>
          <StatusIndicator />
        </div>

        <div className="card">
          <h3 className="font-semibold mb-2">Schnellstart</h3>
          <p className="text-gray-600">Willkommen bei VerdentMoiApp. Wählen Sie eine Funktion aus dem Menü.</p>
        </div>

        <div className="card">
          <h3 className="font-semibold mb-2">Statistiken</h3>
          <p className="text-gray-600">Hier werden später Statistiken angezeigt.</p>
        </div>
      </div>
    </div>
  )
}
