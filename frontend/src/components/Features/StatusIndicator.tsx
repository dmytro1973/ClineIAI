import { useState, useEffect } from 'react'
import { CheckCircle, AlertCircle, Loader2, XCircle } from 'lucide-react'

export default function StatusIndicator() {
  const [status, setStatus] = useState<'loading' | 'healthy' | 'error' | 'offline'>('loading')

  useEffect(() => {
    // Simulate status check
    const timer = setTimeout(() => {
      // Random status for demo
      const randomStatus = Math.random()
      if (randomStatus < 0.3) {
        setStatus('healthy')
      } else if (randomStatus < 0.6) {
        setStatus('error')
      } else {
        setStatus('offline')
      }
    }, 2000)

    return () => clearTimeout(timer)
  }, [])

  const getStatusInfo = () => {
    switch (status) {
      case 'loading':
        return { color: 'text-blue-500', text: 'Lädt...', icon: <Loader2 className="animate-spin" /> }
      case 'healthy':
        return { color: 'text-green-500', text: 'Betriebsbereit', icon: <CheckCircle /> }
      case 'error':
        return { color: 'text-red-500', text: 'Fehler', icon: <AlertCircle /> }
      case 'offline':
        return { color: 'text-gray-500', text: 'Offline', icon: <XCircle /> }
    }
  }

  const { color, text, icon } = getStatusInfo()

  return (
    <div className="flex items-center space-x-2">
      <div className={`${color}`}>{icon}</div>
      <span className="text-sm">{text}</span>
    </div>
  )
}
