# Workshop 11 -  Full-Stack Application with AI Integration

[TOC]

## Objective:

By the end of this workshop, students will:

1. Understand Full-Stack Architecture: Grasp the concept of full-stack development, including the interplay between front-end (React) and back-end (FastAPI) components.
2. Integrate AI Model: Incorporate a simple AI model into the backend and create an endpoint to access it.
3. Integrate Front-end and Back-end: Connect the React front-end with the FastAPI back-end, handling data exchange and managing CORS issues.
4. Implement Data Visualization: Use Chart.js / D3.js to visualize the results from the AI model.
9. Implement Best Practices: Apply coding best practices, including clean code principles, error handling, and basic security measures.



# Part A of Week 11:

## 1. Recapture lecture slides (15 mins)

### Full-stack Integration 
- Architecture Overview
- Communication Flow between React frontend and FastAPI backend
- AI Model Integration
  - Data visualization (D3.js. Chart.js)


### Best Practices in Code Development
- Code Style and Consistency
- Code Comments and Documentation
- Good Code Structure

## 2. Setting up the Development Environment (10 mins)

1. **Install necessary tools if you havn't done so:**

   a. Python 3.7+ with FastAPI and required libraries
   ```bash
   pip install fastapi uvicorn scikit-learn numpy joblib
   ```

   b. Node.js and npm (latest stable version)

   c. Code editor (VS Code recommended)

2. **Create project directory:**

```bash
mkdir cos30049-w11
cd cos30049-w11
mkdir backend frontend
```


## 3. Create FastAPI Backend with AI Model Integration (20 mins)

1. **Set up Python environment and Install FastAPI with dependencies:**

```bash
pip install fastapi uvicorn sklearn numpy joblib
```

2. **Create AI model file:**

Create file `backend/model.py`:

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# A simple regression model
class SimpleModel:
    def __init__(self):
        # Initialize the model (Linear Regression)
        self.model = LinearRegression()

    def train(self):
        # Example training data: X = [[square footage, bedrooms]], y = [price]
        X = np.array([[1500, 3], [1200, 2], [1800, 4], [2000, 5], [1400, 2], [1600, 3]])
        y = np.array([300000, 250000, 400000, 500000, 270000, 320000])
        
        # Train the model
        self.model.fit(X, y)
        
        # Save the model
        joblib.dump(self.model, 'simple_model.pkl')

        # Evaluation
        predictions = self.model.predict(X)
        mse = mean_squared_error(y, predictions)
        r2 = r2_score(y, predictions)

        print(f"Model trained. MSE: {mse}, R²: {r2}")

    def predict(self, square_footage, bedrooms):
        # Load the model
        model = joblib.load('simple_model.pkl')
        
        # Make a prediction based on input
        return model.predict([[square_footage, bedrooms]])

# Example usage (for initial training)
if __name__ == "__main__":
    model = SimpleModel()
    model.train()
```

3. **Create main application file:**

Create file `backend/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model import SimpleModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # URL of React application
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the model
model = SimpleModel()

@app.get("/")
async def root():
    return {"message": "Welcome to the House Price Prediction API"}

@app.get("/predict/{square_footage}/{bedrooms}")
async def predict_price(square_footage: int, bedrooms: int):
    price = model.predict(square_footage, bedrooms)[0]
    return {"predicted_price": round(price, 2)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

4. **Train the model:**

Run the following command to train the model:

```bash
python model.py
```

5. **Run FastAPI server:**

```bash
uvicorn main:app --reload
```

## 4. Create React Frontend (15 mins)

1. **Initialize React application:**

```bash
cd ../frontend
npx create-react-app .
```

2. **Install additional dependencies:**

```bash
npm install axios chart.js react-chartjs-2
npm install @mui/material @emotion/react @emotion/styled
```

3. **Update `frontend/src/App.js`:**

```jsx
import React, { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  Grid,
  Box,
  CircularProgress
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';

// Registering Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [squareFootage, setSquareFootage] = useState('');
  const [bedrooms, setBedrooms] = useState('');
  const [predictedPrice, setPredictedPrice] = useState(null);
  const [error, setError] = useState('');
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setPredictedPrice(null);
    setLoading(true);

    try {
       // Axios call to the backend to predict house price
      const response = await axios.get(`http://localhost:8000/predict/${squareFootage}/${bedrooms}`);
      setPredictedPrice(response.data.predicted_price);
      
      // Prepare data for the chart
      const squareFootages = [1000, 1500, 2000, 2500, 3000];
      const predictions = await Promise.all(
        squareFootages.map(sf => 
          axios.get(`http://localhost:8000/predict/${sf}/${bedrooms}`)
            .then(res => res.data.predicted_price)
        )
      );

       // Creating the chart data using the predictions from the backend
      const newChartData = {
        labels: squareFootages, // X-axis labels (square footage)
        datasets: [
          {
            label: 'Predicted Prices',
            data: predictions,  // Y-axis data (predicted prices)
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            tension: 0.1
          },
          {
            label: 'Your Prediction',
            data: [{x: parseInt(squareFootage), y: response.data.predicted_price}],
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            pointRadius: 8,
            pointHoverRadius: 12,
            showLine: false // Show only the point for the user's prediction
          }
        ]
      };
      setChartData(newChartData);  // Set the chart data in state
    } catch (err) {
      setError('Error predicting price. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            House Price Predictor
          </Typography>
          <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
            <form onSubmit={handleSubmit}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Square Footage"
                    variant="outlined"
                    value={squareFootage}
                    onChange={(e) => setSquareFootage(e.target.value)}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Number of Bedrooms"
                    variant="outlined"
                    value={bedrooms}
                    onChange={(e) => setBedrooms(e.target.value)}
                    required
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button 
                    type="submit" 
                    variant="contained" 
                    color="primary" 
                    fullWidth
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Predict Price'}
                  </Button>
                </Grid>
              </Grid>
            </form>
          </Paper>
          {error && (
            <Typography color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}
          {predictedPrice && (
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                Predicted Price: ${predictedPrice.toLocaleString()}
              </Typography>
              {chartData && (
                <Box sx={{ mt: 3 }}>
                  <Line 
                    data={chartData}
                    options={{
                      responsive: true,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                        title: {
                          display: true,
                          text: 'Price Predictions by Square Footage'
                        }
                      },
                      scales: {
                        x: {
                          type: 'linear',
                          position: 'bottom',
                          title: {
                            display: true,
                            text: 'Square Footage'
                          }
                        },
                        y: {
                          title: {
                            display: true,
                            text: 'Predicted Price ($)'
                          }
                        }
                      }
                    }}
                  />
                </Box>
              )}
            </Paper>
          )}
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
```

**Extract the Axios and Chart.js For Code Explaination**

a. **Axios Call Example:**

Here’s the **Axios** portion extracted as an example of making an HTTP GET request:

```react
const handleSubmit = async (e) => {
  e.preventDefault();
  setError('');
  setPredictedPrice(null);
  setLoading(true);

  try {
    // Axios call to predict house price based on square footage and bedrooms
    const response = await axios.get(`http://localhost:8000/predict/${squareFootage}/${bedrooms}`);
    setPredictedPrice(response.data.predicted_price);
  } catch (err) {
    setError('Error predicting price. Please try again.');
    console.error(err);
  } finally {
    setLoading(false);
  }
};
```

b. **Chart.js Integration Example:**

Here’s the **Chart.js** portion that prepares and displays the chart data:

```react
const newChartData = {
  labels: squareFootages,  // X-axis labels (square footage)
  datasets: [
    {
      label: 'Predicted Prices',
      data: predictions,  // Y-axis data (predicted prices)
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
      tension: 0.1
    },
    {
      label: 'Your Prediction',
      data: [{x: parseInt(squareFootage), y: response.data.predicted_price}],
      borderColor: 'rgb(255, 99, 132)',
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
      pointRadius: 8,
      pointHoverRadius: 12,
      showLine: false  // Show only the point for the user's prediction
    }
  ]
};

// Render Chart using Line component from Chart.js
<Line 
  data={chartData}
  options={{
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Price Predictions by Square Footage'
      }
    },
    scales: {
      x: {
        type: 'linear',
        position: 'bottom',
        title: {
          display: true,
          text: 'Square Footage'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Predicted Price ($)'
        }
      }
    }
  }}
/>
```



4. **Run React application:**

```bash
npm start
```



## 5. Testing and Debugging (20 mins)

- Open a browser and visit http://localhost:3000
- Enter different square footage and bedroom values, and observe the predicted prices and chart
- Use browser developer tools to inspect network requests and responses
- Add print statements in the backend code and observe server logs

------

# Advanced content: you can choose to learn this only if you are aiming for a high mark

## 6. Optimization and Best Practices (10 mins | Extension)

1. **Implement Error Boundaries in React:**

Update `frontend/src/App.js` to include an Error Boundary:

* The ErrorBoundary class component extends React.Component and is responsible for catching JavaScript errors anywhere in its child component tree. It provides fallback UI in case of an error, preventing the entire app from crashing.

```jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.log(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }

    return this.props.children;
  }
}

// Wrap your main App component with ErrorBoundary
export default function App() {
  return (
    <ErrorBoundary>
      {/* Your existing App code */}
    </ErrorBoundary>
  );
}
```

2. **Implement Request Validation in FastAPI:**

Update `backend/main.py` to include input validation:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Define a Pydantic model to validate and parse input data for prediction
class PredictionInput(BaseModel):
    # Field defines constraints for input validation
    square_footage: int = Field(..., gt=0, description="Square footage of the house")
    bedrooms: int = Field(..., ge=1, le=10, description="Number of bedrooms")
  
 # Define a POST endpoint for predicting house prices
@app.post("/predict")
async def predict_price(input: PredictionInput):
    """
    This function handles the prediction based on input data.
    It takes square footage and number of bedrooms as input,
    and returns the predicted price.
    """
    # Call the machine learning model's predict function to get the price
    price = model.predict(input.square_footage, input.bedrooms)[0]
    
    # Return the predicted price in a dictionary (JSON response)
    return {"predicted_price": round(price, 2)}
```

3. **Implement Proper Error Logging:**

Add a logging utility in both frontend and backend:

For backend (`backend/utils.py`):

```python
import logging

def setup_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

logger = setup_logger()
```

Use this logger in your FastAPI app:

```python
from utils import logger

# Define a POST endpoint at "/predict"
@app.post("/predict")
async def predict_price(input: PredictionInput):
    try:
        # Call the model's predict method using the input data
        price = model.predict(input.square_footage, input.bedrooms)[0]
        
        # Log the prediction details (price, square footage, and bedrooms)
        logger.info(f"Prediction made: {price} for {input.square_footage} sq ft, {input.bedrooms} bedrooms")
        
        # Return the predicted price in JSON format, rounding to 2 decimal places
        return {"predicted_price": round(price, 2)}
    
    except Exception as e:
        # Log the error if an exception occurs during prediction
        logger.error(f"Error during prediction: {str(e)}")
        
        # Raise an HTTP 500 Internal Server Error if prediction fails
        raise HTTPException(status_code=500, detail="Internal server error")
```

For frontend, use a custom hook for error logging:

* The useErrorLog hook defines a function that logs errors to the console (or you could extend it to send errors to an external logging service like **Sentry**, **Datadog**, etc.).

```jsx
import { useCallback } from 'react';

const useErrorLog = () => {
  return useCallback((error, info) => {
    console.error("Error occurred:", error, info);
    
    // Example: Send error to an external service like Sentry
    // Sentry.captureException(error);

    // Example: Send error to a custom API
    // axios.post('/api/log', { error: error.toString(), info });
  }, []);
};

// Use in your component
const errorLog = useErrorLog();
// In catch block: errorLog(err, 'Error predicting price');
```

## 7. Further Enhancements (Extension)

1. Add more features to the AI model (e.g., location, year built)
2. Implement a more sophisticated chart showing predictions for various house sizes
3. Add a feature to compare multiple predictions
4. Implement server-side validation for input data
5. Add a loading state while waiting for predictions

Students will now have a more comprehensive full-stack experience, including working with a simple AI model and data visualization.