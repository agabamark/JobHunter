const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export const signUp = async (email: string, jobKeywords: string[], country: string) => {
  const response = await fetch(`${API_BASE}/api/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      job_keywords: jobKeywords,
      country,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to sign up');
  }

  return response.json();
};

export const checkStatus = async (email: string) => {
  const response = await fetch(`${API_BASE}/api/status?email=${encodeURIComponent(email)}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to check status');
  }

  return response.json();
};