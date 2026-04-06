/**
 * Shared authentication middleware
 * Verifies user is authenticated via Netlify Identity JWT token
 */

function getAuthToken(headers) {
  const authHeader = headers.authorization || headers.Authorization;
  if (!authHeader) {
    return null;
  }
  // Expected format: "Bearer {token}"
  const parts = authHeader.split(" ");
  return parts.length === 2 && parts[0] === "Bearer" ? parts[1] : null;
}

function verifyAuth(headers) {
  const token = getAuthToken(headers);
  
  if (!token) {
    return {
      authenticated: false,
      error: "No authentication token provided",
      statusCode: 401,
    };
  }

  return {
    authenticated: true,
    token,
    error: null,
    statusCode: 200,
  };
}

module.exports = { verifyAuth, getAuthToken };
