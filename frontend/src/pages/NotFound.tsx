import { Link } from 'react-router-dom'
import { AlertTriangle } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="text-center py-16">
      <AlertTriangle className="mx-auto mb-4 text-yellow-500" size={64} />
      <h2 className="text-3xl font-bold text-medical-dark mb-4">404 - Seite nicht gefunden</h2>
      <p className="text-gray-600 mb-6">Die angeforderte Seite existiert nicht.</p>
      <Link to="/" className="btn-primary">
        Zurück zur Startseite
      </Link>
    </div>
  )
}
