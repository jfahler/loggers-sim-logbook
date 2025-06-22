import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { Navigation } from './src/components/Navigation';
import { Dashboard } from './src/pages/Dashboard';
import { Flights } from './src/pages/Flights';
import { Pilots } from './src/pages/Pilots';
import { Upload } from './src/pages/Upload';
import Squadron from './src/pages/Squadron';

const queryClient = new QueryClient();

function AppInner() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/flights" element={<Flights />} />
            <Route path="/pilots" element={<Pilots />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/squadron" element={<Squadron />} />
          </Routes>
        </main>
        <Toaster />
      </div>
    </Router>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppInner />
    </QueryClientProvider>
  );
}
