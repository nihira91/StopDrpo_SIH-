const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.post('/api/analyze-student', async (req, res) => {
  const student = req.body;

  try {
    // Forward the student data directly to your FastAPI microservice
    const aiResponse = await fetch('http://localhost:8000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(student),
    });

    if (!aiResponse.ok) {
      throw new Error(`AI service failed with status: ${aiResponse.status}`);
    }

    // Get the prediction from the AI service
    const predictionResult = await aiResponse.json();

    // Send the AI service's response directly back to the frontend
    res.status(200).json(predictionResult);

  } catch (error) {
    console.error('Error during AI analysis:', error);
    res.status(500).json({
      message: 'Internal server error. Failed to get prediction from AI service.',
      error: error.message,
    });
  }
});

// A simple root endpoint to confirm the server is running
app.get('/', (req, res) => {
  res.send('Backend for Student Retention Platform is running!');
});

app.listen(PORT, () => {
  console.log(`Node.js server running on http://localhost:${PORT}`);
});
