import { useState } from 'react'
import { Save, AlertCircle, Key, Shield, Info } from 'lucide-react'

export default function Settings() {
  const [settings, setSettings] = useState({
    theme: 'light',
    language: 'de',
    notifications: true,
    autoSave: false
  })

  const [apiSettings, setApiSettings] = useState({
    apiKey: '',
    apiProvider: 'openai',
    useMock: false
  })

  const [status, setStatus] = useState<{ type: 'success' | 'error' | null; message: string }>({
    type: null,
    message: ''
  })

  const [apiStatus, setApiStatus] = useState<{ type: 'success' | 'error' | 'info' | null; message: string }>({
    type: null,
    message: ''
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    const checked = (e.target as HTMLInputElement).checked
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleApiChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    const checked = (e.target as HTMLInputElement).checked
    setApiSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Simulate saving
    setStatus({ type: 'success', message: 'Einstellungen erfolgreich gespeichert!' })
    setTimeout(() => setStatus({ type: null, message: '' }), 3000)
  }

  const handleApiSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      // Simulate API key validation
      if (apiSettings.apiKey.trim() === '' && !apiSettings.useMock) {
        setApiStatus({ type: 'error', message: 'Bitte geben Sie einen API-Schlüssel ein oder aktivieren Sie den Mock-Modus.' })
        return
      }

      // Simulate saving API settings to backend
      const response = await fetch('/api/settings/api-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          api_key: apiSettings.useMock ? '' : apiSettings.apiKey,
          api_provider: apiSettings.apiProvider,
          use_mock: apiSettings.useMock
        })
      })

      if (response.ok) {
        setApiStatus({
          type: 'success',
          message: apiSettings.useMock
            ? 'Mock-Modus aktiviert! Sie können die KI-Funktionen ohne API-Schlüssel testen.'
            : 'API-Schlüssel erfolgreich gespeichert! Die KI verwendet jetzt echte API-Aufrufe.'
        })
      } else {
        setApiStatus({ type: 'error', message: 'Fehler beim Speichern des API-Schlüssels.' })
      }
    } catch (error) {
      setApiStatus({ type: 'error', message: 'Netzwerkfehler. Bitte versuchen Sie es später erneut.' })
    }

    setTimeout(() => setApiStatus({ type: null, message: '' }), 5000)
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-medical-dark">Einstellungen</h2>

      {status.type && (
        <div className={`p-3 rounded-md ${status.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          <AlertCircle className="inline-block mr-2" size={16} />
          {status.message}
        </div>
      )}

      <div className="card space-y-4">
        <h3 className="text-lg font-semibold text-medical-dark">Allgemeine Einstellungen</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
            <select
              name="theme"
              value={settings.theme}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="light">Hell</option>
              <option value="dark">Dunkel</option>
              <option value="system">System</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sprache</label>
            <select
              name="language"
              value={settings.language}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="de">Deutsch</option>
              <option value="en">Englisch</option>
            </select>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="notifications"
              name="notifications"
              checked={settings.notifications}
              onChange={handleChange}
              className="mr-2"
            />
            <label htmlFor="notifications">Benachrichtigungen aktivieren</label>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="autoSave"
              name="autoSave"
              checked={settings.autoSave}
              onChange={handleChange}
              className="mr-2"
            />
            <label htmlFor="autoSave">Automatisch speichern</label>
          </div>

          <button type="submit" className="btn-primary">
            <Save className="inline-block mr-1" size={16} /> Einstellungen speichern
          </button>
        </form>
      </div>

      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-medical-dark flex items-center">
            <Key className="mr-2" size={18} /> KI-API Einstellungen
          </h3>
          {!apiSettings.useMock && (
            <span className="flex items-center text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
              <Shield className="mr-1" size={12} /> Echte API
            </span>
          )}
          {apiSettings.useMock && (
            <span className="flex items-center text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded-full">
              <Info className="mr-1" size={12} /> Mock-Modus
            </span>
          )}
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded-md">
          <div className="flex items-start">
            <Info className="text-blue-600 mr-2 mt-0.5" size={16} />
            <div className="text-sm text-blue-800">
              <p className="font-medium">Wichtig:</p>
              <p>Für echte KI-Funktionen benötigen Sie einen API-Schlüssel von OpenAI oder Anthropic.</p>
              <p className="mt-1">Ohne API-Schlüssel können Sie den Mock-Modus für Tests verwenden.</p>
            </div>
          </div>
        </div>

        <form onSubmit={handleApiSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">API-Anbieter</label>
            <select
              name="apiProvider"
              value={apiSettings.apiProvider}
              onChange={handleApiChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="openai">OpenAI (GPT-4, GPT-3.5)</option>
              <option value="anthropic">Anthropic (Claude 3, Claude 2)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">API-Schlüssel</label>
            <div className="relative">
              <input
                type={apiSettings.useMock ? 'text' : 'password'}
                name="apiKey"
                value={apiSettings.apiKey}
                onChange={handleApiChange}
                disabled={apiSettings.useMock}
                placeholder={apiSettings.useMock ? "Mock-Modus - kein Schlüssel benötigt" : "Ihr API-Schlüssel"}
                className="w-full px-3 py-2 border border-gray-300 rounded-md pr-10"
              />
              {!apiSettings.useMock && apiSettings.apiKey && (
                <button
                  type="button"
                  onClick={() => setApiSettings(prev => ({ ...prev, apiKey: '' }))}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  title="Löschen"
                >
                  ×
                </button>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {apiSettings.apiProvider === 'openai'
                ? 'Besorgen Sie Ihren Schlüssel unter: https://platform.openai.com/account/api-keys'
                : 'Besorgen Sie Ihren Schlüssel unter: https://console.anthropic.com/account/keys'}
            </p>
          </div>

          <div className="flex items-center p-3 bg-gray-50 rounded-md">
            <input
              type="checkbox"
              id="useMock"
              name="useMock"
              checked={apiSettings.useMock}
              onChange={handleApiChange}
              className="mr-2"
            />
            <label htmlFor="useMock" className="flex-1">Mock-Modus aktivieren (kein API-Schlüssel benötigt)</label>
          </div>

          <div className="flex gap-2">
            <button type="submit" className="btn-primary flex-1">
              <Save className="inline-block mr-1" size={16} /> API-Einstellungen speichern
            </button>
            <button
              type="button"
              onClick={() => {
                setApiSettings({
                  apiKey: '',
                  apiProvider: 'openai',
                  useMock: false
                })
                setApiStatus({ type: 'info', message: 'Formular zurückgesetzt.' })
                setTimeout(() => setApiStatus({ type: null, message: '' }), 2000)
              }}
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Zurücksetzen
            </button>
          </div>
        </form>

        {apiStatus.type && (
          <div className={`p-3 rounded-md mt-4 ${apiStatus.type === 'success' ? 'bg-green-100 text-green-800' :
                          apiStatus.type === 'error' ? 'bg-red-100 text-red-800' :
                          'bg-blue-100 text-blue-800'}`}>
            {apiStatus.type === 'success' && <Shield className="inline-block mr-2" size={16} />}
            {apiStatus.type === 'error' && <AlertCircle className="inline-block mr-2" size={16} />}
            {apiStatus.type === 'info' && <Info className="inline-block mr-2" size={16} />}
            {apiStatus.message}
          </div>
        )}
      </div>
    </div>
  )
}
