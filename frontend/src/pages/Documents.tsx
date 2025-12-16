import { useState } from 'react'
import { File, Plus, Search, Brain, BarChart2, Eye } from 'lucide-react'

interface Document {
  id: number
  name: string
  date: string
  size: string
  content?: string
}

interface AnalysisResult {
  entities: string[]
  medical_concepts: any[]
  summary: string
  sentiment: string
  language: string
}

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([
    {
      id: 1,
      name: 'Patientenbericht.pdf',
      date: '2023-12-15',
      size: '2.4 MB',
      content: 'Patient leidet unter chronischem Husten und Atemnot. Diagnose: Asthma bronchiale. Behandlung mit Inhalationssteroiden begonnen.'
    },
    {
      id: 2,
      name: 'Laborergebnisse.csv',
      date: '2023-12-10',
      size: '1.2 MB',
      content: 'Blutzucker: 180 mg/dl, HbA1c: 7.2%, Cholesterin: 220 mg/dl. Patient hat Diabetes mellitus Typ 2 und Hypertonie.'
    },
    {
      id: 3,
      name: 'Röntgenbild.jpg',
      date: '2023-11-28',
      size: '3.7 MB',
      content: 'Röntgenaufnahme der Lunge zeigt leichte Verschattungen in den Unterfeldern. Verdacht auf beginnende Pneumonie.'
    }
  ])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [showAnalysis, setShowAnalysis] = useState(false)

  const filteredDocuments = documents.filter(doc =>
    doc.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleAnalyze = async (document: Document) => {
    if (!document.content) return

    setSelectedDocument(document)
    setIsAnalyzing(true)
    setShowAnalysis(true)

    try {
      const response = await fetch('/api/ai/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_text: document.content,
          analysis_type: 'full'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setAnalysisResult(data.analysis)
      }
    } catch (error) {
      console.error('Analysis error:', error)
      setAnalysisResult({
        entities: [],
        medical_concepts: [],
        summary: 'Fehler bei der Analyse. Bitte versuchen Sie es später erneut.',
        sentiment: 'neutral',
        language: 'de'
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-medical-dark">Dokumente & KI-Analyse</h2>

      <div className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Dokumente durchsuchen..."
          />
        </div>
        <button className="btn-primary">
          <Plus size={16} className="inline-block mr-1" /> Hochladen
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="font-semibold mb-2">Dokumentenliste</h3>
          {filteredDocuments.length === 0 ? (
            <p className="text-gray-600">Keine Dokumente gefunden.</p>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Name</th>
                  <th className="text-left p-2">Datum</th>
                  <th className="text-left p-2">Größe</th>
                  <th className="text-left p-2">Aktionen</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocuments.map((doc) => (
                  <tr key={doc.id} className="border-b hover:bg-gray-50">
                    <td className="p-2 flex items-center">
                      <File className="mr-2 text-gray-500" size={16} />{doc.name}
                    </td>
                    <td className="p-2">{doc.date}</td>
                    <td className="p-2">{doc.size}</td>
                    <td className="p-2">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleAnalyze(doc)}
                          className="text-primary-600 hover:text-primary-700"
                          disabled={isAnalyzing}
                          title="KI-Analyse"
                        >
                          <Brain size={16} className="inline" />
                        </button>
                        <button className="text-gray-600 hover:text-gray-700" title="Anzeigen">
                          <Eye size={16} className="inline" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <h3 className="font-semibold mb-2 flex items-center">
            <BarChart2 size={16} className="mr-2" />
            KI-Dokumentenanalyse
          </h3>

          {showAnalysis ? (
            <div className="space-y-4">
              {isAnalyzing ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto mb-2"></div>
                  <p>Analysiere Dokument...</p>
                </div>
              ) : (
                <>
                  {selectedDocument && (
                    <div className="bg-gray-50 p-3 rounded-md">
                      <p className="font-medium">Analysiertes Dokument:</p>
                      <p className="text-sm text-gray-600">{selectedDocument.name}</p>
                    </div>
                  )}

                  {analysisResult ? (
                    <div className="space-y-3">
                      <div>
                        <p className="font-medium text-sm mb-1">Zusammenfassung:</p>
                        <p className="text-sm">{analysisResult.summary}</p>
                      </div>

                      <div>
                        <p className="font-medium text-sm mb-1">Stimmung:</p>
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          analysisResult.sentiment === 'positive' ? 'bg-green-100 text-green-800' :
                          analysisResult.sentiment === 'negative' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {analysisResult.sentiment}
                        </span>
                      </div>

                      <div>
                        <p className="font-medium text-sm mb-1">Entitäten:</p>
                        <div className="flex flex-wrap gap-1">
                          {analysisResult.entities.map((entity, index) => (
                            <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                              {entity}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="font-medium text-sm mb-1">Medizinische Konzepte:</p>
                        {analysisResult.medical_concepts.length > 0 ? (
                          <div className="space-y-2">
                            {analysisResult.medical_concepts.map((concept, index) => (
                              <div key={index} className="p-2 bg-gray-50 rounded">
                                <p className="font-medium text-sm">{concept.display}</p>
                                <p className="text-xs text-gray-600">{concept.system} - {concept.code}</p>
                                {concept.definition && (
                                  <p className="text-xs text-gray-500">{concept.definition}</p>
                                )}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-xs text-gray-500">Keine medizinischen Konzepte gefunden.</p>
                        )}
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">Wählen Sie ein Dokument zur Analyse aus.</p>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="text-gray-500 text-center py-4">
              <p>Wählen Sie ein Dokument aus der Liste aus, um eine KI-Analyse durchzuführen.</p>
              <p className="text-xs mt-2">Die Analyse umfasst OCR, NLP und medizinische Konzepterkennung.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
