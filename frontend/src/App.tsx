import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import PlanList from './pages/PlanList';
import PlanDetail from './pages/PlanDetail';
import PlanCreate from './pages/PlanCreate';
import Login from './pages/Login';
import Settings from './pages/Settings';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen" role="status" aria-label="Loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!user?.authenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen" role="status" aria-label="Loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (user?.authenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/plans" element={<PlanList />} />
        <Route path="/plans/new" element={<PlanCreate />} />
        <Route path="/plans/:id" element={<PlanDetail />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;