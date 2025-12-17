import { useState } from 'react'
import { Send, Brain, Stethoscope, FileText, HelpCircle } from 'lucide-react'

interface Message {
  id: number
  text: string
  sender: 'user' | 'ai'
  model?: string
  concepts?: any[]
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: 'Hallo! Ich bin Ihr medizinischer KI-Assistent. Wie kann ich Ihnen helfen?',
      sender: 'ai',
      model: 'medical-ai'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedModel, setSelectedModel] = useState('medical-ai')
  const [analysisMode, setAnalysisMode] = useState<'chat' | 'diagnose' | 'concepts'>('chat')

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const newMessage: Message = {
      id: messages.length + 1,
      text: input,
      sender: 'user' as const
    }

    setMessages([...messages, newMessage])
    setInput('')
    setIsLoading(true)

    try {
      let responseText = 'Entschuldigung, ich konnte keine Antwort generieren.'
      let modelUsed = selectedModel
      let concepts: any[] = []

      if (analysisMode === 'chat') {
        // AI Chat API call
        const chatResponse = await fetch('/api/ai/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: input, model: selectedModel })
        })

        if (chatResponse.ok) {
          const data = await chatResponse.json()
          responseText = data.response
          modelUsed = data.model
        }
      } else if (analysisMode === 'diagnose') {
        // Diagnosis API call
        const diagnosisResponse = await fetch('/api/ai/diagnose', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ symptoms: input })
        })

        if (diagnosisResponse.ok) {
          const data = await diagnosisResponse.json()
          responseText = `Mögliche Diagnosen: ${data.possible_conditions.join(', ')}. Empfohlene Maßnahmen: ${data.recommended_actions.join(', ')}. Vertrauensniveau: ${data.confidence}.`
          concepts = data.medical_concepts
        }
      } else if (analysisMode === 'concepts') {
        // Medical concepts extraction
        const conceptsResponse = await fetch(`/api/ai/medical-concepts?text=${encodeURIComponent(input)}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        })

        if (conceptsResponse.ok) {
          const data = await conceptsResponse.json()
          concepts = data
          responseText = `Medizinische Konzepte gefunden: ${concepts.map(c => c.display).join(', ')}.`
        }
      }

      const aiResponse: Message = {
        id: messages.length + 2,
        text: responseText,
        sender: 'ai' as const,
        model: modelUsed,
        concepts: concepts
      }

      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      const errorMessage: Message = {
        id: messages.length + 2,
        text: 'Entschuldigung, es ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut.',
        sender: 'ai'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-medical-dark">Medizinischer KI-Assistent</h2>

      <div className="flex gap-2 mb-4">
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="medical-ai">Medizinische KI</option>
          <option value="gpt-4">GPT-4</option>
          <option value="claude-3">Claude 3</option>
        </select>

        <div className="flex gap-1">
          <button
            onClick={() => setAnalysisMode('chat')}
            className={`px-3 py-2 rounded-md ${analysisMode === 'chat' ? 'bg-primary-500 text-white' : 'bg-gray-200'}`}
            title="Normaler Chat"
          >
            <Brain size={16} />
          </button>
          <button
            onClick={() => setAnalysisMode('diagnose')}
            className={`px-3 py-2 rounded-md ${analysisMode === 'diagnose' ? 'bg-primary-500 text-white' : 'bg-gray-200'}`}
            title="Diagnosehilfe"
          >
            <Stethoscope size={16} />
          </button>
          <button
            onClick={() => setAnalysisMode('concepts')}
            className={`px-3 py-2 rounded-md ${analysisMode === 'concepts' ? 'bg-primary-500 text-white' : 'bg-gray-200'}`}
            title="Medizinische Konzepte"
          >
            <FileText size={16} />
          </button>
        </div>
      </div>

      <div className="card flex-1 overflow-y-auto max-h-96">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs p-3 rounded-lg ${message.sender === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-800'}`}
              >
                {message.text}
                {message.model && (
                  <div className="text-xs text-gray-500 mt-1">
                    Modell: {message.model}
                  </div>
                )}
                {message.concepts && message.concepts.length > 0 && (
                  <div className="text-xs text-gray-600 mt-1">
                    Konzepte: {message.concepts.map(c => c.display).join(', ')}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={handleSend} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          placeholder={
            analysisMode === 'chat' ? 'Frage an die medizinische KI...' :
            analysisMode === 'diagnose' ? 'Beschreiben Sie Ihre Symptome...' :
            'Text für Konzeptanalyse eingeben...'
          }
          disabled={isLoading}
        />
        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="animate-pulse">...</span>
          ) : (
            <Send size={16} />
          )}
        </button>
      </form>

      <div className="text-xs text-gray-500 mt-2">
        <HelpCircle size={12} className="inline mr-1" />
        Hinweis: Dieser Assistent dient nur zu Informationszwecken und ersetzt keine ärztliche Beratung.
      </div>
    </div>
  )
}
