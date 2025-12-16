import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="app">
      <h1>🤖 ClineIAI Playground</h1>
      <p>Verbunden mit StackBlitz + VS Code + Cline</p>
      
      <div className="card">
        <button onClick={() => setCount((c) => c + 1)}>
          Klicks: {count}
        </button>
      </div>
      
      <p className="hint">
        Bearbeite <code>src/App.tsx</code> und teste mit Cline!
      </p>
    </div>
  )
}

export default App
