/**
 * Netlify Function: /api/dashboard
 * Returns aggregated dashboard data (no individual survey records)
 * Requires authentication via Netlify Identity
 */

const fs = require("fs");
const path = require("path");
const { verifyAuth } = require("./shared/auth.js");

const DASHBOARD_DATA_FILE = path.join(
  __dirname,
  "..",
  "cache",
  "dashboard_data.json"
);

exports.handler = async (event) => {
  const auth = verifyAuth(event.headers);
  if (!auth.authenticated) {
    return {
      statusCode: 401,
      body: JSON.stringify({ error: "Unauthorized" }),
      headers: { "Content-Type": "application/json" },
    };
  }

  try {
    if (!fs.existsSync(DASHBOARD_DATA_FILE)) {
      return {
        statusCode: 404,
        body: JSON.stringify({
          error: "Dashboard data not available. Please regenerate.",
        }),
        headers: { "Content-Type": "application/json" },
      };
    }

    const data = fs.readFileSync(DASHBOARD_DATA_FILE, "utf-8");
    const dashboardData = JSON.parse(data);

    return {
      statusCode: 200,
      body: JSON.stringify(dashboardData),
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=3600",
      },
    };
  } catch (error) {
    console.error("Error reading dashboard data:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Internal server error" }),
      headers: { "Content-Type": "application/json" },
    };
  }
};
