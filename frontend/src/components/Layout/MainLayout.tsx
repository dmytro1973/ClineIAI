import { Link } from 'react-router-dom'
import { Home, MessageSquare, FileText, Settings as SettingsIcon } from 'lucide-react'

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-medical-dark text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">VerdentMoiApp</h1>
          <nav className="flex space-x-4">
            <Link to="/" className="hover:text-medical-light transition-colors">
              <Home className="inline-block mr-1" size={16} /> Dashboard
            </Link>
            <Link to="/chat" className="hover:text-medical-light transition-colors">
              <MessageSquare className="inline-block mr-1" size={16} /> Chat
            </Link>
            <Link to="/documents" className="hover:text-medical-light transition-colors">
              <FileText className="inline-block mr-1" size={16} /> Dokumente
            </Link>
            <Link to="/settings" className="hover:text-medical-light transition-colors">
              <SettingsIcon className="inline-block mr-1" size={16} /> Einstellungen
            </Link>
          </nav>
        </div>
      </header>

      <main className="container mx-auto p-4">
        {children}
      </main>

      <footer className="bg-gray-200 text-gray-600 p-4 text-center mt-8">
        <p>© {new Date().getFullYear()} VerdentMoiApp. Alle Rechte vorbehalten.</p>
      </footer>
    </div>
  )
}
