import React, { useState, useEffect } from 'react';
import CameraView from './components/CameraView';
import AlertFeed from './components/AlertFeed';
import './styles/main.css';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [cameraUrl, setCameraUrl] = useState('');

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL}/alerts`);
        const data = await response.json();
        setAlerts(data);
      } catch (error) {
        console.error("Error fetching alerts:", error);
      }
    };
    
    const interval = setInterval(fetchAlerts, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <h1>AI Security System</h1>
      <div className="main-content">
        <div className="camera-section">
          <input
            type="text"
            placeholder="Enter RTSP URL"
            value={cameraUrl}
            onChange={(e) => setCameraUrl(e.target.value)}
          />
          <CameraView url={cameraUrl} />
        </div>
        <AlertFeed alerts={alerts} />
      </div>
    </div>
  );
}

export default App;