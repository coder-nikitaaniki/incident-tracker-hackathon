import { useState, useEffect } from 'react';
import { 
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, 
  Button, Select, MenuItem, FormControl, InputLabel, Box, Chip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';
import IncidentForm from '../components/IncidentForm';

export default function Dashboard() {
  const [incidents, setIncidents] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [severityFilter, setSeverityFilter] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const navigate = useNavigate();

  const fetchIncidents = async () => {
    try {
      let url = 'http://localhost:8000/incidents?';
      if (statusFilter) url += `status=${statusFilter}&`;
      if (severityFilter) url += `severity=${severityFilter}&`;
      
      const response = await axios.get(url);
      setIncidents(response.data);
    } catch (error) {
      console.error("Error fetching incidents", error);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [statusFilter, severityFilter]);

  const severityColor = (severity) => {
    switch(severity) {
      case 'Critical': return 'error';
      case 'High': return 'warning';
      case 'Medium': return 'info';
      case 'Low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="Open">Open</MenuItem>
              <MenuItem value="Investigating">Investigating</MenuItem>
              <MenuItem value="Resolved">Resolved</MenuItem>
              <MenuItem value="Closed">Closed</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Severity</InputLabel>
            <Select
              value={severityFilter}
              label="Severity"
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="Critical">Critical</MenuItem>
              <MenuItem value="High">High</MenuItem>
              <MenuItem value="Medium">Medium</MenuItem>
              <MenuItem value="Low">Low</MenuItem>
            </Select>
          </FormControl>
        </Box>
        <Button variant="contained" onClick={() => setIsFormOpen(true)}>
          Report Incident
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Reported By</TableCell>
              <TableCell>Created At</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {incidents.map((incident) => (
              <TableRow 
                key={incident.id}
                hover
                onClick={() => navigate(`/incident/${incident.id}`)}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell>{incident.title}</TableCell>
                <TableCell>
                  <Chip label={incident.severity} color={severityColor(incident.severity)} size="small" />
                </TableCell>
                <TableCell>{incident.status}</TableCell>
                <TableCell>{incident.reported_by}</TableCell>
                <TableCell>{dayjs(incident.created_at).format('MMM D, YYYY h:mm A')}</TableCell>
              </TableRow>
            ))}
            {incidents.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center">No incidents found</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <IncidentForm 
        open={isFormOpen} 
        onClose={() => setIsFormOpen(false)} 
        onSuccess={() => {
          setIsFormOpen(false);
          fetchIncidents();
        }}
      />
    </Box>
  );
}
