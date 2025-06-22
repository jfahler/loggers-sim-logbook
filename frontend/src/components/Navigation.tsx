import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Plane, Users, Upload, BarChart3 } from 'lucide-react';
import loggersLogo from '../../public/assets/loggers-logo.png';

const navigation = [
  { name: 'Dashboard', href: '/', icon: BarChart3 },
  { name: 'Flights', href: '/flights', icon: Plane },
  { name: 'Pilots', href: '/pilots', icon: Users },
  { name: 'Upload', href: '/upload', icon: Upload },
];

export function Navigation() {
  const location = useLocation();

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <img src={loggersLogo} alt="Loggers Logo" className="h-8 w-8" />
            <h1 className="text-xl font-bold text-gray-900">Loggers Logbook App</h1>
          </div>
          
          <div className="flex space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
