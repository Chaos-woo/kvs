# KVs - Advanced Key-Value Store Desktop Application

[![Version](https://img.shields.io/badge/version-0.6.1-blue.svg)](https://github.com/Chaos-woo/kvs)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

KVs is a modern, feature-rich desktop application for managing key-value pairs with advanced search capabilities, data visualization, and comprehensive data management tools. Built with a Python Flask backend and a Tauri + React frontend, it provides a seamless experience for storing, searching, and analyzing key-value data.

## 🚀 Features

### Core Functionality
- **Advanced Key-Value Storage**: Store and manage key-value pairs with support for multiple values per key
- **Full-Text Search (FTS5)**: Powerful search capabilities using SQLite FTS5 for fast and accurate results
- **Multiple Search Modes**: Support for different search strategies (mixed, exact, fuzzy)
- **Data Clustering**: Intelligent key clustering for better data organization and analysis
- **Statistics Dashboard**: Comprehensive statistics and analytics for your data

### User Interface
- **Modern UI**: Clean, intuitive interface built with shadcn/ui components
- **Theme Support**: Light and dark theme modes with system preference detection
- **Tab-Based Navigation**: Organized interface with "快记" (Quick Note) and "快搜" (Quick Search) tabs
- **K-View Explorer**: Advanced data exploration and visualization tool
- **Responsive Design**: Optimized for desktop usage with proper window management

### Data Management
- **Import/Export**: Support for data import and export by jsonl
- **Batch Operations**: Efficient batch deletion and management of multiple records
- **Data Cleanup**: Built-in tools for data maintenance and cleanup
- **Backup & Restore**: Comprehensive data backup and restoration capabilities

### Developer Features
- **Comprehensive Logging**: Detailed API request/response logging with structured output
- **Debug Tools**: Built-in debugging interface for development and troubleshooting
- **RESTful API**: Well-documented REST API for programmatic access
- **Extensive Testing**: Comprehensive test suite covering all major functionality

## 🏗️ Architecture

### Backend (Python + Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite with FTS5 extension for full-text search
- **API Design**: RESTful API with versioning (`/api/v1/`)
- **Logging**: Structured logging with separate API and error logs
- **Services**: Modular service architecture for business logic

### Frontend (Tauri + React)
- **Framework**: React 18 with TypeScript for type safety
- **Desktop**: Tauri framework for native desktop integration
- **UI Components**: shadcn/ui with Radix UI primitives
- **Styling**: Tailwind CSS with custom theming
- **State Management**: React hooks with context API

## 📋 Prerequisites

Before developing and cloning KVs, ensure you have the following installed:

- **Python 3.8+** with pip package manager
- **Node.js 16+** with npm
- **Rust toolchain** (for Tauri)
- **Visual Studio** or **Intellij IDEA** with C++ desktop development workload (Windows)

## 🛠️ Installation & Setup

### Quick Start (Automated Build)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Chaos-woo/kvs.git
   cd kvs
   ```

2. **Run the automated build**:
   ```bash
   build.bat
   ```

   This will:
   - Install all dependencies
   - Build the backend executable
   - Package the frontend application
   - Create a Windows installer

3. **Find the installer**:
   ```
   frontend\src-tauri\target\release\bundle\
   ```

### Development Setup

#### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run development server**:
   ```bash
   python app.py
   ```

   The Flask server will start at `http://localhost:5000`

#### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Run development server**:
   ```bash
   npm run tauri dev
   ```

   For concurrent backend and frontend running and development:
   ```bash
   npm run dev-with-backend
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
FLASK_ENV=development
DATABASE_URL=sqlite:///kvs.db
LOG_LEVEL=INFO
API_VERSION=v1
```

### Database Configuration

The application automatically creates the SQLite database and FTS5 tables on first run. Database files are stored in:
- **Development**: `backend/kvs.db`
- **Production**: Application data directory

### Logging Configuration

Logs are stored in the `backend/logs/` directory:
- `api.log` - API request/response logs
- `error.log` - Error and exception logs
- `frontend.log` - Frontend application logs

## 📖 API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Authentication
Currently, the API does not require authentication for local desktop usage.

### Endpoints

#### Key-Value Operations

**Create Key-Value Pair**
```http
POST /api/v1/kv
Content-Type: application/json

{
  "key": "example_key",
  "values": ["value1", "value2", "value3"]
}
```

**Get All Key-Value Pairs**
```http
GET /api/v1/kv
```

**Get Specific Key-Value Pair**
```http
GET /api/v1/kv/{key_id}
```

**Update Key-Value Pair**
```http
PUT /api/v1/kv/{key_id}
Content-Type: application/json

{
  "key": "updated_key",
  "values": ["new_value1", "new_value2"]
}
```

**Delete Key-Value Pair**
```http
DELETE /api/v1/kv/{key_id}
```

**Batch Delete**
```http
DELETE /api/v1/kv/batch
Content-Type: application/json

{
  "key_ids": [1, 2, 3, 4]
}
```

#### Search Operations

**Search Key-Value Pairs**
```http
GET /api/v1/search?q={query}&mode={search_mode}
```

Parameters:
- `q`: Search query string
- `mode`: Search mode (`mixed`, `key`, `value`)

#### Statistics and Analytics

**Get Statistics**
```http
GET /api/v1/stats
```

**Get Export Statistics**
```http
GET /api/v1/export-stats
```

#### Data Management

**Export Data**
```http
GET /api/v1/export?format={format}
```

**Import Data**
```http
POST /api/v1/import
Content-Type: multipart/form-data

file: [data_file]
```

**Cluster Keys**
```http
POST /api/v1/cluster
Content-Type: application/json

{
  "algorithm": "kmeans",
  "n_clusters": 5
}
```

## 🧪 Testing

### Running Tests

**Backend Tests**:
```bash
cd backend
python -m pytest tests/ -v
```

**Frontend Tests**:
```bash
cd frontend
npm test
```

**Run Specific Test**:
```bash
cd backend
python -m pytest tests/test_key_value.py -v
```

### Test Coverage

The application includes comprehensive tests for:
- API endpoints and responses
- Database operations and models
- Search functionality (FTS5)
- Data import/export
- Clustering algorithms
- Error handling and edge cases
- Frontend components and interactions

## 🚀 Building for Production

### Frontend Build
```bash
cd frontend
npm run tauri build
```

### Backend Build
```bash
cd backend
python build_backend.py
```

### Complete Build Process
```bash
# From project root
build.bat
```

The build process creates:
- **Windows Installer**: `.msi` file for easy installation
- **Portable Executable**: Standalone `.exe` file
- **Application Bundle**: Complete application package

Output location: `frontend\src-tauri\target\release\bundle\`

## 🐛 Troubleshooting

### Common Issues

**Backend Connection Issues**:
- Ensure Python virtual environment is activated
- Check if port 5000 is available
- Verify all dependencies are installed

**Frontend Build Errors**:
- Update Node.js to version 16+
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

**Tauri Build Issues**:
- Ensure Rust toolchain is installed and updated
- Verify Visual Studio C++ tools are installed
- Check WebView2 runtime is available

**Database Issues**:
- Check SQLite database permissions
- Verify FTS5 extension is available
- Review database logs in `backend/logs/`

### Debug Mode

Enable debug logging by setting environment variable:
```bash
set FLASK_ENV=development
```

Access debug interface through the application menu: `View > Debug Logs`

## 📚 Documentation

Additional documentation is available in the `docs/` directory:

- [Logging System](docs/LOGGING.md) - Comprehensive logging documentation
- [Debugging Guide](docs/DEBUGGING.md) - Development and debugging tips
- [Import System](docs/IMPORT_DESIGN.md) - Data import functionality
- [K-View Feature](docs/K_VIEW_IMPLEMENTATION_SUMMARY.md) - Data exploration tool

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure all tests pass: `npm test` and `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write tests for new functionality
- Update documentation for API changes
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Tauri](https://tauri.app/) - Desktop application framework
- [React](https://reactjs.org/) - UI library
- [shadcn/ui](https://ui.shadcn.com/) - UI components
- [SQLite](https://www.sqlite.org/) - Database engine
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework

## 📞 Support

For support, please:
1. Check the [troubleshooting section](#-troubleshooting)
2. Review existing [issues](https://github.com/Chaos-woo/kvs/issues)
3. Create a new issue with detailed information

---

**KVs** - Making key-value data management simple and powerful.