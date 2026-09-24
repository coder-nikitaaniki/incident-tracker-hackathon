import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Paper, Typography, Box, Button, Chip, Divider, CircularProgress
} from '@mui/material';
import axios from 'axios';
import dayjs from 'dayjs';

export default function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchIncident = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/incidents/${id}`);
      setIncident(response.data);
      
      const logsResponse = await axios.get(`http://localhost:8000/incidents/${id}/audit-log`);
      setAuditLogs(logsResponse.data);
      
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
      await axios.patch(`http://localhost:8000/incidents/${id}/status`, { status: newStatus });
      fetchIncident();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update status');
    }
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!incident) return <Typography>Incident not found</Typography>;

  const getNextStatusOptions = (current) => {
    switch(current) {
      case 'Open': return ['Investigating'];
      case 'Investigating': return ['Resolved'];
      case 'Resolved': return ['Closed'];
      default: return [];
    }
  };

  const nextStatuses = getNextStatusOptions(incident.status);

  return (
    <Paper sx={{ p: 4 }}>
      <Button onClick={() => navigate('/')} sx={{ mb: 2 }}>&larr; Back to Dashboard</Button>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Typography variant="h4" gutterBottom>{incident.title}</Typography>
        <Chip label={incident.status} color={incident.status === 'Closed' ? 'default' : 'primary'} />
      </Box>
      
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Typography variant="body2" color="text.secondary">
          ID: #{incident.id}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Reported by: {incident.reported_by}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Created: {dayjs(incident.created_at).format('MMM D, YYYY h:mm A')}
        </Typography>
      </Box>

      <Typography variant="h6" gutterBottom>Description</Typography>
      <Typography variant="body1" paragraph>
        {incident.description || 'No description provided.'}
      </Typography>
      
      <Divider sx={{ my: 3 }} />

      <Box>
        <Typography variant="h6" gutterBottom>Actions</Typography>
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
              No further actions available.
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
                  {dayjs(log.changed_at).format('MMM D, YYYY h:mm A')} by {log.actor}
                </Typography>
                <Typography variant="body1">
                  Status changed {log.old_status ? `from ${log.old_status} ` : ''}to <strong>{log.new_status}</strong>
                </Typography>
              </Box>
            ))}
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No audit logs available. (Only new updates will be tracked).
          </Typography>
        )}
      </Box>
    </Paper>
  );
}
