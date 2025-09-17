const express = require("express");
const bodyParser = require("body-parser");
const { google } = require("googleapis");

const app = express();
app.use(bodyParser.json());

const auth = new google.auth.GoogleAuth({
  keyFile: "student-risk-eaa67dbdaf24.json",
  scopes: ["https://www.googleapis.com/auth/spreadsheets"],
});

const spreadsheetId = "1HZz4CC05aKQoAWnA6gShj2D0S7Ztg3KOO9wNUzfOXRg";
const sheetName = "Sheet1";

// Risk calculation
function getRiskAndReason(attendance, marks) {
  let risk = "Green";
  let reason = "Good performance";

  if (attendance < 75) {
    risk = "Red";
    reason = "Low attendance (< 75%)";
  } else if (marks < 40) {
    risk = "Red";
    reason = "Very low marks (< 40)";
  } else if (marks < 60) {
    risk = "Yellow";
    reason = "Moderate marks (40–59)";
  }

  return { risk, reason };

}

app.post("/addStudent", async (req, res) => {
  try {
    const { name, attendance, marks, feeStatus } = req.body;

    const { risk, reason } = getRiskAndReason(attendance, marks);

    const client = await auth.getClient();
    const sheets = google.sheets({ version: "v4", auth: client });

    await sheets.spreadsheets.values.append({
      spreadsheetId,
      range: `${sheetName}!A:F`,
      valueInputOption: "USER_ENTERED",
      requestBody: {
        values: [[name, attendance, marks, feeStatus || "", risk, reason]],
      },
    });

    res.json({ status: "success", name, risk, reason });
  } catch (err) {
    console.error("Error:", err);
    res.status(500).send("Something went wrong");
  }
});

app.listen(3000, () => {
  console.log("✅ Server running on http://localhost:3000");
});
