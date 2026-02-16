# Code Intelligence Platform - Frontend

## 🚀 Sprint 8: GitHub Integration Complete!

Modern React frontend for the Code Intelligence Platform with GitHub integration, quality analysis, and semantic search.

## ✨ Features Implemented

### Core Features
- ✅ **Home Page** - Hero section, stats, features overview, recent repositories
- ✅ **GitHub Integration** - Import repositories directly from GitHub with validation
- ✅ **Repository Management** - List, filter, and manage all repositories
- ✅ **Repository Details** - Comprehensive view with multiple tabs
- ✅ **File Browser** - Tree-based file navigation with language filters
- ✅ **Code Viewer** - Syntax-highlighted code display with line numbers and real file content
- ✅ **Quality Dashboard** - Complexity and maintainability metrics with charts
- ✅ **Semantic Search** - Natural language code search powered by AI
- ✅ **Responsive Design** - Mobile-friendly UI

### Technical Features
- ✅ **React Router** - Client-side routing with nested routes
- ✅ **React Query** - Efficient API state management
- ✅ **Zustand** - Global state management
- ✅ **TypeScript** - Full type safety
- ✅ **Tailwind CSS** - Modern styling
- ✅ **Prism.js** - Syntax highlighting for Python, C, Assembly, COBOL
- ✅ **Recharts** - Interactive data visualizations
- ✅ **Axios** - HTTP client for API calls
- ✅ **File Content API** - Real-time file content loading from disk

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Layout.tsx       # Main layout with navigation
│   │   ├── FilesTab.tsx     # File tree browser
│   │   ├── QualityTab.tsx   # Quality metrics dashboard
│   │   ├── SecurityTab.tsx  # Security analysis (coming soon)
│   │   ├── SearchBar.tsx    # Search interface
│   │   ├── SearchResult.tsx # Search results display
│   │   └── Stats.tsx        # Statistics display
│   ├── pages/               # Page components
│   │   ├── HomePage.tsx     # Landing page
│   │   ├── RepositoriesPage.tsx      # Repository list
│   │   ├── GitHubImportPage.tsx      # GitHub import form
│   │   ├── RepositoryDetailsPage.tsx # Repository details
│   │   ├── CodeViewerPage.tsx        # Code viewer with real content
│   │   └── SearchPage.tsx            # Search page
│   ├── services/            # API services
│   │   ├── api.ts           # Search API
│   │   ├── githubApi.ts     # GitHub integration API
│   │   └── repositoryApi.ts # Repository API with file content
│   ├── types/               # TypeScript types
│   │   ├── api.ts           # Search types
│   │   ├── github.ts        # GitHub types
│   │   └── repository.ts    # Repository types
│   ├── store/               # State management
│   │   └── useStore.ts      # Zustand store
│   ├── lib/                 # Utilities
│   │   └── utils.ts         # Helper functions
│   ├── router.tsx           # Route configuration
│   ├── App.tsx              # Root component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── package.json
└── README.md
```

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 18+ and npm
- Backend running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start development server:**
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## 🔗 API Integration

The frontend connects to the backend API at `http://localhost:8000/api`

### Endpoints Used

**GitHub Integration:**
- `POST /api/github/validate` - Validate GitHub URL
- `POST /api/github/import` - Import repository
- `GET /api/github/repositories` - List GitHub repos
- `GET /api/github/repositories/{id}` - Get repo details
- `DELETE /api/github/repositories/{id}` - Delete repo
- `GET /api/github/stats` - GitHub statistics

**Repository Management:**
- `GET /api/repositories` - List all repositories
- `GET /api/repositories/{id}` - Get repository
- `GET /api/repositories/{id}/files` - Get files
- `GET /api/repositories/{id}/files/{path}/content` - **Get file content** ✅ NEW!
- `GET /api/repositories/{id}/symbols` - Get symbols

**Quality & Recommendations:**
- `GET /api/recommendations/quality-dashboard` - Quality metrics
- `GET /api/recommendations/complex-functions` - Complex functions
- `GET /api/recommendations/low-maintainability` - Low maintainability

**Search:**
- `POST /api/search/semantic` - Semantic search
- `GET /api/search/stats` - Search statistics

## 🎨 Component Architecture

### Pages
- **HomePage** - Landing page with hero, stats, features
- **RepositoriesPage** - Repository list with filters
- **GitHubImportPage** - GitHub import form with validation
- **RepositoryDetailsPage** - Tabbed interface for repo details
- **CodeViewerPage** - Syntax-highlighted code viewer with real content
- **SearchPage** - Semantic code search

### Components
- **Layout** - Main layout with navigation and footer
- **FilesTab** - Collapsible file tree with language filters
- **QualityTab** - Charts and metrics for code quality
- **SecurityTab** - Security analysis (placeholder)
- **SearchBar** - Search input with filters
- **SearchResult** - Search result cards
- **Stats** - Statistics display

## 🎯 Key Features Explained

### GitHub Integration
1. Real-time URL validation
2. Branch selection
3. Token support for private repos
4. Background processing with status tracking
5. Automatic metadata extraction (stars, language)

### Quality Dashboard
- Complexity distribution (pie chart)
- Maintainability distribution (bar chart)
- Top complex functions
- Average metrics
- Issue counts

### File Browser
- Tree structure with folders
- Collapsible directories
- Language filtering
- File line counts
- Click to view code

### Code Viewer (✨ **Fully Functional**)
- **Real file content** loaded from backend
- Syntax highlighting (Prism.js)
- Line numbers with highlighting
- Symbol sidebar with jump-to-line
- Copy to clipboard
- Complexity indicators
- Breadcrumb navigation
- File size display
- Error handling for missing files

### Semantic Search
- Natural language queries
- Similarity threshold control
- Language filtering
- Real-time results
- Performance metrics

## 🔧 Technologies

- **React 19** - UI framework
- **TypeScript 5** - Type safety
- **Vite** - Build tool (Rolldown-based)
- **React Router 7** - Routing
- **TanStack Query 5** - API state
- **Zustand 5** - Global state
- **Tailwind CSS 3** - Styling
- **Prism.js** - Syntax highlighting
- **Recharts 3** - Data visualization
- **Lucide React** - Icons
- **Axios** - HTTP client

## 📝 Development Notes

### Adding New Routes
1. Create page in `src/pages/`
2. Add route to `src/router.tsx`
3. Update navigation in `src/components/Layout.tsx`

### Adding New API Calls
1. Add types to `src/types/`
2. Add service to `src/services/`
3. Use with React Query in components

### Styling Guidelines
- Use Tailwind utility classes
- Follow dark mode classes: `dark:*`
- Consistent spacing: `gap-*`, `p-*`, `m-*`
- Rounded corners: `rounded-xl`, `rounded-2xl`
- Shadows: `shadow-lg`, `shadow-2xl`

## 🚧 Coming Soon (Sprint 9)

- [ ] Security vulnerability detection
- [ ] Repository-specific search
- [ ] Code diff viewer
- [ ] Export reports (PDF/CSV)
- [ ] User authentication
- [ ] Team collaboration features
- [ ] CI/CD integration
- [ ] Custom analysis rules
- [ ] WebSocket support for real-time updates

## ✅ Sprint 8 - Complete!

All planned features for Sprint 8 have been successfully implemented:
- ✅ GitHub integration with validation
- ✅ File browser with tree structure
- ✅ Code viewer with real file content
- ✅ Quality dashboard with visualizations
- ✅ Semantic search
- ✅ Full responsive design

**No known issues!** The platform is ready for testing and deployment.

## 📦 Dependencies

### Production
```json
{
  "@tanstack/react-query": "^5.90.21",
  "axios": "^1.13.4",
  "clsx": "^2.1.1",
  "lucide-react": "^0.563.0",
  "prismjs": "^1.30.0",
  "react": "^19.2.0",
  "react-dom": "^19.2.0",
  "react-hook-form": "^7.71.1",
  "react-router-dom": "^7.13.0",
  "recharts": "^3.7.0",
  "zod": "^4.3.6",
  "zustand": "^5.0.11"
}
```

### Development
```json
{
  "@types/prismjs": "^1.26.6",
  "@vitejs/plugin-react": "^5.1.1",
  "typescript": "~5.9.3",
  "tailwindcss": "^3.4.19",
  "vite": "npm:rolldown-vite@7.2.5"
}
```

## 🤝 Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ for Sprint 8 - GitHub Integration - COMPLETE!**
