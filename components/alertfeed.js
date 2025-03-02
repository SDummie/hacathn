import React from 'react';

const AlertFeed = ({ alerts }) => {
  return (
    <div className="alert-feed">
      <h2>Security Alerts</h2>
      <div className="alert-list">
        {alerts.map((alert, index) => (
          <div key={index} className="alert-card">
            <div className="alert-header">
              <span className="alert-type">{alert.label}</span>
              <span className="confidence">{alert.confidence.toFixed(2)}</span>
            </div>
            <div className="timestamp">
              {new Date(alert.timestamp).toLocaleString()}
            </div>
            <img 
              src={`data:image/jpeg;base64,${alert.image}`}
              alt="Alert Snapshot"
              className="alert-image"
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default AlertFeed;