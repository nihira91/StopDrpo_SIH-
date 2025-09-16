const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const calculateRisk = (student) => {
  let riskScore = 0;
  let reasons = [];

  const attendance = parseFloat(student.attendance);
  const marks = parseFloat(student.marks);

  if (attendance < 75) {
    riskScore += 40;
    reasons.push('Low attendance');
  }

  if (marks < 50) {
    riskScore += 40;
    reasons.push('Academic decline (low marks)');
  }

  if (student.fees_status.toLowerCase() !== 'paid') {
    riskScore += 20;
    reasons.push('Fee delays');
  }

  riskScore = Math.min(riskScore, 100);

  return {
    riskScore: riskScore,
    riskLevel: riskScore >= 80 ? 'red' : riskScore >= 50 ? 'yellow' : 'green',
    reasons: reasons,
  };
};

app.post('/api/analyze-student', (req, res) => {
  const student = req.body;
  if (!student || !student.name || !student.attendance || !student.marks || !student.fees_status) {
    return res.status(400).json({ message: 'Missing required student data.' });
  }

  const risk = calculateRisk(student);

  res.status(200).json({
    message: 'Student risk analyzed successfully.',
    student: {
      name: student.name,
      ...risk,
    },
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});