import { useState } from 'react';
import { 
  Dialog, DialogTitle, DialogContent, DialogActions, 
  Button, TextField, FormControl, InputLabel, Select, MenuItem,
  Box
} from '@mui/material';
import axios from 'axios';

export default function IncidentForm({ open, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    severity: 'Medium',
    reported_by: ''
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await axios.post('http://localhost:8000/incidents', formData);
      setFormData({ title: '', description: '', severity: 'Medium', reported_by: '' });
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Report New Incident</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && <Box color="error.main" mb={2}>{error}</Box>}
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Title"
            type="text"
            fullWidth
            required
            value={formData.title}
            onChange={handleChange}
            inputProps={{ maxLength: 200 }}
          />
          <TextField
            margin="dense"
            name="description"
            label="Description"
            type="text"
            fullWidth
            multiline
            rows={4}
            value={formData.description}
            onChange={handleChange}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Severity</InputLabel>
            <Select
              name="severity"
              value={formData.severity}
              label="Severity"
              onChange={handleChange}
            >
              <MenuItem value="Low">Low</MenuItem>
              <MenuItem value="Medium">Medium</MenuItem>
              <MenuItem value="High">High</MenuItem>
              <MenuItem value="Critical">Critical</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            name="reported_by"
            label="Reported By"
            type="text"
            fullWidth
            required
            value={formData.reported_by}
            onChange={handleChange}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained">Submit</Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
