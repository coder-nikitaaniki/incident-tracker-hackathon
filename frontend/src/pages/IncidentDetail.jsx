import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Typography, Box, Paper, Button, Divider, CircularProgress } from '@mui/material';
import axios from 'axios';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import local from 'dayjs/plugin/timezone';
import IncidentForm from '../components/IncidentForm';

dayjs.extend(utc);
dayjs.extend(local);

export default function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditOpen, setIsEditOpen] = useState(false);

  const fetchIncident = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/incidents/${id}`);
      setIncident(response.data.data);
      
      const logsResponse = await axios.get(`http://localhost:8000/incidents/${id}/audit-log`);
      setAuditLogs(logsResponse.data.data);
      
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch incident details');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncident();
  }, [id]);

  const handleStatusChange = async (newStatus) => {
    try {
      // Hardcoded 'Current User' as actor for now, could be dynamic
      await axios.patch(`http://localhost:8000/incidents/${id}/status`, { 
        status: newStatus,
        actor: "Current User" 
      });
      fetchIncident();
    } catch (err) {
      alert("Error updating status: " + (err.response?.data?.error || "Unknown error"));
    }
  };

  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to delete this incident?")) {
      try {
        await axios.delete(`http://localhost:8000/incidents/${id}`);
        navigate('/');
      } catch (err) {
        alert("Error deleting: " + (err.response?.data?.error || "Unknown error"));
      }
    }
  };

  if (loading) return <CircularProgress />;
  if (error || !incident) return <Typography color="error">{error || 'Not found'}</Typography>;

  const getNextValidStatuses = (current) => {
    const transitions = {
      "Open": ["Investigating"],
      "Investigating": ["Resolved"],
      "Resolved": ["Closed"],
      "Closed": []
    };
    return transitions[current] || [];
  };

  const nextStatuses = getNextValidStatuses(incident.status);

  return (
    <Paper sx={{ p: 4 }}>
      <Button onClick={() => navigate('/')} sx={{ mb: 2 }}>
        &larr; Back to Dashboard
      </Button>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" gutterBottom>{incident.title}</Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            ID: #{incident.id} &nbsp;|&nbsp; Reported by: {incident.reported_by} &nbsp;|&nbsp; Assigned to: {incident.assigned_to || 'Unassigned'}
          </Typography>
          <Typography variant="subtitle2" color="text.secondary">
            Created: {dayjs(incident.created_at).local().format('MMM D, YYYY h:mm A')}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" size="small" onClick={() => setIsEditOpen(true)}>Edit</Button>
          <Button variant="outlined" color="error" size="small" onClick={handleDelete}>Delete</Button>
        </Box>
      </Box>

      <Divider sx={{ my: 3 }} />

      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>Description</Typography>
        <Typography variant="body1">
          {incident.description || 'No description provided.'}
        </Typography>
      </Box>

      <Divider sx={{ my: 3 }} />

      <Box>
        <Typography variant="h6" gutterBottom>Actions (Current Status: {incident.status})</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {nextStatuses.map(status => (
            <Button 
              key={status}
              variant="contained" 
              onClick={() => handleStatusChange(status)}
            >
              Mark as {status}
            </Button>
          ))}
          {nextStatuses.length === 0 && (
            <Typography variant="body2" color="text.secondary">
              No further status actions available.
            </Typography>
          )}
        </Box>
      </Box>

      <Divider sx={{ my: 3 }} />

      <Box>
        <Typography variant="h6" gutterBottom>Audit Log</Typography>
        {auditLogs.length > 0 ? (
          <Box sx={{ mt: 2 }}>
            {auditLogs.map(log => (
              <Box key={log.id} sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {dayjs(log.changed_at).local().format('MMM D, YYYY h:mm A')} by {log.actor}
                </Typography>
                <Typography variant="body1">
                  Status changed {log.old_status ? `from ${log.old_status} ` : ''}to <strong>{log.new_status}</strong>
                </Typography>
              </Box>
            ))}
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No audit logs available.
          </Typography>
        )}
      </Box>

      <IncidentForm 
        open={isEditOpen} 
        onClose={() => setIsEditOpen(false)} 
        onSuccess={() => {
          setIsEditOpen(false);
          fetchIncident();
        }}
        initialData={incident}
      />
    </Paper>
  );
}
