const API_URL = "http://localhost:8000";

export const predictUrl = async (url) => {
  const response = await fetch(`${API_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  });
  
  if (!response.ok) {
    throw new Error('Prediction failed');
  }
  
  return await response.json();
};

export const explainUrl = async (url) => {
  const response = await fetch(`${API_URL}/explain`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  });
  
  if (!response.ok) {
    throw new Error('Explanation failed');
  }
  
  return await response.json();
};

export const analyzeUrl = async (url) => {
  const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url }),
  });
  
  if (!response.ok) {
    throw new Error('Analysis failed');
  }
  
  return await response.json();
};
