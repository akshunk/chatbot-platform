import "./globals.css";

export const metadata = {
  title: "Nova - Conversational AI",
  description: "Unfiltered. Direct. Intelligent.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="h-screen overflow-hidden">{children}</body>
    </html>
  );
}
