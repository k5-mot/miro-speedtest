"use client";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import {
  AppBar,
  Box,
  Button,
  Container,
  Toolbar,
  Stack,
  Typography,
} from "@mui/material";
import { TestStickyNote } from "@/components/TestStickyNote";

export default function Home() {
  const baseUrl = String(process.env.NEXT_PUBLIC_BACKEND_URL);

  const handleClick = async () => {
    // /oauth2/refresh をコールして、/ にリダイレクトするのだ
    try {
      const userInfo = await miro.board.getUserInfo();
      const userId = userInfo.id;
      const url = `${baseUrl}/api/oauth/revoke?user_id=${userId}`;
      await fetch(url, {
        method: "POST",
        credentials: "include",
      });
      window.location.href = "/";
    } catch (error) {
      console.error("リフレッシュリクエストに失敗したのだ: ", error);
    }
  };

  return (
    <Container
      maxWidth="sm"
      sx={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        padding: 0,
        overflow: "auto",
      }}
    >
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar sx={{ justifyContent: "space-between" }}>
          <Box
            component="img"
            src="/miro-speedtest-logo.svg"
            alt="Miro Speedtest Logo"
            sx={{ width: "60%", minWidth: 120 }}
          />
          <Button color="inherit" aria-label="ヘルプ">
            <HelpOutlineIcon />
          </Button>
        </Toolbar>
      </AppBar>

      <TestStickyNote />

      <Stack>
        <Typography variant="body2" gutterBottom>
          不具合があったら、こちらをクリックしてね
        </Typography>
        <Button
          variant="outlined"
          color="primary"
          onClick={handleClick}
          sx={{ my: 2 }}
        >
          認証リセット
        </Button>
      </Stack>
    </Container>
  );
}
