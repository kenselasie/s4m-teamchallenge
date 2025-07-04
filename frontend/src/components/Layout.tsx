import React from "react";
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Tabs,
  Tab,
} from "@mui/material";
import {
  CloudUpload,
  List,
  Search,
  PictureAsPdf,
  Home,
} from "@mui/icons-material";
import { useAuth } from "../context/AuthContext";
import { useNavigate, useLocation } from "react-router-dom";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Get current tab value based on route
  const getCurrentTab = () => {
    switch (location.pathname) {
      case "/":
      case "/dashboard":
        return 0;
      case "/upload":
        return 1;
      case "/documents":
        return 2;
      case "/search":
        return 3;
      default:
        return 0;
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    switch (newValue) {
      case 0:
        navigate("/dashboard");
        break;
      case 1:
        navigate("/upload");
        break;
      case 2:
        navigate("/documents");
        break;
      case 3:
        navigate("/search");
        break;
    }
  };

  return (
    <Box sx={{ flexGrow: 1, minHeight: "100vh" }}>
      <AppBar position="static">
        <Toolbar>
          <PictureAsPdf sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            PDF Parser Dashboard
          </Typography>
          <Button color="inherit" onClick={logout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      {/* Navigation Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Container maxWidth="lg">
          <Tabs
            value={getCurrentTab()}
            onChange={handleTabChange}
            aria-label="PDF dashboard navigation"
          >
            <Tab icon={<Home />} label="Dashboard" iconPosition="start" />
            <Tab icon={<CloudUpload />} label="Upload" iconPosition="start" />
            <Tab icon={<List />} label="Documents" iconPosition="start" />
            <Tab icon={<Search />} label="Search" iconPosition="start" />
          </Tabs>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ mt: 3, pb: 4 }}>
        {children}
      </Container>
    </Box>
  );
};

export default Layout;
