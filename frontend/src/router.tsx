import { createBrowserRouter, Navigate } from 'react-router-dom';
import App from './App';
import { AnalysisDashboard } from './components/AnalysisDashboard';
// Import other existing components here as needed

export const router = createBrowserRouter([
    {
        path: '/',
        element: <App />,
        children: [
            {
                path: 'analysis/:id',
                element: <AnalysisDashboard />
            },
            // Add other routes here
            {
                path: '*',
                element: <Navigate to="/" replace />
            }
        ]
    }
]);
