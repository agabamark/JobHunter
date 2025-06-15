import { SpeedInsights } from "@vercel/speed-insights/next"
import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "JobHunter",
  description: "Find your next job opportunity",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <SpeedInsights />
      </body>
    </html>
  )
}