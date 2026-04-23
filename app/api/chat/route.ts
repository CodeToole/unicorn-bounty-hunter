import { GoogleGenerativeAI } from "@google/generative-ai";
import { NextResponse } from "next/server";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY as string);

export async function POST(req: Request) {
  try {
    const { prompt } = await req.json();

    const model = genAI.getGenerativeModel({ 
      model: "gemini-1.5-flash",
      systemInstruction: "You are the automated Studio Concierge for Unicorn Bounty Hunter (UBH), an independent label run by Ali Kazem. Your job is to help artists book studio time. Maintain a professional, slightly gritty 'underground prestige' tone. Studio blocks are 4 hours minimum. Remote and in-person mixing available. Never negotiate prices. Always direct them to the booking calendar below if ready."
    });

    const result = await model.generateContent(prompt);
    const response = await result.response;
    
    return NextResponse.json({ message: response.text() });
  } catch (error) {
    console.error(error);
    return NextResponse.json({ error: "Comms link severed. Try again." }, { status: 500 });
  }
}
