import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useState } from 'react';
import { Menu, X, LogOut, Settings, Home, FileText, PlusCircle } from 'lucide-react';

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/plans', label: 'Plans', icon: FileText },
    { path: '/plans/new', label: 'New Plan', icon: PlusCircle },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="layout">
      <aside className={`sidebar ${mobileMenuOpen ? 'mobile-open' : ''}`} role="navigation" aria-label="Main navigation">
        <div className="sidebar-header">
          <h1 className="logo">Beacon Station</h1>
          <button
            className="sidebar-close"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close sidebar"
          >
            <X size={20} />
          </button>
        </div>
        <nav className="sidebar-nav">
          <ul role="list">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
              return (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    className={`nav-link ${isActive ? 'active' : ''}`}
                    onClick={() => setMobileMenuOpen(false)}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <Icon size={20} aria-hidden="true" />
                    <span>{item.label}</span>
                  </NavLink>
                </li>
              );
            })}
          </ul>
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <span className="user-email">{user?.email || 'Unknown'}</span>
            <span className="user-roles">{user?.roles?.join(', ') || 'viewer'}</span>
          </div>
          <button onClick={logout} className="logout-btn" aria-label="Log out">
            <LogOut size={18} aria-hidden="true" />
            <span>Log out</span>
          </button>
        </div>
      </aside>

      <header className="header" role="banner">
        <button
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(true)}
          aria-label="Open menu"
          aria-expanded={mobileMenuOpen}
        >
          <Menu size={24} aria-hidden="true" />
        </button>
        <h2 className="page-title">{getPageTitle(location.pathname)}</h2>
      </header>

      <main className="main-content" role="main">
        <Outlet />
      </main>

      {mobileMenuOpen && (
        <div className="sidebar-overlay" onClick={() => setMobileMenuOpen(false)} aria-hidden="true" />
      )}
    </div>
  );
}

function getPageTitle(pathname: string): string {
  if (pathname === '/') return 'Dashboard';
  if (pathname === '/plans') return 'Plans';
  if (pathname.startsWith('/plans/') && pathname !== '/plans/new') return 'Plan Detail';
  if (pathname === '/plans/new') return 'New Plan';
  if (pathname === '/settings') return 'Settings';
  return 'Beacon Station';
}