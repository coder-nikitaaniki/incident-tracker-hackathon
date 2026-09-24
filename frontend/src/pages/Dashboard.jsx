import { useState, useEffect } from 'react';
import { 
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, 
  Button, Select, MenuItem, FormControl, InputLabel, Box, Chip, Pagination
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import local from 'dayjs/plugin/timezone';
import IncidentForm from '../components/IncidentForm';

dayjs.extend(utc);
dayjs.extend(local);

export default function Dashboard() {
  const [incidents, setIncidents] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('All');
  const [severityFilter, setSeverityFilter] = useState('All');
  const [sortBy, setSortBy] = useState('created_at');
  const [order, setOrder] = useState('desc');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const navigate = useNavigate();

  const fetchIncidents = async () => {
    try {
      let url = `http://localhost:8000/incidents?page=${page}&page_size=10&sort_by=${sortBy}&order=${order}`;
      if (statusFilter && statusFilter !== 'All') url += `&status=${statusFilter}`;
      if (severityFilter && severityFilter !== 'All') url += `&severity=${severityFilter}`;
      
      const response = await axios.get(url);
      setIncidents(response.data.data);
      setTotal(response.data.total);
    } catch (error) {
      console.error("Error fetching incidents", error);
    }
  };

  useEffect(() => {
    fetchIncidents();
    
    let ws;
    let reconnectTimer;
    let isMounted = true;

    const connectWebSocket = () => {
      console.log("Attempting WebSocket connection...");
      ws = new WebSocket('ws://localhost:8000/ws/incidents');
      
      ws.onopen = () => {
        console.log("WebSocket connected successfully!");
      };
      
      ws.onmessage = (event) => {
        console.log("WebSocket message received:", event.data);
        if (event.data === 'update') {
          fetchIncidents();
        }
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected.");
        if (isMounted) {
          // Auto-reconnect after 2 seconds
          reconnectTimer = setTimeout(connectWebSocket, 2000);
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
      };
    };

    connectWebSocket();

    return () => {
      isMounted = false;
      clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, [statusFilter, severityFilter, page, sortBy, order]);

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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', mb: 3, gap: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select value={statusFilter} label="Status" onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}>
              <MenuItem value="All">All</MenuItem>
              <MenuItem value="Open">Open</MenuItem>
              <MenuItem value="Investigating">Investigating</MenuItem>
              <MenuItem value="Resolved">Resolved</MenuItem>
              <MenuItem value="Closed">Closed</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Severity</InputLabel>
            <Select value={severityFilter} label="Severity" onChange={(e) => { setSeverityFilter(e.target.value); setPage(1); }}>
              <MenuItem value="All">All</MenuItem>
              <MenuItem value="Critical">Critical</MenuItem>
              <MenuItem value="High">High</MenuItem>
              <MenuItem value="Medium">Medium</MenuItem>
              <MenuItem value="Low">Low</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Sort By</InputLabel>
            <Select value={sortBy} label="Sort By" onChange={(e) => { setSortBy(e.target.value); setPage(1); }}>
              <MenuItem value="created_at">Date Created</MenuItem>
              <MenuItem value="severity">Severity</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Order</InputLabel>
            <Select value={order} label="Order" onChange={(e) => { setOrder(e.target.value); setPage(1); }}>
              <MenuItem value="desc">Descending</MenuItem>
              <MenuItem value="asc">Ascending</MenuItem>
            </Select>
          </FormControl>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" onClick={() => navigate('/analytics')}>
            Analytics
          </Button>
          <Button variant="contained" onClick={() => setIsFormOpen(true)}>
            Report Incident
          </Button>
        </Box>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Reported By</TableCell>
              <TableCell>Assigned To</TableCell>
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
                <TableCell>{incident.assigned_to || '-'}</TableCell>
                <TableCell>{dayjs(incident.created_at).local().format('MMM D, YYYY h:mm A')}</TableCell>
              </TableRow>
            ))}
            {incidents.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} align="center">No incidents found</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      {total > 10 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination 
            count={Math.ceil(total / 10)} 
            page={page} 
            onChange={(e, value) => setPage(value)} 
            color="primary" 
          />
        </Box>
      )}

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
