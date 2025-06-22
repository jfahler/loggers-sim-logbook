import SquadronSettings from '../components/SquadronSettings';

export default function Squadron() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Squadron Settings</h1>
        <p className="text-gray-600 mt-2">
          Configure your squadron's pilot callsigns for accurate tracking.
        </p>
      </div>
      
      <SquadronSettings />
    </div>
  );
} 