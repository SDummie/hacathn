import React from 'react';

const CameraView = ({ url }) => {
  return (
    <div className="video-container">
      {url ? (
        <img 
          src={`${process.env.REACT_APP_API_URL}/video_feed?url=${encodeURIComponent(url)}`} 
          alt="Live Stream" 
        />
      ) : (
        <div className="placeholder">
          Enter RTSP URL to begin
        </div>
      )}
    </div>
  );
};

export default CameraView;