import { onDocumentCreated } from "firebase-functions/v2/firestore";
import * as admin from "firebase-admin";
import * as nodemailer from "nodemailer";
import { defineSecret } from "firebase-functions/params";
import { GoogleGenerativeAI } from "@google/generative-ai";

admin.initializeApp();

// Define secrets for protected credentials
const WORKSPACE_APP_PASSWORD = defineSecret("WORKSPACE_APP_PASSWORD");
const GEMINI_API_KEY = defineSecret("GEMINI_API_KEY");

/**
 * Automatically dispatches a "Welcome to the Tribe" email when a new subscriber
 * is added to the 'ubh_subscribers' collection.
 */
export const triggerWelcomeEmail = onDocumentCreated({
  document: "ubh_subscribers/{subscriberId}",
  secrets: [WORKSPACE_APP_PASSWORD],
}, async (event) => {
  const snapshot = event.data;
  if (!snapshot) {
    console.log("No snapshot data found");
    return;
  }

  const data = snapshot.data();
  const email = data.email;

  if (!email) {
    console.log("No email address found in the document");
    return;
  }

  // Configure the Nodemailer transporter
  // NOTE: Replace 'your-email@gmail.com' with the actual sender address.
  const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
      user: "djwaitaminute@gmail.com", 
      pass: WORKSPACE_APP_PASSWORD.value(),
    },
  });

  const mailOptions = {
    from: '"UBH PRESTIGE" <djwaitaminute@gmail.com>',
    to: email,
    subject: "WELCOME TO THE TRIBE // UBH PRESTIGE",
    html: `
<!DOCTYPE html>
<html>
<head>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;700;900&display=swap');
    body {
      background-color: #0e0e0e;
      margin: 0;
      padding: 0;
      font-family: 'Space Grotesk', sans-serif;
    }
    .container {
      max-width: 600px;
      margin: 40px auto;
      background-color: #0e0e0e;
      border: 1px solid #262626;
      padding: 40px;
      text-align: center;
    }
    .header {
      color: #E0FF00;
      font-size: 40px;
      font-weight: 900;
      letter-spacing: -2px;
      margin-bottom: 10px;
      text-transform: uppercase;
      line-height: 1;
    }
    .subheader {
      font-size: 14px;
      color: #777575;
      letter-spacing: 4px;
      text-transform: uppercase;
      margin-bottom: 40px;
    }
    .status-box {
      background-color: #131313;
      border-left: 4px solid #E0FF00;
      padding: 24px;
      text-align: left;
      margin-bottom: 40px;
    }
    .status-label {
      font-size: 12px;
      font-weight: bold;
      color: #E0FF00;
      letter-spacing: 2px;
      margin-bottom: 8px;
    }
    .status-text {
      font-size: 16px;
      color: #ffffff;
      line-height: 1.5;
      margin: 0;
    }
    .cta-button {
      display: inline-block;
      background-color: #E0FF00;
      color: #000000;
      padding: 18px 36px;
      text-decoration: none;
      font-weight: bold;
      font-size: 14px;
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-top: 20px;
    }
    .footer {
      margin-top: 60px;
      font-size: 10px;
      color: #494847;
      letter-spacing: 2px;
      text-transform: uppercase;
      border-top: 1px solid #262626;
      padding-top: 20px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">WELCOME TO THE TRIBE</div>
    <div class="subheader">DATA_INTERCEPT_SUCCESSFUL</div>
    
    <div class="status-box">
      <div class="status-label">[ENROLLED // ACCESS_GRANTED]</div>
      <p class="status-text">
        You are now part of the elite. Expect secret drops, unreleased demos, and VIP access to underground sessions before they hit the surface.
      </p>
    </div>
    
    <a href="https://ubh-ecosystem-2026.web.app" class="cta-button">RETURN TO THE HUNT</a>
    
    <div class="footer">
      © 2024 UNDERGROUND PRESTIGE // SECURED BY UBH_ENGINE
    </div>
  </div>
</body>
</html>
    `,
  };

  try {
    await transporter.sendMail(mailOptions);
    console.log("Welcome email sent to:", email);
  } catch (error) {
    console.error("Error sending email:", error);
    throw error;
  }
});

/**
 * Triggered when a new lead is created in 'musical_chairs_leads'.
 * Uses Gemini AI to generate an A&R scouting brief and sends it via email.
 */
export const processMusicalChairsLead = onDocumentCreated({
  document: "musical_chairs_leads/{leadId}",
  secrets: [WORKSPACE_APP_PASSWORD, GEMINI_API_KEY],
}, async (event) => {
  const snapshot = event.data;
  if (!snapshot) {
    console.log("No snapshot data found");
    return;
  }

  const data = snapshot.data();
  const artistName = data.artistName;
  const instagramUrl = data.instagramUrl;

  if (!artistName || !instagramUrl) {
    console.log("Missing artistName or instagramUrl in the document");
    return;
  }

  // Initialize Gemini AI
  const genAI = new GoogleGenerativeAI(GEMINI_API_KEY.value());
  const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

  const prompt = `You are the A&R Director for Unicorn Bounty Hunter. A new artist named ${artistName} just applied for the Musical Chairs cipher. Their Instagram is ${instagramUrl}. Draft a highly professional, short, gritty A&R scouting brief for Ali Kazem. Format it as an intelligence report advising Ali on what to look for when reviewing this artist's profile.`;

  try {
    // Generate AI Scouting Brief
    const result = await model.generateContent(prompt);
    const reportText = result.response.text();

    // Configure the Nodemailer transporter
    const transporter = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: "djwaitaminute@gmail.com",
        pass: WORKSPACE_APP_PASSWORD.value(),
      },
    });

    const mailOptions = {
      from: '"UBH SYSTEM" <djwaitaminute@gmail.com>',
      to: "unicornbountyhunters@gmail.com",
      subject: `UBH SYSTEM // New A&R Lead: ${artistName}`,
      text: reportText,
    };

    // Send Email
    await transporter.sendMail(mailOptions);
    console.log("A&R scouting brief sent for:", artistName);

    // Update the Firestore document, changing notified to true
    await snapshot.ref.update({ notified: true });
    console.log("Firestore document updated with notified=true for:", artistName);

  } catch (error) {
    console.error("Error in processMusicalChairsLead:", error);
    throw error;
  }
});
