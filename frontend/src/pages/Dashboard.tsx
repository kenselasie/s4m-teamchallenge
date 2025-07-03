import React from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
} from "@mui/material";
import { CloudUpload, List, Search } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import Layout from "../components/Layout";

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  const quickActions = [
    {
      title: "Upload PDF",
      description: "Upload new PDF documents for processing",
      icon: <CloudUpload sx={{ fontSize: 40 }} />,
      action: () => navigate("/upload"),
      color: "primary" as const,
    },
    {
      title: "View Documents",
      description: "Browse and manage your PDF collection",
      icon: <List sx={{ fontSize: 40 }} />,
      action: () => navigate("/documents"),
      color: "secondary" as const,
    },
    {
      title: "Search Content",
      description: "Search across all PDF documents",
      icon: <Search sx={{ fontSize: 40 }} />,
      action: () => navigate("/search"),
      color: "info" as const,
    },
  ];

  return (
    <Layout>
      <Box>
        {/* Welcome Section */}
        <Box sx={{ mb: 4 }}>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Typography variant="h4" gutterBottom align="center">
              Welcome to the Dashboard
            </Typography>
          </Box>
        </Box>
        {/* Quick Actions */}
        <Typography variant="h5" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {quickActions.map((action, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card
                sx={{
                  height: "100%",
                  cursor: "pointer",
                  "&:hover": {
                    boxShadow: 3,
                    transform: "translateY(-2px)",
                  },
                  transition: "all 0.3s ease",
                }}
                onClick={action.action}
              >
                <CardContent sx={{ textAlign: "center", py: 4 }}>
                  <Box sx={{ color: `${action.color}.main`, mb: 2 }}>
                    {action.icon}
                  </Box>
                  <Typography variant="h6" gutterBottom>
                    {action.title}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    {action.description}
                  </Typography>
                  <Button variant="contained" color={action.color}>
                    Get Started
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Layout>
  );
};

export default Dashboard;
