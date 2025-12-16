const express = require('express');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const fetch = require('node-fetch');

const app = express();
const PORT = process.env.PORT || 3000;

// Backend port (FastAPI). 8000 is excluded on some Windows setups (WinError 10013).
const BACKEND_PORT = process.env.BACKEND_PORT || 9000;

// Middleware
app.use(express.json());
app.use(express.static('frontend/dist'));

// API to check if backend is running
app.get('/api/backend-status', async (req, res) => {
    try {
        // Check if backend directory exists
        if (!fs.existsSync('backend')) {
            return res.json({ status: 'backend-missing', message: 'Backend directory not found' });
        }

        // Check if backend has app directory
        if (!fs.existsSync('backend/app')) {
            return res.json({ status: 'backend-incomplete', message: 'Backend app directory not found' });
        }

        // Check if main.py exists
        if (!fs.existsSync('backend/app/main.py')) {
            return res.json({ status: 'backend-incomplete', message: 'Backend main.py not found' });
        }

        res.json({ status: 'backend-ready', message: 'Backend is ready to start' });
    } catch (error) {
        res.status(500).json({ status: 'error', message: error.message });
    }
});

// API to start backend
app.post('/api/start-backend', async (req, res) => {
    try {
        // Check if backend is already running
        const { stdout } = await execAsync(`netstat -ano | findstr :${BACKEND_PORT}`);
        if (stdout) {
            return res.json({ status: 'already-running', message: 'Backend is already running' });
        }

        // Start backend
        const backendProcess = exec(`cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port ${BACKEND_PORT}`, {
            cwd: __dirname,
            detached: true
        });

        backendProcess.stdout.on('data', (data) => {
            console.log(`Backend: ${data}`);
        });

        backendProcess.stderr.on('data', (data) => {
            console.error(`Backend Error: ${data}`);
        });

        // Wait a bit for backend to start
        await new Promise(resolve => setTimeout(resolve, 5000));

        res.json({ status: 'started', message: 'Backend started successfully' });
    } catch (error) {
        res.status(500).json({ status: 'error', message: error.message });
    }
});

// API to check backend health
app.get('/api/backend-health', async (req, res) => {
    try {
        const response = await fetch(`http://localhost:${BACKEND_PORT}/api/health`);
        const data = await response.json();
        res.json(data);
    } catch (error) {
        res.status(500).json({ status: 'error', message: 'Backend not responding' });
    }
});

// Serve frontend
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'frontend', 'dist', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Web server running on port ${PORT}`);
    console.log(`Access the application at http://localhost:${PORT}`);
});
