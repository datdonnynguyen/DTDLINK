# Week 9 - MUI React Project with Router

In this guide, we'll continue from the **"MUI React Project Setup Guide"** and focus on adding routing using **React Router**, including an **About page** accessible from both the **Drawer** and **AppBar**.

[TOC]

---



## 1. Step 1: Install React Router

First, you need to install **React Router** if you haven’t done so already.

```
npm install react-router-dom
```



## 2. Step 2: Set up Routing

Next, you’ll set up routing in your app by wrapping it in BrowserRouter. You’ll also define routes for the **About** page.

In **App.js**:

```react
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
```

In **index,js**:

```react
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router } from 'react-router-dom'; // Ensure this is added
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <Router>
      <App />
    </Router>
  </React.StrictMode>
);
```



## 3. Step 3: Create the About Page:

Create a simple **About page** component inside **App.js** that can be accessed via routing.

```react
// About page component
function About() {
  return (
    <Container>
      <Typography variant="h2" component="h1" gutterBottom>
        About Us
      </Typography>
      <Typography variant="h5" component="h2" gutterBottom>
        This is the About page. Here, you can add more information about the project or your team.
      </Typography>
    </Container>
  );
}
```



## 4. Step 4: Define Routes

In **App.js**, wrap the app content with Routes and Route components to define paths for the **Home** and **About** pages. The **Home** page remains the default route (/), while a new route is added for the **About** page.

```react
<Routes>
  <Route path="/" element={
    <Container component="main" sx={{ mt: 8, mb: 2, flex: 1 }}>
      {/* Home page content */}
    </Container>
  }/>
  <Route path="/about" element={<About />} />
</Routes>
```



## 5. Step 4: Update Drawer Links to Navigate:

Next, update the **Drawer** to include navigation to both the **Home** and **About** pages using the Link component from **React Router**.

```react
<ListItem button component={Link} to="/">
  <ListItemIcon><HomeIcon /></ListItemIcon>
  <ListItemText primary="Home" />
</ListItem>
<ListItem button component={Link} to="/about">
  <ListItemIcon><InfoIcon /></ListItemIcon>
  <ListItemText primary="About" />
</ListItem>
```



## More Resouses  - Add About Page in App Bar

If you want to add another **About** page link in the **AppBar** (next to the **Contact** button), you can simply add a new button that uses Link from **React Router** to navigate to the **About** page.



**In App.js:** In the **AppBar** (the top navigation bar), add  a new button that navigates to the **About** page:

```react
<Button color="inherit" component={Link} to="/about">About</Button>
```

**The** Link **component** is used in the Button to handle navigation when the user clicks the **About** button.



By following these steps, you’ve successfully added routing and integrated navigation to an **About** page in both the **Drawer** and **AppBar**. Now, your project has basic routing functionality with React Router and Material-UI components!



## The Entire Code for **App.js** With Routing Set Up

```react
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Container, Grid, Card, CardContent, Button, Box,
  Drawer, List, ListItem, ListItemIcon, ListItemText, IconButton, TextField,
  Switch, Snackbar, Alert, Fab, Dialog, DialogTitle, DialogContent, DialogContentText,
  DialogActions, CircularProgress, LinearProgress, Chip, Avatar, Divider
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  Info as InfoIcon,
  Mail as MailIcon,
  Add as AddIcon,
} from '@mui/icons-material';

// About page component
function About() {
  return (
    <Container>
      <Typography variant="h2" component="h1" gutterBottom>
        About Us
      </Typography>
      <Typography variant="h5" component="h2" gutterBottom>
        This is the About page. Here, you can add more information about the project or your team.
      </Typography>
    </Container>
  );
}

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggleDrawer = (open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }
    setDrawerOpen(open);
  };

  const handleDarkModeToggle = () => {
    setDarkMode(!darkMode);
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbarOpen(false);
  };

  const handleDialogOpen = () => {
    setDialogOpen(true);
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  const handleSubmit = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      handleDialogClose();
      setSnackbarOpen(true);
    }, 2000);
  };

  const drawerContent = (
    <Box sx={{ width: 250 }} role="presentation" onClick={toggleDrawer(false)} onKeyDown={toggleDrawer(false)}>
       <List>
        <ListItem button component={Link} to="/">
          <ListItemIcon><HomeIcon /></ListItemIcon>
          <ListItemText primary="Home" />
        </ListItem>
        <ListItem button component={Link} to="/about">
          <ListItemIcon><InfoIcon /></ListItemIcon>
          <ListItemText primary="About" />
        </ListItem>
        <ListItem button>
          <ListItemIcon><MailIcon /></ListItemIcon>
          <ListItemText primary="Contact" />
        </ListItem>
      </List>
      <Divider />
      <List>
        <ListItem>
          <ListItemText primary="Dark Mode" />
          <Switch checked={darkMode} onChange={handleDarkModeToggle} />
        </ListItem>
      </List>
    </Box>
  );

  return (
    
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: darkMode ? 'grey.900' : 'background.default', color: darkMode ? 'common.white' : 'common.black' }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" aria-label="menu" onClick={toggleDrawer(true)}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Enhanced MUI React Page
          </Typography>
             {/* Add About Button in the AppBar */}
             <Button color="inherit" component={Link} to="/about">About</Button>
          <Button color="inherit" onClick={handleDialogOpen}>Contact</Button>
        </Toolbar>
      </AppBar>

      <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer(false)}>
        {drawerContent}
      </Drawer>
      
      <Routes>
      <Route path="/" element={
      <Container component="main" sx={{ mt: 8, mb: 2, flex: 1 }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to COS30049 - COS30049 is Fun
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom>
          This page showcases various Material-UI components.
        </Typography>

        <Grid container spacing={4} sx={{ mt: 4 }}>
          {[1, 2, 3].map((card) => (
            <Grid item key={card} xs={12} sm={6} md={4}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography gutterBottom variant="h5" component="h2">
                    Feature {card}
                  </Typography>
                  <Typography>
                    This card demonstrates MUI's Card component. It's great for displaying content in a clean, organized manner.
                  </Typography>
                  <LinearProgress sx={{ mt: 2 }} variant="determinate" value={card * 33} />
                </CardContent>
                <Box sx={{ p: 2 }}>
                  <Button size="small" variant="contained">Learn More</Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mt: 4 }}>
          <TextField fullWidth label="Subscribe to our newsletter" variant="outlined" />
          <Button variant="contained" sx={{ mt: 2 }}>Subscribe</Button>
        </Box>

        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Chip label="React" color="primary" />
          <Chip label="Material-UI" color="secondary" />
          <Chip label="Web Development" color="success" />
          <Chip
            avatar={<Avatar>JS</Avatar>}
            label="JavaScript"
            variant="outlined"
          />
        </Box>
      </Container>
  }/>
        
    <Route path="/about" element={<About />} />
    </Routes>
      
      <Box component="footer" sx={{ bgcolor: darkMode ? 'grey.800' : 'background.paper', py: 6, mt: 'auto' }}>
        <Container maxWidth="lg">
          <Typography variant="body1">
            Enhanced MUI React Page Footer
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {'Copyright © '}
            {new Date().getFullYear()}
            {'.'}
          </Typography>
        </Container>
      </Box>

      <Fab color="primary" aria-label="add" sx={{ position: 'fixed', bottom: 16, right: 16 }}>
        <AddIcon />
      </Fab>

      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
        <Alert onClose={handleSnackbarClose} severity="success" sx={{ width: '100%' }}>
          {darkMode ? 'Dark mode enabled!' : 'Light mode enabled!'}
        </Alert>
      </Snackbar>

      <Dialog open={dialogOpen} onClose={handleDialogClose}>
        <DialogTitle>Contact Us</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Fill out this form to get in touch with us.
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Your Name"
            type="text"
            fullWidth
            variant="standard"
          />
          <TextField
            margin="dense"
            id="email"
            label="Email Address"
            type="email"
            fullWidth
            variant="standard"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Submit'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default App;
```

