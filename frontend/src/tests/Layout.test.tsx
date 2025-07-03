import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../components/Layout';
import { useAuth } from '../context/AuthContext';

// Mock the useAuth hook
vi.mock('../context/AuthContext', () => ({
  useAuth: vi.fn(),
}));

const mockUseAuth = vi.mocked(useAuth);

// Mock react-router-dom functions
const mockNavigate = vi.fn();
let mockLocation = { pathname: '/' };

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => mockLocation,
  };
});

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Layout', () => {
  const mockLogout = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockLocation = { pathname: '/' };
    mockUseAuth.mockReturnValue({
      logout: mockLogout,
      isAuthenticated: true,
      token: 'test-token',
      login: vi.fn(),
    } as any);
  });

  it('renders layout with header and navigation', () => {
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    expect(screen.getByText('PDF Parser Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Upload')).toBeInTheDocument();
    expect(screen.getByText('Documents')).toBeInTheDocument();
    expect(screen.getByText('Search')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('handles logout button click', () => {
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);

    expect(mockLogout).toHaveBeenCalled();
  });

  it('navigates to dashboard when dashboard tab is clicked', () => {
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const dashboardTab = screen.getByRole('tab', { name: /dashboard/i });
    fireEvent.click(dashboardTab);

    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('navigates to upload when upload tab is clicked', () => {
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const uploadTab = screen.getByRole('tab', { name: /upload/i });
    fireEvent.click(uploadTab);

    expect(mockNavigate).toHaveBeenCalledWith('/upload');
  });

  it('navigates to documents when documents tab is clicked', () => {
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const documentsTab = screen.getByRole('tab', { name: /documents/i });
    fireEvent.click(documentsTab);

    expect(mockNavigate).toHaveBeenCalledWith('/documents');
  });

  it('navigates to search when search tab is clicked', () => {
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const searchTab = screen.getByRole('tab', { name: /search/i });
    fireEvent.click(searchTab);

    expect(mockNavigate).toHaveBeenCalledWith('/search');
  });

  it('shows correct active tab for dashboard route', () => {
    mockLocation = { pathname: '/dashboard' };
    
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const dashboardTab = screen.getByRole('tab', { name: /dashboard/i });
    expect(dashboardTab).toHaveAttribute('aria-selected', 'true');
  });

  it('shows correct active tab for upload route', () => {
    mockLocation = { pathname: '/upload' };
    
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const uploadTab = screen.getByRole('tab', { name: /upload/i });
    expect(uploadTab).toHaveAttribute('aria-selected', 'true');
  });

  it('shows correct active tab for documents route', () => {
    mockLocation = { pathname: '/documents' };
    
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const documentsTab = screen.getByRole('tab', { name: /documents/i });
    expect(documentsTab).toHaveAttribute('aria-selected', 'true');
  });

  it('shows correct active tab for search route', () => {
    mockLocation = { pathname: '/search' };
    
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const searchTab = screen.getByRole('tab', { name: /search/i });
    expect(searchTab).toHaveAttribute('aria-selected', 'true');
  });

  it('defaults to dashboard tab for unknown routes', () => {
    mockLocation = { pathname: '/unknown-route' };
    
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const dashboardTab = screen.getByRole('tab', { name: /dashboard/i });
    expect(dashboardTab).toHaveAttribute('aria-selected', 'true');
  });

  it('renders children content correctly', () => {
    const testContent = (
      <div>
        <h1>Test Title</h1>
        <p>Test paragraph</p>
      </div>
    );

    renderWithRouter(
      <Layout>
        {testContent}
      </Layout>
    );

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test paragraph')).toBeInTheDocument();
  });

  it('has correct ARIA labels for accessibility', () => {
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const tabsContainer = screen.getByRole('tablist');
    expect(tabsContainer).toHaveAttribute('aria-label', 'PDF dashboard navigation');

    const dashboardTab = screen.getByRole('tab', { name: /dashboard/i });
    const uploadTab = screen.getByRole('tab', { name: /upload/i });
    const documentsTab = screen.getByRole('tab', { name: /documents/i });
    const searchTab = screen.getByRole('tab', { name: /search/i });

    expect(dashboardTab).toBeInTheDocument();
    expect(uploadTab).toBeInTheDocument();
    expect(documentsTab).toBeInTheDocument();
    expect(searchTab).toBeInTheDocument();
  });
});