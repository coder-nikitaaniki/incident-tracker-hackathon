import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { CssBaseline, Container, AppBar, Toolbar, Typography } from '@mui/material';
import Dashboard from './pages/Dashboard';
import IncidentDetail from './pages/IncidentDetail';

function App() {
  return (
    <BrowserRouter>
      <CssBaseline />
      <AppBar position="static" sx={{ mb: 4 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }} style={{cursor: 'pointer'}} onClick={() => window.location.href='/'}>
            Incident Tracker
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/incident/:id" element={<IncidentDetail />} />
        </Routes>
      </Container>
    </BrowserRouter>
  );
}

export default App;
