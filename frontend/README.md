# Companies Simulator Frontend

React frontend for the Companies Simulator application with Polymarket-inspired design.

## Features

- Company selection sidebar
- Products list with current metrics (market share & revenue)
- Historical charts showing revenue and market share trends over time
- Clean, modern UI similar to Polymarket

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

```powershell
cd frontend
npm install
```

### Development

Start the development server:

```powershell
npm start
```

The app will open at http://localhost:3000

### Build for Production

```powershell
npm run build
```

## API Integration

The frontend expects a REST API at `http://localhost:8000/api` with the following endpoints:

- `GET /api/companies` - List all companies
- `GET /api/companies/:id/products` - Get products for a company
- `GET /api/products/:id/metrics` - Get annual metrics for a product

Set `REACT_APP_API_URL` environment variable to customize the API URL.

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.js
│   │   ├── CompanySelector.js
│   │   ├── ProductsList.js
│   │   └── HistoricalChart.js
│   ├── api.js
│   ├── App.js
│   └── index.js
└── package.json
```
