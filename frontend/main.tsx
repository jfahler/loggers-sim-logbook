import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import Pilots from './Pilots';
import PilotProfile from './PilotProfile'; // create this if not done

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/pilots" element={<Pilots />} />
        <Route path="/pilot/:slug" element={<PilotProfile />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
