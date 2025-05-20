"use client";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { Noto_Sans, Noto_Sans_JP } from "next/font/google";
import Script from "next/script";

import { MiroSDKInit } from "@/components/SDKInit";
import { TokenProvider } from "../components/TokenContext";

const notoSans = Noto_Sans({
  variable: "--font-noto-sans",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const notoSansJP = Noto_Sans_JP({
  variable: "--font-noto-sans-jp",
  subsets: ["latin"],
  weight: ["400", "700"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const theme = createTheme({
    palette: { mode: "light" },
    typography: {
      fontFamily: `${notoSans.style.fontFamily}, ${notoSansJP.style.fontFamily}, 'Noto Sans', 'Noto Sans JP', 'sans-serif'`,
    },
  });

  return (
    <html lang="ja">
      <head>
        <meta name="viewport" content="initial-scale=1, width=device-width" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
      </head>
      <body className={`${notoSans.variable} ${notoSansJP.variable}`}>
        <TokenProvider>
          {/* Miro SDK Setup */}
          <Script
            src="https://miro.com/app/static/sdk/v2/miro.js"
            strategy="beforeInteractive"
          />
          <MiroSDKInit />

          {/* Material UI Setup */}
          <ThemeProvider theme={theme}>
            <CssBaseline />
            {children}
          </ThemeProvider>
        </TokenProvider>
      </body>
    </html>
  );
}
