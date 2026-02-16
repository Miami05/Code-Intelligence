import { createBrowserRouter } from 'react-router-dom';
import App from './App';
import HomePage from './pages/HomePage';
import RepositoriesPage from './pages/RepositoriesPage';
import GitHubImportPage from './pages/GitHubImportPage';
import RepositoryDetailsPage from './pages/RepositoryDetailsPage';
import CodeViewerPage from './pages/CodeViewerPage';
import SearchPage from './pages/SearchPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'repositories',
        element: <RepositoriesPage />,
      },
      {
        path: 'repositories/import',
        element: <GitHubImportPage />,
      },
      {
        path: 'repositories/:id',
        element: <RepositoryDetailsPage />,
      },
      {
        path: 'repositories/:id/files/*',
        element: <CodeViewerPage />,
      },
      {
        path: 'search',
        element: <SearchPage />,
      },
    ],
  },
]);
