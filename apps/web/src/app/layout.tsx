import "./globals.css";

export const metadata = {
  title: "Nova Chat",
  description: "Conversational chatbot platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">{children}</body>
    </html>
  );
}
