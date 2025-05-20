"use client";
import { useEffect, useState } from "react";
import { useToken } from "@/components/TokenContext";
import CircularProgress from "@mui/material/CircularProgress";
import Box from "@mui/material/Box";

export default function App() {
  const baseUrl = String(process.env.NEXT_PUBLIC_BACKEND_URL);
  const { setCode, setState, setClientId, setTeamId } = useToken();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    const start = Date.now();

    const run = async () => {
      const userInfo = await miro.board.getUserInfo();
      const userId = userInfo.id;
      // /api/oauth2/status をコールして認証状態を確認するのだ
      let isAuthenticated = false;
      try {
        console.log(
          `app/page.tsx ${baseUrl}/api/oauth/status?user_id=${encodeURIComponent(userId)}`,
        );
        const res = await fetch(
          `${baseUrl}/api/oauth/status?user_id=${encodeURIComponent(userId)}`,
          { method: "GET", credentials: "include" },
        );
        if (res.ok) {
          const data = await res.json();
          isAuthenticated = data.status;
          console.log(data);
        }
      } catch (e) {
        // 通信エラー時は未認証扱いにするのだ
        isAuthenticated = false;
      }
      // 3秒は必ず表示するのだ
      timeoutId = setTimeout(
        () => {
          window.location.href = isAuthenticated ? "/home" : "/auth/1-signin";
        },
        Math.max(0, 1000 - (Date.now() - start)),
      );
    };
    run();

    return () => clearTimeout(timeoutId);
  }, [setCode, setState, setClientId, setTeamId]);

  // ロゴの下にぐるぐるを表示するのだ
  return (
    <Box
      sx={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Box
        component="img"
        src="/miro-speedtest-logo.svg"
        alt="Miro Speedtest Logo"
        sx={{ width: 200, mb: 4 }}
      />
      <CircularProgress />
    </Box>
  );
}
