# Week 9 - MUI React Project Setup + Demo

This guide will walk you through setting up and understanding the React Material-UI demo project, which showcases various MUI components and features within a React application.

[TOC]

## 0. Prerequisites

- Node.js and npm installed on your system
- Basic knowledge of React and JavaScript

## 1. Step 1: Create a new React project

1. Open your terminal or command prompt.
2. Navigate to the directory where you want to create your project.
3. Run the following command to create a new React project:

   ```
   npx create-react-app react-mui-demo
   ```

4. Once the project is created, navigate into the project directory:

   ```
   cd react-mui-demo
   ```

5. Now, run the project by using the following command, what do you observed?

   ```
   npm start
   ```



## 2. Step 2: Install Material-UI

1. In your project directory, run the following command to install MUI and its dependencies:

   ```
   npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
   ```



## 3. Step 3: Replace the content of src/App.js

1. Open the `src/App.js` file in your favorite code editor.

2. .Replace its **entire** content with the following to create a simple MUI-powered page:

   ```react
   import React from 'react';
   import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
   
   function App() {
     return (
       <Box sx={{ flexGrow: 1 }}>
         <AppBar position="static">
           <Toolbar>
             <Typography variant="h6" sx={{ flexGrow: 1 }}>
               My MUI App
             </Typography>
             <Button color="inherit">Contact</Button>
           </Toolbar>
         </AppBar>
       </Box>
     );
   }
   
   export default App;
   ```

3. Save the file and observe the changes in the browser.

   

## 4. Step 4: Add Navigation Drawer

Now let’s add a **Drawer** (sidebar navigation) to the project, please replace the entire code in **App.js**

```react
import React, { useState } from 'react';
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

function App() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  const toggleDrawer = (open) => () => {
    setDrawerOpen(open);
  };

  const drawerContent = (
    <Box sx={{ width: 250 }} role="presentation" onClick={toggleDrawer(false)}>
      <List>
        {['Home', 'About', 'Contact'].map((text, index) => (
          <ListItem button key={text}>
            <ListItemIcon>{index === 0 ? <HomeIcon /> : index === 1 ? <InfoIcon /> : <MailIcon />}</ListItemIcon>
            <ListItemText primary={text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton edge="start" color="inherit" aria-label="menu" onClick={toggleDrawer(true)}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            My MUI App
          </Typography>
          <Button color="inherit">Contact</Button>
        </Toolbar>
      </AppBar>
      <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer(false)}>
        {drawerContent}
      </Drawer>
    </Box>
  );
}

export default App;
```



## 5. Step 5: Implement Dark Mode

Now, Let's add dark mode in our project:

```react
// Add dark mode functionality using the Switch component. Update the state to toggle between light and dark modes.
const [darkMode, setDarkMode] = useState(false);

const handleDarkModeToggle = () => {
  setDarkMode(!darkMode);
};

// Inside the drawerContent(), add this below </list>
<Divider />
<List>
  <ListItem>
    <ListItemText primary="Dark Mode" />
    <Switch checked={darkMode} onChange={handleDarkModeToggle} />
  </ListItem>
</List>

// Apply dark mode background to the main container, chage the <box element> in return
 return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: darkMode ? 'grey.900' : 'background.default', color: darkMode ? 'common.white' : 'common.black' }}>
```



## 6. Step 6: Add Snarkbar for Feedback

Implement a **Snackbar** to provide feedback when dark mode is toggled.

```react
const [snackbarOpen, setSnackbarOpen] = useState(false);

// remember to modify your handleDarkModeToggle()
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

// In the return JSX, add this above the last </Box> tag
<Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
  <Alert onClose={handleSnackbarClose} severity="success" sx={{ width: '100%' }}>
    {darkMode ? 'Dark mode enabled!' : 'Light mode enabled!'}
  </Alert>
</Snackbar>
```



## 7. Step 7: Create a Contact Form with Dialog

Add a **Dialog** to show a contact form when clicking the “Contact” button:

```react
const [dialogOpen, setDialogOpen] = useState(false);
const [loading, setLoading] = useState(false);
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

```

​	Add the **Dialog** component to your return statement:

```react
// Change your <AppBar> entirely in return
<AppBar position="static">
  <Toolbar>
    <IconButton edge="start" color="inherit" aria-label="menu" onClick={toggleDrawer(true)}>
      <MenuIcon />
    </IconButton>
    <Typography variant="h6" sx={{ flexGrow: 1 }}>
      Enhanced MUI React Page
    </Typography>
    <Button color="inherit" onClick={handleDialogOpen}>Contact</Button>
  </Toolbar>
</AppBar>

// In the return JXS, add Dialog below </Snackbar>
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
```



## 8. Step 8: Add other components in your home page

1. Add below container into your return JSX, what changes do you observe?

```react
// In the return JSX, add under </Drawer>
<Container component="main" sx={{ mt: 8, mb: 2, flex: 1 }}>
  <Typography variant="h2" component="h1" gutterBottom>
    Welcome to COS30049 - COS30049 is Fun
  </Typography>
  <Typography variant="h5" component="h2" gutterBottom>
    This page showcases various Material-UI components.
  </Typography>
</Container>
```

2. Update the **entire** Container code , and what changes do you observe?

```react
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
</Container>    

```

3. Let's add more components into your <Container>

```react
// add inside the </Container> for the last components
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
```

10. Let's add a footer for your website down below the <Container>

```react
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
```



## The Entire Code for **App.js** :

```react
import React, { useState } from 'react';
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
        {['Home', 'About', 'Contact'].map((text, index) => (
          <ListItem button key={text}>
            <ListItemIcon>
              {index === 0 ? <HomeIcon /> : index === 1 ? <InfoIcon /> : <MailIcon />}
            </ListItemIcon>
            <ListItemText primary={text} />
          </ListItem>
        ))}
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
          <Button color="inherit" onClick={handleDialogOpen}>Contact</Button>
        </Toolbar>
      </AppBar>

      <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer(false)}>
        {drawerContent}
      </Drawer>

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



## 9. Step 9: Update src/index.js

1. Open the `src/index.js` file in your code editor.

2. Now, Let's use MUI to wrap the application inside the ThemeProvider and applying CssBaseline to ensure consistent styling across browsersReplace the content with the following code:

   * ThemeProvider**,** createTheme, and CssBaseline are all from @mui/material/styles:

   ```javascript
   import React from 'react';
   import ReactDOM from 'react-dom/client';
   import { ThemeProvider, createTheme } from '@mui/material/styles';// Import MUI's ThemeProvider and createTheme for applying a theme
   import CssBaseline from '@mui/material/CssBaseline'; // CssBaseline for consistent baseline styles across browsers
   import App from './App';
   
   const theme = createTheme();
   
   const root = ReactDOM.createRoot(document.getElementById('root'));
   root.render(
     <React.StrictMode>
      {/* Wrap the app in ThemeProvider and pass the theme for consistent styling */}
       <ThemeProvider theme={theme}>
         <CssBaseline />
         <App />
       </ThemeProvider>
     </React.StrictMode>
   );
   ```



## 10. Run the application

1. In your terminal, make sure you're in the project directory.

2. Run the following command to start the development server:

   ```
   npm start
   ```

3. Your default web browser should automatically open and display your new React application with MUI components. If it doesn't, you can manually open a browser and navigate to `http://localhost:3000`.

## 11. File Structure

- `src/App.js`: Main application component
- `src/index.js`: Entry point of the React application

## 12. Code Explanation

### index.js

```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';

const theme = createTheme();

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
```

This file sets up the root of the React application:
- It imports necessary components from React and Material-UI.
- Creates a default theme using `createTheme()`.
- Wraps the `App` component with `ThemeProvider` to provide the Material-UI theme throughout the application.
- Includes `CssBaseline` to normalize styles across different browsers.
- Renders the app within `React.StrictMode` for additional development checks.

### App.js

This file contains the main application logic and UI components. Let's break it down:

1. Imports:
   ```javascript
   import React, { useState } from 'react';
   import { /* MUI components */ } from '@mui/material';
   import { /* MUI icons */ } from '@mui/icons-material';
   ```
   - Imports React and the `useState` hook.
   - Imports various Material-UI components and icons.

2. App Component and State Management:
   ```javascript
   function App() {
     const [drawerOpen, setDrawerOpen] = useState(false);
     const [darkMode, setDarkMode] = useState(false);
     const [snackbarOpen, setSnackbarOpen] = useState(false);
     const [dialogOpen, setDialogOpen] = useState(false);
     const [loading, setLoading] = useState(false);
   
     // ... (event handlers)
   ```
   - Uses `useState` to manage the state of the drawer, dark mode, snackbar, dialog, and loading indicator.

3. Event Handlers:
   - `toggleDrawer`: Controls the opening and closing of the side drawer.
   - `handleDarkModeToggle`: Toggles dark mode and shows a snackbar notification.
   - `handleSnackbarClose`: Closes the snackbar.
   - `handleDialogOpen/Close`: Controls the contact dialog.
   - `handleSubmit`: Simulates form submission with a loading state.

4. Drawer Content:
   ```javascript
   const drawerContent = (
     <Box sx={{ width: 250 }} role="presentation" onClick={toggleDrawer(false)} onKeyDown={toggleDrawer(false)}>
       {/* ... Drawer content ... */}
     </Box>
   );
   ```
   - Defines the content of the side drawer, including navigation items and the dark mode toggle.

5. Main Render Function:
   ```javascript
   return (
     <Box sx={{ /* ... */ }}>
       <AppBar position="static">
         {/* ... AppBar content ... */}
       </AppBar>
   
       <Drawer anchor="left" open={drawerOpen} onClose={toggleDrawer(false)}>
         {drawerContent}
       </Drawer>
   
       <Container component="main" sx={{ /* ... */ }}>
         {/* ... Main content ... */}
       </Container>
   
       <Box component="footer" sx={{ /* ... */ }}>
         {/* ... Footer content ... */}
       </Box>
   
       <Fab color="primary" aria-label="add" sx={{ /* ... */ }}>
         <AddIcon />
       </Fab>
   
       <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
         {/* ... Snackbar content ... */}
       </Snackbar>
   
       <Dialog open={dialogOpen} onClose={handleDialogClose}>
         {/* ... Dialog content ... */}
       </Dialog>
     </Box>
   );
   ```
   - Renders the main application structure, including:
     - An `AppBar` with a menu button and contact button.
     - A side `Drawer` for navigation.
     - The main content area with a welcome message, feature cards, and a newsletter subscription form.
     - A footer with copyright information.
     - A floating action button (`Fab`).
     - A `Snackbar` for notifications.
     - A `Dialog` for the contact form.

## 13. Key Features

1. Responsive Layout: Uses Material-UI's `Grid` system for a responsive design.
2. Dark Mode: Implements a toggle for dark/light mode.
3. Interactive Components: Includes interactive elements like the drawer, dialog, and snackbar.
4. Custom Styling: Uses Material-UI's `sx` prop for custom styling.
5. Form Elements: Demonstrates the use of various form components like `TextField` and `Button`.
6. Progress Indicators: Uses `LinearProgress` and `CircularProgress` to show loading states.

## Troubleshooting

If you encounter any errors related to missing dependencies, try running:

```
npm install
```

This will install all dependencies listed in your `package.json` file.

## Customization

Feel free to modify the React component in `src/App.js` to suit your needs. You can add new MUI components, change the layout, or adjust the styling as required.

## Learn More

- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Material-UI Documentation](https://mui.com/getting-started/usage/)

Enjoy building your React application with Material-UI!