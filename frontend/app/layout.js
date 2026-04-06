import "./globals.css";


export const metadata = {
  title: "CV Copilot",
  description: "Resume tailoring workspace for role-fit analysis and rewrite guidance."
};


export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
