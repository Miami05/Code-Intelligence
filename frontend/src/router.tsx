import { createBrowserRouter, Navigate } from 'react-router-dom';
import App from './App';
import { HomePage } from './pages/HomePage';
import { RepositoriesPage } from './pages/RepositoriesPage';
import { RepositoryDetailsPage } from './pages/RepositoryDetailsPage';
import { SearchPage } from './pages/SearchPage';
import { GitHubImportPage } from './pages/GitHubImportPage';
import { CodeViewerPage } from './pages/CodeViewerPage';
import { CallGraphFullPage } from './pages/CallGraphFullPage';
import { AnalysisDashboard } from './components/AnalysisDashboard';

export const router = createBrowserRouter([
    {
        path: '/',
        element: <App />,
        children: [
            {
                index: true,
                element: <HomePage />
            },
            {
                path: 'repositories',
                element: <RepositoriesPage />
            },
            {
                path: 'repositories/:id',
                element: <RepositoryDetailsPage />
            },
            {
                path: 'repositories/:id/code/*',
                element: <CodeViewerPage />
            },
            {
                path: 'repositories/:id/call-graph',
                element: <CallGraphFullPage />
            },
            {
                path: 'search',
                element: <SearchPage />
            },
            {
                path: 'import',
                element: <GitHubImportPage />
            },
            {
                path: 'analysis/:id',
                element: <AnalysisDashboard />
            },
            {
                path: '*',
                element: <Navigate to="/" replace />
            }
        ]
    }
]);
