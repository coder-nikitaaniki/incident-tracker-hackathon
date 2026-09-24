import { useState, useEffect } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, FormControl, InputLabel, Select, MenuItem, Box, Alert } from '@mui/material';
import axios from 'axios';

export default function IncidentForm({ open, onClose, onSuccess, initialData = null }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    severity: 'Medium',
    reported_by: '',
    assigned_to: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        title: initialData.title || '',
        description: initialData.description || '',
        severity: initialData.severity || 'Medium',
        reported_by: initialData.reported_by || '',
        assigned_to: initialData.assigned_to || ''
      });
    } else {
      setFormData({
        title: '',
        description: '',
        severity: 'Medium',
        reported_by: '',
        assigned_to: ''
      });
    }
  }, [initialData, open]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (initialData) {
        await axios.put(`http://localhost:8000/incidents/${initialData.id}`, formData);
      } else {
        await axios.post('http://localhost:8000/incidents', formData);
      }
      onSuccess();
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError("An error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{initialData ? 'Edit Incident' : 'Report New Incident'}</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Title"
              required
              fullWidth
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
            />
            <TextField
              label="Description"
              multiline
              rows={3}
              fullWidth
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
            />
            <FormControl fullWidth>
              <InputLabel>Severity</InputLabel>
              <Select
                value={formData.severity}
                label="Severity"
                onChange={(e) => setFormData({...formData, severity: e.target.value})}
              >
                <MenuItem value="Critical">Critical</MenuItem>
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="Low">Low</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Reported By"
              required
              fullWidth
              value={formData.reported_by}
              disabled={!!initialData} // Usually can't change original reporter
              onChange={(e) => setFormData({...formData, reported_by: e.target.value})}
            />
            <TextField
              label="Assigned To"
              fullWidth
              value={formData.assigned_to}
              onChange={(e) => setFormData({...formData, assigned_to: e.target.value})}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Saving...' : (initialData ? 'Update' : 'Submit')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
