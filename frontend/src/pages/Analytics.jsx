import { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Button, CircularProgress } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await axios.get('http://localhost:8000/incidents/analytics');
        setData(res.data.data); // Fixed: unpacking wrapped success response
      } catch (err) {
        console.error("Failed to fetch analytics", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) return <CircularProgress />;
  if (!data) return <Typography>Error loading analytics.</Typography>;

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <Box>
      <Button variant="outlined" onClick={() => navigate('/')} sx={{ mb: 3 }}>
        &larr; Back to Dashboard
      </Button>
      <Typography variant="h4" gutterBottom>Incident Analytics</Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <Typography variant="h6" color="text.secondary">Avg Resolution Time</Typography>
            <Typography variant="h3" color="primary">{data.avg_resolution_hours} hrs</Typography>
            <Typography variant="body2" color="text.secondary">For closed incidents</Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 300 }}>
            <Typography variant="h6" gutterBottom>Incidents Per Day (Last 7 Days)</Typography>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.daily_counts}>
                <XAxis dataKey="date" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 300 }}>
            <Typography variant="h6" gutterBottom>Incidents By Severity</Typography>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.severity_counts} dataKey="count" nameKey="severity" cx="50%" cy="50%" outerRadius={80} label>
                  {data.severity_counts.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 300 }}>
            <Typography variant="h6" gutterBottom>Incidents By Status</Typography>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.status_counts}>
                <XAxis dataKey="status" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#9c27b0" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
