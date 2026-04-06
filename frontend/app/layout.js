import { Space_Grotesk, Source_Sans_3 } from "next/font/google";

import "./globals.css";


const displayFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display"
});

const bodyFont = Source_Sans_3({
  subsets: ["latin"],
  variable: "--font-body"
});


export const metadata = {
  title: "CV Copilot",
  description: "Resume tailoring workspace for role-fit analysis and rewrite guidance."
};


export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${displayFont.variable} ${bodyFont.variable}`}>
        {children}
      </body>
    </html>
  );
}
